from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SimulationStatusResponse(BaseModel):
    is_running: bool
    speed: int
    events_generated: int
    threats_detected: int
    incidents_triggered: int
    queue_size: int
    active_clients: int
    uptime_seconds: float


class SimulationSpeedRequest(BaseModel):
    speed: int = Field(..., ge=1, le=10, description="Event generation speed multiplier (1 to 10)")


class InjectScenarioRequest(BaseModel):
    scenario: str = Field(..., description="Scenario type: 'brute_force', 'dos', or 'port_scan'")


class InjectScenarioResponse(BaseModel):
    status: str
    scenario: str
    events_queued: int
    total_queue_size: int

