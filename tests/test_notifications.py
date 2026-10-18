"""Unit and integration tests for user notification system."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationSeverity
from app.models.user import User


def test_notifications_crud_and_unread_count(
    client: TestClient,
    db: Session,
    admin_user: User,
    admin_headers: dict,
    analyst_user: User,
    analyst_headers: dict,
):
    """Verify notifications listing, unread count, marking read, and user isolation."""
    # 1. Create notifications for admin_user
    n1 = Notification(
        user_id=admin_user.id,
        title="Spike in Refrigeration Complaints",
        message="Store #128 has experienced a 300% surge in freezer issues.",
        severity=NotificationSeverity.HIGH,
        link="/emerging-issues",
        is_read=False,
    )
    n2 = Notification(
        user_id=admin_user.id,
        title="Scheduled Maintenance Complete",
        message="Freezer units at Store #091 inspected.",
        severity=NotificationSeverity.INFO,
        link="/stores",
        is_read=True,
    )
    # Create notification for analyst_user (isolation test)
    n3 = Notification(
        user_id=analyst_user.id,
        title="Analyst Alert",
        message="Private note for analyst.",
        severity=NotificationSeverity.WARNING,
        is_read=False,
    )
    db.add_all([n1, n2, n3])
    db.commit()

    # 2. Test unread count for admin
    res = client.get("/api/v1/notifications/unread-count", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["unread_count"] == 1

    # 3. Test list notifications for admin
    res = client.get("/api/v1/notifications", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    # Ensure analyst notification n3 is NOT exposed to admin
    for item in data["items"]:
        assert item["user_id"] == admin_user.id
        assert item["title"] != "Analyst Alert"

    # 4. Test mark single notification as read
    res = client.patch(f"/api/v1/notifications/{n1.id}/read", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["is_read"] is True

    # Verify unread count is now 0
    res = client.get("/api/v1/notifications/unread-count", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["unread_count"] == 0

    # 5. Test mark all as read for analyst
    res = client.get("/api/v1/notifications/unread-count", headers=analyst_headers)
    assert res.status_code == 200
    assert res.json()["unread_count"] == 1

    res = client.post("/api/v1/notifications/mark-all-read", headers=analyst_headers)
    assert res.status_code == 200
    assert res.json()["updated_count"] == 1

    res = client.get("/api/v1/notifications/unread-count", headers=analyst_headers)
    assert res.status_code == 200
    assert res.json()["unread_count"] == 0
