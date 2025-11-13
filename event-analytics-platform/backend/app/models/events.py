from sqlalchemy import Column, String, DateTime, Integer, JSON, Float, Index, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.core.database import Base


class Event(Base):
    """
    Core event model - stores all incoming events
    Optimized for time-series queries with TimescaleDB
    """
    __tablename__ = "events"

    # Primary columns
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String(100), unique=True, index=True, nullable=False)
    type = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    source = Column(String(50), index=True, nullable=False)
    
    # Event data
    properties = Column(JSONB, default={})
    
    # Metadata
    ip = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    user_id = Column(String(100), index=True)  # For user tracking
    session_id = Column(String(100), index=True)  # For session tracking
    
    # Additional tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False, index=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_events_timestamp_type', 'timestamp', 'type'),
        Index('idx_events_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_events_session_timestamp', 'session_id', 'timestamp'),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "event_id": self.event_id,
            "type": self.type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source,
            "properties": self.properties,
            "ip": self.ip,
            "user_agent": self.user_agent,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class EventAggregation(Base):
    """
    Pre-aggregated metrics for fast dashboard queries
    Updated by consumer in real-time
    """
    __tablename__ = "event_aggregations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Time bucket
    time_bucket = Column(DateTime, index=True, nullable=False)
    window_size = Column(Integer, default=60)  # seconds
    
    # Aggregation dimensions
    event_type = Column(String(50), index=True)
    source = Column(String(50), index=True)
    
    # Metrics
    count = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    unique_sessions = Column(Integer, default=0)
    
    # Additional metrics
    avg_processing_time = Column(Float)
    properties_summary = Column(JSONB, default={})
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_agg_time_type', 'time_bucket', 'event_type'),
        Index('idx_agg_time_source', 'time_bucket', 'source'),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "time_bucket": self.time_bucket.isoformat() if self.time_bucket else None,
            "window_size": self.window_size,
            "event_type": self.event_type,
            "source": self.source,
            "count": self.count,
            "unique_users": self.unique_users,
            "unique_sessions": self.unique_sessions,
            "avg_processing_time": self.avg_processing_time,
            "properties_summary": self.properties_summary,
        }


class UserSession(Base):
    """
    Track user sessions for analytics
    Useful for funnel analysis and user journey tracking
    """
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(100), index=True)
    
    # Session timing
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Session data
    source = Column(String(50))
    entry_page = Column(String(500))
    exit_page = Column(String(500))
    
    # Metrics
    event_count = Column(Integer, default=0)
    page_views = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    
    # Device/Browser info
    device_type = Column(String(50))
    browser = Column(String(100))
    os = Column(String(100))
    ip = Column(String(45))
    
    # Additional data
    properties = Column(JSONB, default={})
    
    __table_args__ = (
        Index('idx_session_user_started', 'user_id', 'started_at'),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "session_id": self.session_id,
            "user_id": self.user_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.duration_seconds,
            "source": self.source,
            "entry_page": self.entry_page,
            "exit_page": self.exit_page,
            "event_count": self.event_count,
            "page_views": self.page_views,
            "clicks": self.clicks,
            "conversions": self.conversions,
            "device_type": self.device_type,
            "browser": self.browser,
            "os": self.os,
            "properties": self.properties,
        }