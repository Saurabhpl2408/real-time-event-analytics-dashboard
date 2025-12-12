import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "Custom Analytics Platform"
    app_version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Server (Render uses PORT env variable)
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("PORT", os.getenv("BACKEND_PORT", "8000")))
    
    # Database (Render provides DATABASE_URL)
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://analytics:analytics123@localhost:5432/analytics_db"
    )
    
    # Kafka (disabled in production for now)
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic_events: str = "analytics.events"
    kafka_enabled: bool = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
    
    # CORS - FIXED
    cors_origins: List[str] = ["*"]  # Default to allow all
    
    # Tag Manager
    tag_manager_base_url: str = os.getenv("TAG_MANAGER_BASE_URL", "http://localhost:8000")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS_ORIGINS from environment
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env and cors_env != "*":
            self.cors_origins = [origin.strip() for origin in cors_env.split(",")]
        elif cors_env == "*":
            self.cors_origins = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()