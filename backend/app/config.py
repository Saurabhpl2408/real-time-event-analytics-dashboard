import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    app_name: str = "Custom Analytics Platform"
    app_version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Server
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://analytics:analytics123@postgres:5432/analytics_db"
    )
    
    # Kafka
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    kafka_topic_events: str = "analytics.events"
    
    # CORS
    cors_origins: list = ["*"]  # In production, specify actual domains
    
    # Tag Manager
    tag_manager_base_url: str = os.getenv("TAG_MANAGER_BASE_URL", "http://localhost:8000")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()