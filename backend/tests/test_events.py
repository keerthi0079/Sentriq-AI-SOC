import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_events_stats_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/events/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data
    assert "threat_events" in data
    assert "benign_events" in data
    assert "attack_distribution" in data
    assert "severity_distribution" in data
    assert data["total_events"] >= 45


@pytest.mark.asyncio
async def test_events_list_and_filtering(async_client: AsyncClient):
    # 1. Test basic listing with pagination
    res = await async_client.get("/api/v1/events?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) <= 10
    assert data["total"] >= 45

    # 2. Test filter by attack_type
    res_attack = await async_client.get("/api/v1/events?attack_type=Brute Force")
    assert res_attack.status_code == 200
    attack_data = res_attack.json()
    for ev in attack_data["items"]:
        assert ev["attack_type"] == "Brute Force"

    # 3. Test filter by severity
    res_sev = await async_client.get("/api/v1/events?severity=Critical")
    assert res_sev.status_code == 200
    sev_data = res_sev.json()
    for ev in sev_data["items"]:
        assert ev["severity"] == "Critical"

    # 4. Test text search
    res_search = await async_client.get("/api/v1/events?search=198.51.100.45")
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert search_data["total"] >= 1


@pytest.mark.asyncio
async def test_simulate_scenario_endpoint(async_client: AsyncClient):
    payload = {"scenario": "port_scan", "count": 10}
    res = await async_client.post("/api/v1/events/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["scenario"] == "port_scan"
    assert data["generated_events_count"] == 10
    assert len(data["events"]) == 10
    for ev in data["events"]:
        assert ev["is_simulated"] is True
        assert ev["attack_type"] == "Port Scan"

