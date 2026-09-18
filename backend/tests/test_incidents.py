import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_incidents_crud(async_client: AsyncClient):
    # 1. Test create incident
    new_incident = {
        "title": "Test Brute Force Detection",
        "description": "Integration test created incident",
        "attack_category": "Brute Force",
        "severity": "High",
        "risk_score": 75.0,
        "risk_level": "High",
        "confidence": 0.92,
        "status": "Open",
        "source_ip": "198.51.100.99",
        "target_asset": "test-workstation",
        "event_count": 3,
    }

    create_res = await async_client.post("/api/v1/incidents", json=new_incident)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["title"] == new_incident["title"]
    assert "id" in created_data
    assert "incident_code" in created_data
    inc_id = created_data["id"]

    # 2. Test get incident by ID
    get_res = await async_client.get(f"/api/v1/incidents/{inc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == inc_id

    # 3. Test update status
    update_res = await async_client.patch(
        f"/api/v1/incidents/{inc_id}/status",
        json={"status": "Investigating", "notes": "Analyst assigned"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "Investigating"

    # 4. Test summary
    summary_res = await async_client.get("/api/v1/incidents/summary")
    assert summary_res.status_code == 200
    summary_data = summary_res.json()
    assert summary_data["total_incidents"] >= 1

