"""Unit and integration tests for store directory and exposure management."""

from fastapi.testclient import TestClient
from app.models.store import Store


def test_create_store_admin(client: TestClient, admin_headers: dict, analyst_headers: dict):
    """Test store creation authorization and persistence."""
    payload = {
        "store_number": "STORE-999",
        "name": "New Flagship Store",
        "city": "Denver",
        "state": "CO",
        "size_sqft": 40000.0,
        "avg_daily_transactions": 4500.0,
    }

    # Forbidden for analyst
    res_deny = client.post("/api/v1/stores", json=payload, headers=analyst_headers)
    assert res_deny.status_code == 403

    # Allowed for admin
    res_ok = client.post("/api/v1/stores", json=payload, headers=admin_headers)
    assert res_ok.status_code == 201
    data = res_ok.json()
    assert data["store_number"] == "STORE-999"
    assert data["avg_daily_transactions"] == 4500.0


def test_list_stores_isolation(
    client: TestClient,
    test_stores: list[Store],
    admin_headers: dict,
    store_manager_headers: dict,
):
    """Test store listing isolation: manager only sees assigned store."""
    # Admin sees all stores
    res_admin = client.get("/api/v1/stores", headers=admin_headers)
    assert res_admin.status_code == 200
    assert res_admin.json()["total"] >= 2

    # Manager only sees STORE-101
    res_mgr = client.get("/api/v1/stores", headers=store_manager_headers)
    assert res_mgr.status_code == 200
    data_mgr = res_mgr.json()
    assert data_mgr["total"] == 1
    assert data_mgr["items"][0]["store_number"] == "STORE-101"


def test_store_manager_cross_store_access_denied(
    client: TestClient,
    test_stores: list[Store],
    store_manager_headers: dict,
):
    """Ensure store manager cannot retrieve another store's record."""
    store2_id = test_stores[1].id  # STORE-102
    res = client.get(f"/api/v1/stores/{store2_id}", headers=store_manager_headers)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "PERMISSION_DENIED"


def test_update_store_admin(
    client: TestClient,
    test_stores: list[Store],
    admin_headers: dict,
):
    """Test updating store exposure and metadata."""
    store1_id = test_stores[0].id
    res = client.patch(
        f"/api/v1/stores/{store1_id}",
        json={"size_sqft": 30000.0, "avg_daily_transactions": 3500.0},
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["size_sqft"] == 30000.0
    assert res.json()["avg_daily_transactions"] == 3500.0
