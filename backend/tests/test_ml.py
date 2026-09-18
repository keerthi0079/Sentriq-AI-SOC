import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_model_info_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/ml/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["algorithm"] == "RandomForestClassifier"
    assert "Brute Force" in data["supported_classes"]
    assert "DoS" in data["supported_classes"]
    assert "Normal" in data["supported_classes"]
    assert data["metrics_summary"]["binary_accuracy"] >= 0.90


@pytest.mark.asyncio
async def test_evaluation_report_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/ml/evaluation-report")
    assert response.status_code == 200
    data = response.json()
    assert "binary_classification" in data
    assert "multiclass_classification" in data
    assert "confusion_matrix" in data["binary_classification"]


@pytest.mark.asyncio
async def test_predict_dos_traffic(async_client: AsyncClient):
    # Volumetric DoS payload
    payload = {
        "features": {
            "rate": 250000.0,
            "spkts": 15000,
            "dpkts": 0,
            "sbytes": 900000,
            "dbytes": 0,
            "dur": 0.05,
            "destination_port": 443,
            "proto": "TCP",
            "service": "http",
            "source": "perimeter_firewall",
        }
    }
    response = await async_client.post("/api/v1/ml/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_threat"] is True
    assert data["verdict"] == "MALICIOUS"
    assert data["predicted_attack_category"] in ["DoS", "Exploitation"]
    assert len(data["detection_reasons"]) > 0


@pytest.mark.asyncio
async def test_predict_benign_traffic(async_client: AsyncClient):
    # Benign web traffic payload
    payload = {
        "features": {
            "rate": 80.0,
            "spkts": 8,
            "dpkts": 10,
            "sbytes": 540,
            "dbytes": 1200,
            "dur": 0.12,
            "destination_port": 443,
            "proto": "TCP",
            "service": "http",
            "source": "web_server",
        }
    }
    response = await async_client.post("/api/v1/ml/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_threat"] is False
    assert data["verdict"] == "BENIGN"
    assert data["predicted_attack_category"] == "Normal"


@pytest.mark.asyncio
async def test_analyze_event_by_id(async_client: AsyncClient):
    # 1. Fetch an existing event
    events_res = await async_client.get("/api/v1/events?page=1&page_size=1")
    assert events_res.status_code == 200
    events = events_res.json()["items"]
    assert len(events) > 0
    event_id = events[0]["id"]

    # 2. Run analysis by ID
    analysis_res = await async_client.post(f"/api/v1/ml/analyze-event/{event_id}")
    assert analysis_res.status_code == 200
    data = analysis_res.json()
    assert "verdict" in data
    assert "confidence" in data
    assert "class_probabilities" in data
    assert "detection_reasons" in data

