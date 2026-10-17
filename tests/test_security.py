"""Unit and integration tests for security, RBAC, store isolation, and request limits."""

from fastapi.testclient import TestClient
from app.models.store import Store


def test_unauthenticated_request_rejected(client: TestClient):
    """Ensure sensitive endpoints reject calls missing Bearer tokens."""
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "AUTHENTICATION_FAILED"


def test_tampered_token_rejected(client: TestClient):
    """Ensure forged or tampered JWT is rejected."""
    tampered_headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"}
    res = client.get("/api/v1/auth/me", headers=tampered_headers)
    assert res.status_code == 401


def test_store_manager_cannot_modify_unassigned_store(
    client: TestClient,
    test_stores: list[Store],
    store_manager_headers: dict,
):
    """Ensure store manager cannot access or modify incidents belonging to another store."""
    # STORE-102 is not the assigned store for this store manager
    store2_id = test_stores[1].id
    res = client.get(f"/api/v1/stores/{store2_id}", headers=store_manager_headers)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "PERMISSION_DENIED"


def test_request_size_limit_middleware(client: TestClient):
    """Ensure oversized request bodies are rejected with 413 Payload Too Large."""
    # Large content-length header exceeding 2MB
    oversized_headers = {"Content-Length": str(5 * 1024 * 1024)}
    res = client.post(
        "/api/v1/feedback",
        headers=oversized_headers,
        json={"store_id": "any", "text": "test"},
    )
    assert res.status_code == 413
    assert res.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"
