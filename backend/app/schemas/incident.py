from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.event import SecurityEventResponse


class IncidentBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    attack_category: str = Field(default="Unknown", max_length=64)
    severity: str = Field(default="Medium", pattern="^(Low|Medium|High|Critical)$")
    risk_score: float = Field(default=50.0, ge=0.0, le=100.0)
    risk_level: str = Field(default="Medium", pattern="^(Low|Medium|High|Critical)$")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    status: str = Field(default="Open", pattern="^(Open|Investigating|Resolved|Closed)$")
    source_ip: Optional[str] = None
    target_asset: Optional[str] = None
    event_count: int = Field(default=1, ge=1)
    notes: Optional[str] = None


class IncidentCreate(IncidentBase):
    incident_code: Optional[str] = None


class IncidentStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(Open|Investigating|Resolved|Closed)$")
    notes: Optional[str] = None


class IncidentResponse(IncidentBase):
    id: str
    incident_code: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimelineEventItem(BaseModel):
    id: str
    timestamp: datetime
    delta_seconds: int
    time_offset: str  # e.g. "+0s", "+14s", "+2m 15s"
    event_type: str
    source: str
    severity: str
    source_ip: str
    destination_ip: str
    destination_port: Optional[int] = None
    message: str
    attack_type: str
    user_identity: Optional[str] = None


class IncidentTimelineResponse(BaseModel):
    incident_id: str
    incident_code: str
    title: str
    total_events: int
    duration_seconds: int
    events: List[TimelineEventItem]


class IncidentDetailResponse(IncidentResponse):
    risk_breakdown: Optional[Dict[str, Any]] = None
    events: List[SecurityEventResponse] = []

    model_config = ConfigDict(from_attributes=True)


class IncidentSummary(BaseModel):
    total_incidents: int
    open_incidents: int
    critical_incidents: int
    high_risk_incidents: int
