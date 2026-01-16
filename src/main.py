from fastapi import FastAPI
import logfire

from contextlib import asynccontextmanager
import asyncio
import docker
import json
import nats

from src.config import settings
from src.handlers import handle_execution_request, handle_grading_job

logfire.configure()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        docker.from_env().ping()
        print("Docker daemon connected successfully.")
    except Exception as e:
        print(f"CRITICAL: Cannot connect to Docker: {e}")

    nc = await nats.connect(settings.nats_url)
    print(f"Connected to NATS at {settings.nats_url}")
    
    async def message_handler(msg):
        try:
            data = json.loads(msg.data.decode())
            
            result = await handle_execution_request(data)
            
            if msg.reply:
                await nc.publish(msg.reply, json.dumps(result).encode())
                
        except Exception as e:
            print(f"CRITICAL ERROR processing message: {e}")
            if msg.reply:
                await nc.publish(msg.reply, json.dumps({"error": str(e)}).encode())

    async def grading_job_handler(msg):
        try:
            data = json.loads(msg.data.decode())
            print(f"Received Grading job for attempt {data.get('attempt_id')}")
            
            result = await handle_grading_job(data)
            
            await nc.publish("attempt.graded", json.dumps(result).encode())
            print(f"Published results for attempt {data.get('attempt_id')}")
            
        except Exception as e:
             print(f"Error processing grading job: {e}")

    await nc.subscribe("execution.run", cb=message_handler)
    await nc.subscribe("execution.job", cb=grading_job_handler)
    print("Subscribed to 'execution.run' and 'execution.job'")
    
    yield
    
    await nc.close()

    await nc.close()

app = FastAPI(lifespan=lifespan)
logfire.instrument_fastapi(app)

from prometheus_fastapi_instrumentator import Instrumentator
# Prometheus metrics
Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health():
    return {"status": "healthy"}