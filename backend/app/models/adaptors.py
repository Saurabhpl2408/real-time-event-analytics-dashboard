from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import secrets

from app.core.database import Base


class Adaptor(Base):
    """Adaptor configuration model"""
    __tablename__ = "adaptors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    container_id = Column(String(50), unique=True, nullable=False, index=True)
    
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Associated schema
    schema_id = Column(String(100), nullable=False)
    
    # Website info
    website_url = Column(String(500), nullable=False)
    allowed_domains = Column(JSON, default=[])
    
    # Tracking configuration
    tracking_rules = Column(JSON, default={})
    # Example: {"auto_page_view": true, "track_clicks": true}
    
    # Custom adaptor code (JavaScript)
    custom_code = Column(Text)
    
    # Status
    active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Stats
    total_events = Column(JSON, default={"count": 0})
    
    def generate_container_id(self):
        """Generate unique container ID"""
        return f"CAP-{secrets.token_hex(8).upper()}"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "container_id": self.container_id,
            "name": self.name,
            "description": self.description,
            "schema_id": self.schema_id,
            "website_url": self.website_url,
            "allowed_domains": self.allowed_domains,
            "tracking_rules": self.tracking_rules,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "total_events": self.total_events
        }