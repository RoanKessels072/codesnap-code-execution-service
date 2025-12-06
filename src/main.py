from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import docker
import json

from src.config import settings
from src.executor import execute_code_job
import nats

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        d_client = docker.from_env()
        d_client.ping()
        print("Docker daemon connected successfully.")
    except Exception as e:
        print(f"CRITICAL: Cannot connect to Docker: {e}")

    nc = await nats.connect(settings.nats_url)
    print(f"Connected to NATS at {settings.nats_url}")
    
    async def message_handler(msg):
        try:
            data = json.loads(msg.data.decode())
            result = await asyncio.to_thread(execute_code_job, data)
            
            if msg.reply:
                await nc.publish(msg.reply, json.dumps(result).encode())
        except Exception as e:
            if msg.reply:
                await nc.publish(msg.reply, json.dumps({"error": str(e)}).encode())

    await nc.subscribe("execution.run", cb=message_handler)
    print("Subscribed to 'execution.run'")
    
    yield
    
    await nc.close()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "healthy"}