"""Unit and integration tests for Action Queue remediation tasks."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.task import RemediationTask, TaskStatus


def test_remediation_tasks_crud(
    client: TestClient,
    db: Session,
    admin_headers: dict,
):
    """Verify listing tasks, creating a task, and updating status with audit logging."""
    # 1. Create task
    payload = {
        "task_id": "ACT-TEST-01",
        "title": "Repair Walk-in Freezer #2",
        "store_name": "Store #128 • Chennai",
        "owner": "Store Ops",
        "owner_tag": "store-ops",
        "severity": "High",
        "status": "Open",
        "sla_window": "4 hours remaining",
        "sla_urgent": True,
        "reported_date": "16 Oct 2026",
    }
    res = client.post("/api/v1/tasks", json=payload, headers=admin_headers)
    assert res.status_code == 201
    created_id = res.json()["id"]

    # 2. List tasks
    res = client.get("/api/v1/tasks", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["total"] >= 1

    # 3. Filter tasks
    res = client.get("/api/v1/tasks?status=Open", headers=admin_headers)
    assert res.status_code == 200
    assert any(t["task_id"] == "ACT-TEST-01" for t in res.json()["items"])

    # 4. Update status to In Progress
    res = client.patch(
        f"/api/v1/tasks/{created_id}/status",
        json={"status": "In Progress", "notes": "Technician dispatched."},
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "In Progress"

    # 5. Resolve task
    res = client.patch(
        f"/api/v1/tasks/{created_id}/status",
        json={"status": "Resolved"},
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "Resolved"
    assert res.json()["resolved_at"] is not None
