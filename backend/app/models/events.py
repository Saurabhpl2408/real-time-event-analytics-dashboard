from sqlalchemy import Column, String, DateTime, JSON, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.core.database import Base


class EventLog(Base):
    """
    Master event log - stores all events across all schemas
    This is for quick lookups and statistics
    Schema-specific tables store detailed data
    """
    __tablename__ = "event_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event identification
    event_id = Column(String(100), unique=True, index=True, nullable=False)
    schema_id = Column(String(100), index=True, nullable=False)
    event_type = Column(String(100), index=True, nullable=False)
    
    # User tracking
    user_id = Column(String(100), index=True)
    session_id = Column(String(100), index=True)
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Data (stored as JSONB for fast queries)
    properties = Column(JSONB, default={})
    event_metadata = Column(JSONB, default={})  # CHANGED: metadata -> event_metadata
    
    # Container info
    container_id = Column(String(50), index=True)
    
    # Status
    processed = Column(Integer, default=0)  # 0=pending, 1=processed, -1=failed
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "event_id": self.event_id,
            "schema_id": self.schema_id,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "properties": self.properties,
            "metadata": self.event_metadata,  # Return as 'metadata' for API compatibility
            "container_id": self.container_id,
            "processed": self.processed
        }