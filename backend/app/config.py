import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings - simplified for production"""
    
    app_name: str = "Custom Analytics Platform"
    app_version: str = "1.0.0"
    environment: str = "development"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    database_url: str = "postgresql+asyncpg://analytics:analytics123@localhost:5432/analytics_db"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_events: str = "analytics.events"
    kafka_enabled: bool = False
    tag_manager_base_url: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"


settings = Settings()

# Handle CORS separately (avoid Pydantic parsing issues)
CORS_ORIGINS_STR = os.getenv("CORS_ORIGINS", "*")
if CORS_ORIGINS_STR == "*":
    CORS_ORIGINS = ["*"]
else:
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_STR.split(",") if origin.strip()]