"""Unit and integration tests for health and readiness endpoints."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Confirm basic liveness probe works on both root and /api/v1."""
    res_root = client.get("/health")
    assert res_root.status_code == 200
    data_root = res_root.json()
    assert data_root["status"] == "ok"
    assert "version" in data_root

    res_v1 = client.get("/api/v1/health")
    assert res_v1.status_code == 200
    assert res_v1.json()["status"] == "ok"


def test_readiness_check(client: TestClient):
    """Confirm readiness probe checks database and ML classifier status."""
    res = client.get("/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["ready", "degraded"]
    assert data["database"] == "ok"
    assert data["model_loaded"] is True
