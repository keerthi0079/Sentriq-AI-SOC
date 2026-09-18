import pytest
from app.core.websocket_hub import MessageType, websocket_hub
from app.models.event import SecurityEvent
from app.services.data_generator import SecurityDataGenerator
from app.services.streamer import background_streamer


@pytest.mark.asyncio
async def test_simulation_status_endpoint(async_client):
    """Verifies that the simulation status endpoint returns valid telemetry."""
    response = await async_client.get("/api/v1/simulation/status")
    assert response.status_code == 200
    data = response.json()
    assert "is_running" in data
    assert "speed" in data
    assert "events_generated" in data
    assert "threats_detected" in data
    assert "queue_size" in data


@pytest.mark.asyncio
async def test_simulation_speed_endpoint(async_client):
    """Verifies updating simulation speed multiplier."""
    response = await async_client.post("/api/v1/simulation/speed", json={"speed": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["speed"] == 5

    # Reset back to 1
    reset_resp = await async_client.post("/api/v1/simulation/speed", json={"speed": 1})
    assert reset_resp.status_code == 200
    assert reset_resp.json()["speed"] == 1


@pytest.mark.asyncio
async def test_simulation_inject_scenario(async_client):
    """Verifies queuing a dedicated scenario burst into the streamer."""
    response = await async_client.post(
        "/api/v1/simulation/inject",
        json={"scenario": "brute_force"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert data["scenario"] == "brute_force"
    assert data["events_queued"] > 0
    assert data["total_queue_size"] > 0


@pytest.mark.asyncio
async def test_simulation_start_and_stop(async_client):
    """Verifies starting and stopping the background streamer via REST endpoints."""
    start_resp = await async_client.post("/api/v1/simulation/start")
    assert start_resp.status_code == 200
    assert start_resp.json()["is_running"] is True

    # Immediately stop so it doesn't run in background during rest of tests
    stop_resp = await async_client.post("/api/v1/simulation/stop")
    assert stop_resp.status_code == 200
    assert stop_resp.json()["is_running"] is False


@pytest.mark.asyncio
async def test_streamer_process_single_event():
    """Verifies executing the full automated pipeline for a single generated event."""
    benign_event = SecurityDataGenerator.generate_benign_event()
    processed_event, incident = await background_streamer.process_event(benign_event)

    assert processed_event.id == benign_event.id
    assert processed_event.attack_type == "Normal"
    # Benign events should not create an incident
    assert incident is None

    # Process attack event with dedicated source IP to prevent collision with live demo incidents
    attack_events = SecurityDataGenerator.generate_brute_force_scenario(fail_count=2)
    attack_event = attack_events[0]
    attack_event.source_ip = "198.51.100.222"
    processed_attack, inc = await background_streamer.process_event(attack_event)

    assert processed_attack.id == attack_event.id
    assert processed_attack.is_attack is True
    # Should be correlated to an incident
    assert inc is not None
    assert inc.attack_category in ["Brute Force", "Exploitation"]


@pytest.mark.asyncio
async def test_websocket_hub_broadcast():
    """Verifies WebSocketHub broadcast handles empty or active connections without errors."""
    assert websocket_hub.connection_count >= 0
    # Broadcasting to empty set should not raise an error
    await websocket_hub.broadcast_typed(
        MessageType.SYSTEM_MESSAGE,
        {"test": "ping"},
    )

