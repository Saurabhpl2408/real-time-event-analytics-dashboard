from pydantic import BaseModel, Field
from typing import Dict, Any, Literal
from datetime import datetime
import uuid

class EventMetadata(BaseModel):
    ip: str = "0.0.0.0"
    user_agent: str = "Unknown"

class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal["page_view", "click", "trade", "purchase", "signup", "custom"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: Literal["web", "api", "mobile", "external"]
    properties: Dict[str, Any] = Field(default_factory=dict)
    metadata: EventMetadata = Field(default_factory=EventMetadata)

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "b7b7c9fa-7321-4e1b-8217-1a9a7f8c43a1",
                "type": "page_view",
                "timestamp": "2025-10-15T18:00:00Z",
                "source": "web",
                "properties": {"page": "/home"},
                "metadata": {"ip": "127.0.0.1", "user_agent": "Mozilla/5.0"}
            }
        }

class AggregatedMetric(BaseModel):
    minute: str
    event_type: str
    count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DashboardUpdate(BaseModel):
    event_type: str
    minute: str
    count: int
    total_events: int
    events_per_type: Dict[str, int]