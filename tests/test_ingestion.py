"""Unit and integration tests for feedback ingestion and idempotency."""

from fastapi.testclient import TestClient
from app.models.store import Store


def test_single_feedback_ingestion_success(client: TestClient, test_stores: list[Store]):
    """Test successful single feedback ingestion and response structure."""
    store = test_stores[0]
    payload = {
        "store_id": store.id,
        "text": "Produce section had fresh organic strawberries on display today.",
        "source": "customer",
        "idempotency_key": "idemp-001",
    }
    res = client.post("/api/v1/feedback", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["store_id"] == store.id
    assert data["processing_status"] == "PROCESSED"
    assert data["incident_id"] is not None


def test_idempotency_duplicate_submission(client: TestClient, test_stores: list[Store]):
    """Ensure client retry with same idempotency key does not create duplicate record."""
    store = test_stores[0]
    payload = {
        "store_id": store.id,
        "text": "Out of 2% milk in the dairy aisle.",
        "idempotency_key": "idemp-retry-test-123",
    }
    # Initial submission
    res1 = client.post("/api/v1/feedback", json=payload)
    assert res1.status_code == 201
    fb_id_1 = res1.json()["id"]

    # Retried submission with identical key
    res2 = client.post("/api/v1/feedback", json=payload)
    assert res2.status_code == 201
    fb_id_2 = res2.json()["id"]

    # Must be the exact same feedback record
    assert fb_id_1 == fb_id_2


def test_ingestion_invalid_store(client: TestClient):
    """Ensure submission with nonexistent store returns 404."""
    payload = {
        "store_id": "nonexistent-store-id-9999",
        "text": "Valid text but invalid store reference.",
    }
    res = client.post("/api/v1/feedback", json=payload)
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "ENTITY_NOT_FOUND"


def test_batch_ingestion_partial_failures(client: TestClient, test_stores: list[Store]):
    """
    Test batch ingestion handles mix of valid and invalid items without
    rolling back valid items.
    """
    store = test_stores[0]
    batch_payload = {
        "items": [
            {"store_id": store.id, "text": "Valid item one regarding long lines at cashier.", "idempotency_key": "b-1"},
            {"store_id": "invalid-store-id", "text": "Item two with non-existent store.", "idempotency_key": "b-2"},
            {"store_id": store.id, "text": "Valid item three regarding clean restrooms.", "idempotency_key": "b-3"},
        ]
    }
    res = client.post("/api/v1/feedback/batch", json=batch_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_received"] == 3
    assert data["successful_count"] == 2
    assert data["failed_count"] == 1
    assert data["results"][0]["status"] == "SUCCESS"
    assert data["results"][1]["status"] == "ERROR"
    assert data["results"][2]["status"] == "SUCCESS"
