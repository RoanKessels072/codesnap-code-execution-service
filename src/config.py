from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8004 

    nats_url: str = "nats://nats:4222"
    service_name: str = "code-execution-service"
    logfire_token: str | None = None
    logfire_service_name: str | None = None
    
    python_image: str = "codesnap-python-runner"
    node_image: str = "codesnap-node-runner"
    
    execution_timeout: int = 5
    max_memory: str = "128m"
    
    class Config:
        env_file = ".env"

settings = Settings()