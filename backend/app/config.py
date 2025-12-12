import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    app_name: str = "Custom Analytics Platform"
    app_version: str = "1.0.0"
    environment: str = "development"
    
    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # Database
    database_url: str = "postgresql+asyncpg://analytics:analytics123@localhost:5432/analytics_db"
    
    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_events: str = "analytics.events"
    kafka_enabled: bool = False
    
    # CORS - Simple string that we'll parse
    cors_origins_str: str = "*"
    
    # Tag Manager
    tag_manager_base_url: str = "http://localhost:8000"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from string"""
        if self.cors_origins_str == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Map environment variables
        fields = {
            'cors_origins_str': {
                'env': ['CORS_ORIGINS', 'cors_origins_str']
            }
        }


settings = Settings()