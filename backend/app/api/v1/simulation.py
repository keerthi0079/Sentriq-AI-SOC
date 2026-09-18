import logging
from fastapi import APIRouter, HTTPException
from app.schemas.simulation import (
    InjectScenarioRequest,
    InjectScenarioResponse,
    SimulationSpeedRequest,
    SimulationStatusResponse,
)
from app.services.streamer import background_streamer

logger = logging.getLogger("sentriq.api.simulation")

router = APIRouter(prefix="/simulation", tags=["Telemetry Stream Simulation"])


@router.get("/status", response_model=SimulationStatusResponse)
async def get_simulation_status():
    """Returns the current state and telemetry metrics of the background event streamer."""
    return background_streamer.get_status()


@router.post("/start", response_model=SimulationStatusResponse)
async def start_simulation():
    """Starts the background event streaming loop."""
    status = await background_streamer.start()
    return status


@router.post("/stop", response_model=SimulationStatusResponse)
async def stop_simulation():
    """Stops the background event streaming loop."""
    status = await background_streamer.stop()
    return status


@router.post("/speed", response_model=SimulationStatusResponse)
async def set_simulation_speed(payload: SimulationSpeedRequest):
    """Sets the event generation speed multiplier (1x, 2x, 5x)."""
    status = await background_streamer.set_speed(payload.speed)
    return status


@router.post("/inject", response_model=InjectScenarioResponse)
async def inject_simulation_scenario(payload: InjectScenarioRequest):
    """
    Enqueues an immediate dedicated attack scenario into the stream queue
    (e.g., 'brute_force', 'dos', 'port_scan').
    """
    result = await background_streamer.inject_scenario(payload.scenario)
    return result

