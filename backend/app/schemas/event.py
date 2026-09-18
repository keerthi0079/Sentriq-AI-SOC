from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SecurityEventBase(BaseModel):
    timestamp: Optional[datetime] = None
    source: str = Field(default="auth_service", max_length=64)
    event_type: str = Field(default="login_attempt", max_length=64)
    source_ip: str = Field(default="127.0.0.1", max_length=64)
    destination_ip: str = Field(default="10.0.0.1", max_length=64)
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: str = Field(default="TCP", max_length=16)
    user_identity: Optional[str] = None
    attack_type: str = Field(default="Normal", max_length=64)
    severity: str = Field(default="Low", pattern="^(Low|Medium|High|Critical)$")
    message: str
    raw_features: Optional[Dict[str, Any]] = None
    is_attack: bool = False
    is_simulated: bool = True
    incident_id: Optional[str] = None


class SecurityEventCreate(SecurityEventBase):
    pass


class SecurityEventResponse(SecurityEventBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventStatsResponse(BaseModel):
    total_events: int
    threat_events: int
    benign_events: int
    attack_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]
    source_distribution: Dict[str, int]


class SimulateScenarioRequest(BaseModel):
    scenario: str = Field(
        default="brute_force",
        description="Scenario type: 'brute_force', 'dos', 'port_scan', 'benign'",
    )
    count: int = Field(default=5, ge=1, le=50)


class SimulateScenarioResponse(BaseModel):
    scenario: str
    generated_events_count: int
    message: str
    events: List[SecurityEventResponse]


class DatasetSummaryResponse(BaseModel):
    source: str
    display_name: str
    record_count: int
    threat_count: int
    benign_count: int
    is_simulated: bool
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class DatasetUpdateRequest(BaseModel):
    new_source_name: str = Field(min_length=1, max_length=64)


class SecurityEventUpdate(BaseModel):
    attack_type: Optional[str] = None
    severity: Optional[str] = Field(default=None, pattern="^(Low|Medium|High|Critical)$")
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: Optional[str] = None
    user_identity: Optional[str] = None
    message: Optional[str] = None
    is_attack: Optional[bool] = None

