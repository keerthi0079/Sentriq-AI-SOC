import pytest
from app.core.database import AsyncSessionLocal
from app.ml.explainer import xai_explainer_service
from app.models.event import SecurityEvent
from app.services.data_generator import SecurityDataGenerator


@pytest.mark.asyncio
async def test_xai_explainer_service_direct():
    """Verifies that XAIExplainerService computes SHAP values and narrative correctly."""
    # Benign test features
    benign_features = {
        "source": "web_server",
        "event_type": "web_request",
        "protocol": "HTTP",
        "destination_port": 443,
        "raw_features": {
            "dur": 0.05,
            "rate": 150.0,
            "spkts": 5,
            "dpkts": 6,
            "sbytes": 350,
            "dbytes": 1200,
        },
    }

    res = xai_explainer_service.explain(benign_features)
    assert res is not None
    assert res.attack_probability <= 0.5
    assert len(res.negative_contributors) > 0
    assert len(res.all_features) > 0
    assert "narrative" in res.model_dump()
    assert res.inference_latency_ms > 0

    # Attack test features (Brute Force)
    attack_features = {
        "source": "auth_service",
        "event_type": "failed_login",
        "protocol": "TCP",
        "destination_port": 22,
        "raw_features": {
            "dur": 2.5,
            "rate": 35.0,
            "spkts": 25,
            "dpkts": 20,
            "sbytes": 3000,
            "dbytes": 4500,
            "ct_dst_sport_ltm": 8,
            "ct_src_dport_ltm": 8,
        },
    }

    attack_res = xai_explainer_service.explain(attack_features)
    assert attack_res is not None
    assert attack_res.attack_probability >= 0.5
    assert len(attack_res.positive_contributors) > 0
    assert attack_res.rule_agreement in (True, False)
    assert "Attack classification was primarily driven by" in attack_res.narrative


@pytest.mark.asyncio
async def test_api_explain_post_endpoint(async_client):
    """Verifies the POST /api/v1/ml/explain endpoint with custom feature dictionary."""
    payload = {
        "features": {
            "source": "firewall",
            "event_type": "port_probe",
            "protocol": "TCP",
            "destination_port": 23,
            "raw_features": {
                "dur": 0.1,
                "rate": 800.0,
                "ct_dst_sport_ltm": 12,
                "ct_src_dport_ltm": 12,
            },
        }
    }

    response = await async_client.post("/api/v1/ml/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "attack_probability" in data
    assert "positive_contributors" in data
    assert "negative_contributors" in data
    assert "narrative" in data
    assert "rule_agreement" in data


@pytest.mark.asyncio
async def test_api_explain_by_event_id_endpoint(async_client):
    """Verifies the GET /api/v1/ml/explain/{event_id} endpoint against a database event."""
    # Seed a single event into database
    test_event = SecurityDataGenerator.generate_benign_event()
    async with AsyncSessionLocal() as session:
        session.add(test_event)
        await session.commit()
        await session.refresh(test_event)

    response = await async_client.get(f"/api/v1/ml/explain/{test_event.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == test_event.id
    assert "positive_contributors" in data
    assert "negative_contributors" in data

    # Verify cached retrieval
    cached_response = await async_client.get(f"/api/v1/ml/explain/{test_event.id}")
    assert cached_response.status_code == 200
    assert cached_response.json()["event_id"] == test_event.id

