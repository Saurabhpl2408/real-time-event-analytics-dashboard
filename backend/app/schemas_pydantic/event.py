from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class EventIngest(BaseModel):
    """Event ingestion request"""
    schema_id: str = Field(..., description="Schema name")
    event_type: str = Field(..., description="Event type (must match schema)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Event properties")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class EventResponse(BaseModel):
    """Event ingestion response"""
    status: str
    event_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EventStatsResponse(BaseModel):
    """Event statistics response"""
    total_events: int
    events_by_schema: Dict[str, int]
    events_by_type: Dict[str, int]
    recent_events: int