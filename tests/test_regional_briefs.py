"""Tests for Weekly One-Page Regional Executive Brief service and API endpoints."""

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.models.store import Store
from app.schemas.feedback import FeedbackSubmitSingle
from app.services.ingestion_service import ingestion_service
from app.services.regional_brief_service import regional_brief_service


def test_week_over_week_zero_baseline_handling():
    """Verify that WoW calculations gracefully handle zero baselines without ZeroDivisionError."""
    # Zero in previous week, positive in current week
    res1 = regional_brief_service.calculate_week_over_week(current_count=5, previous_count=0)
    assert res1["percentage_change"] is None
    assert res1["direction"] == "UP"
    assert "New" in res1["trend_label"]

    # Zero in both weeks
    res2 = regional_brief_service.calculate_week_over_week(current_count=0, previous_count=0)
    assert res2["percentage_change"] is None
    assert res2["direction"] == "STABLE"

    # Standard positive change
    res3 = regional_brief_service.calculate_week_over_week(current_count=15, previous_count=10)
    assert res3["percentage_change"] == 50.0
    assert res3["direction"] == "UP"

    # Standard drop
    res4 = regional_brief_service.calculate_week_over_week(current_count=8, previous_count=10)
    assert res4["percentage_change"] == -20.0
    assert res4["direction"] == "DOWN"


def test_generate_regional_brief_service(db: Session, test_stores: list[Store]):
    """Verify regional brief generation, metric compilation, and HTML formatting."""
    store = test_stores[0]
    store.region = "South"
    db.commit()

    # Ingest feedback to create an incident
    sub = FeedbackSubmitSingle(
        store_id=store.id,
        text="The dairy freezer is warm and yogurt cartons are spoiling.",
        event_timestamp=datetime.now(timezone.utc),
    )
    ingestion_service.ingest_single(db, sub)

    # Generate brief for South region
    brief = regional_brief_service.generate_brief(db=db, region="South")
    assert brief.region == "South"
    assert brief.week_start < brief.week_end
    assert brief.executive_summary is not None
    assert len(brief.executive_summary) > 10
    assert brief.metrics_json is not None
    assert brief.metrics_json["total_stores"] >= 1
    assert brief.html_content is not None
    assert "<html>" in brief.html_content
    assert "South" in brief.html_content


def test_regional_briefs_api_endpoints(client: TestClient, admin_headers: dict, db: Session, test_stores: list[Store]):
    """Verify API routes for regional briefs."""
    # List regions
    resp = client.get("/api/v1/regional-briefs/regions", headers=admin_headers)
    assert resp.status_code == 200
    regions = resp.json()
    assert isinstance(regions, list)
    assert len(regions) > 0

    # Get latest brief for South
    resp_brief = client.get("/api/v1/regional-briefs/South/latest", headers=admin_headers)
    assert resp_brief.status_code == 200
    brief_data = resp_brief.json()
    assert brief_data["region"] == "South"
    brief_id = brief_data["id"]

    # Get HTML version
    resp_html = client.get(f"/api/v1/regional-briefs/{brief_id}/html")
    assert resp_html.status_code == 200
    assert "text/html" in resp_html.headers.get("content-type", "")
