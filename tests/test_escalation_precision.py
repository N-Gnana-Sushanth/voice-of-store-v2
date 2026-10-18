"""Tests for Escalation Precision Analytics, Wilson confidence intervals, and review queue."""

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.escalation_review import EscalationReview
from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.models.store import Store
from app.schemas.feedback import FeedbackSubmitSingle
from app.services.ingestion_service import ingestion_service
from app.services.precision_service import precision_service


def test_precision_unreviewed_isolation(db: Session, test_stores: list[Store]):
    """Verify unreviewed cases are strictly excluded from the denominator to avoid FP distortion."""
    store = test_stores[0]

    # Ingest critical safety issue (auto-escalated by policy)
    sub = FeedbackSubmitSingle(
        store_id=store.id,
        text="Customer slipped and fell on wet floor near entrance, bleeding from elbow.",
        event_timestamp=datetime.now(timezone.utc),
    )
    fb, inc, status = ingestion_service.ingest_single(db, sub)
    assert inc.policy_escalated is True

    # Check metrics before any review
    metrics = precision_service.get_precision_metrics(db=db)
    assert metrics["unreviewed_count"] >= 1

    # If all cases in window are unreviewed, precision is None rather than 0.0 (no false-positive bias)
    # The denominator only includes verified evaluated cases (TP + FP)
    assert metrics["denominator_total"] == metrics["sample_size_evaluated"]


def test_precision_human_review_and_wilson_ci(db: Session, test_stores: list[Store]):
    """Verify recording human reviews updates precision metrics and computes Wilson score CI."""
    store = test_stores[0]

    # Ingest two escalated reports
    sub1 = FeedbackSubmitSingle(
        store_id=store.id,
        text="Walk-in freezer temperature is 18C, dairy cartons swelling.",
        event_timestamp=datetime.now(timezone.utc),
    )
    _, inc1, _ = ingestion_service.ingest_single(db, sub1)

    sub2 = FeedbackSubmitSingle(
        store_id=store.id,
        text="Customer observed minor crack on shelf tile near checkout.",
        event_timestamp=datetime.now(timezone.utc),
    )
    _, inc2, _ = ingestion_service.ingest_single(db, sub2)
    inc1.policy_escalated = True
    inc2.policy_escalated = True
    db.commit()

    # Record review 1 as True Positive (actionable)
    rev1 = precision_service.record_review(
        db=db,
        incident_id=inc1.id,
        is_truly_actionable=True,
        review_notes="Technician verified failed compressor",
    )
    assert rev1.is_truly_actionable is True

    # Record review 2 as False Positive (spurious / low risk)
    rev2 = precision_service.record_review(
        db=db,
        incident_id=inc2.id,
        is_truly_actionable=False,
        review_notes="Cosmetic tile crack, no hazard",
    )
    assert rev2.is_truly_actionable is False

    # Check precision
    metrics = precision_service.get_precision_metrics(db=db)
    assert metrics["numerator_tp"] >= 1
    assert metrics["denominator_total"] >= 2
    assert metrics["precision"] is not None
    assert 0.0 <= metrics["precision"] <= 1.0

    # Wilson confidence interval is bounded within [0, 100]%
    ci = metrics["confidence_interval_95"]
    assert ci is not None
    assert len(ci) == 2
    assert 0.0 <= ci[0] <= ci[1] <= 100.0


def test_escalation_precision_api_endpoints(client: TestClient, admin_headers: dict, db: Session, test_stores: list[Store]):
    """Verify precision analytics API routes."""
    # Metrics endpoint
    resp_metrics = client.get("/api/v1/analytics/escalation-precision", headers=admin_headers)
    assert resp_metrics.status_code == 200
    data = resp_metrics.json()
    assert "numerator_tp" in data
    assert "denominator_total" in data
    assert "unreviewed_count" in data

    # Review queue endpoint
    resp_queue = client.get("/api/v1/analytics/escalation-precision/queue", headers=admin_headers)
    assert resp_queue.status_code == 200
    queue = resp_queue.json()
    assert isinstance(queue, list)
