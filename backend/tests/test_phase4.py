import pytest
from httpx import AsyncClient
from app.services.risk_engine import RiskEngine


def test_risk_engine_calculation():
    """Validates the 4-factor deterministic risk calculation and weights."""
    result = RiskEngine.calculate_risk(
        severity="Critical",
        confidence=0.96,
        attack_category="Exploitation",
        asset_identifier="domain-controller",
    )

    # Calculation:
    # Sev: 100 * 0.3 = 30.0
    # Conf: 96 * 0.3 = 28.8
    # Asset: 95 * 0.2 = 19.0
    # Impact: 95 * 0.2 = 19.0
    # Total = 96.8
    assert result["risk_score"] == 96.8
    assert result["risk_level"] == "Critical"
    assert "Critical" in result["explanation"]
    assert result["factors"]["severity"]["contribution"] == 30.0
    assert result["factors"]["confidence"]["contribution"] == 28.8
    assert result["factors"]["asset_importance"]["contribution"] == 19.0
    assert result["factors"]["attack_impact"]["contribution"] == 19.0


def test_risk_engine_low_severity():
    result = RiskEngine.calculate_risk(
        severity="Low",
        confidence=0.70,
        attack_category="Port Scan",
        asset_identifier="guest-wifi",
    )
    # Sev: 20 * 0.3 = 6.0
    # Conf: 70 * 0.3 = 21.0
    # Asset: 20 * 0.2 = 4.0
    # Impact: 40 * 0.2 = 8.0
    # Total = 39.0 -> Medium
    assert result["risk_score"] == 39.0
    assert result["risk_level"] == "Medium"


@pytest.mark.asyncio
async def test_correlate_unassigned_and_timeline(async_client: AsyncClient):
    # 1. Trigger correlation across unassigned events
    corr_res = await async_client.post("/api/v1/incidents/correlate")
    assert corr_res.status_code == 200
    corr_data = corr_res.json()
    assert corr_data["status"] == "success"

    # 2. Get list of incidents and pick one with correlated events
    inc_res = await async_client.get("/api/v1/incidents?page=1&page_size=30")
    assert inc_res.status_code == 200
    inc_list = [inc for inc in inc_res.json()["items"] if inc["event_count"] > 1]
    assert len(inc_list) > 0
    inc_id = inc_list[0]["id"]

    # 3. Test detailed incident with 4-factor risk breakdown (INC-2026-0001 has 5 seeded events)
    detail_res = await async_client.get("/api/v1/incidents/INC-2026-0001/detail")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert "risk_breakdown" in detail_data
    assert "factors" in detail_data["risk_breakdown"]
    assert "explanation" in detail_data["risk_breakdown"]
    assert len(detail_data["events"]) >= 1

    # 4. Test incident timeline endpoint
    timeline_res = await async_client.get("/api/v1/incidents/INC-2026-0001/timeline")
    assert timeline_res.status_code == 200
    timeline_data = timeline_res.json()
    assert timeline_data["incident_code"] == "INC-2026-0001"
    assert "events" in timeline_data
    assert len(timeline_data["events"]) >= 1
    first_ev = timeline_data["events"][0]
    assert "time_offset" in first_ev
    assert first_ev["time_offset"] == "+0s"
