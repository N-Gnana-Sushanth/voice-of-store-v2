"""Unit and integration tests for multi-signal incident deduplication."""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.feedback import FeedbackRecord
from app.models.incident import Incident, IncidentCategory, IncidentSeverity, IncidentStatus
from app.models.store import Store
from app.schemas.feedback import FeedbackSubmitSingle
from app.services.deduplicator import deduplicator
from app.services.ingestion_service import ingestion_service


def test_exact_and_near_duplicate_matching(db: Session, test_stores: list[Store]):
    """Test that repeated complaints about the same problem consolidate into one incident."""
    store = test_stores[0]
    now = datetime.now(timezone.utc)

    # 1. Ingest first feedback
    sub1 = FeedbackSubmitSingle(
        store_id=store.id,
        text="Card reader froze at checkout lane 3 and double charged my debit card.",
        event_timestamp=now,
    )
    fb1, inc1, status1 = ingestion_service.ingest_single(db, sub1)
    assert status1 == "SUCCESS"
    assert inc1 is not None
    assert inc1.feedback_count == 1

    # 2. Ingest near-duplicate feedback within 2 hours
    sub2 = FeedbackSubmitSingle(
        store_id=store.id,
        text="Register lane 3 card machine froze during swipe and charged credit card twice.",
        event_timestamp=now + timedelta(hours=2),
    )
    fb2, inc2, status2 = ingestion_service.ingest_single(db, sub2)
    assert status2 == "SUCCESS"
    assert inc2 is not None

    # Should consolidate into the same incident!
    assert inc2.id == inc1.id
    assert inc2.feedback_count == 2
    # But both raw feedback records are preserved!
    assert fb1.id != fb2.id
    assert fb1.incident_id == inc1.id
    assert fb2.incident_id == inc1.id


def test_cross_store_deduplication_isolation(db: Session, test_stores: list[Store]):
    """Ensure identical feedback from DIFFERENT stores is NEVER merged into the same incident."""
    store1 = test_stores[0]
    store2 = test_stores[1]
    now = datetime.now(timezone.utc)
    text = "The bathroom was completely out of toilet paper and hand soap."

    sub1 = FeedbackSubmitSingle(store_id=store1.id, text=text, event_timestamp=now)
    fb1, inc1, _ = ingestion_service.ingest_single(db, sub1)

    sub2 = FeedbackSubmitSingle(store_id=store2.id, text=text, event_timestamp=now)
    fb2, inc2, _ = ingestion_service.ingest_single(db, sub2)

    assert inc1.id != inc2.id
    assert inc1.store_id == store1.id
    assert inc2.store_id == store2.id


def test_deduplication_never_suppresses_safety_escalation(db: Session, test_stores: list[Store]):
    """
    Ensure that if a new report matches an existing incident but reports a serious safety
    escalation, the incident is upgraded and escalated.
    """
    store = test_stores[0]
    now = datetime.now(timezone.utc)

    # First report: general spill in produce
    sub1 = FeedbackSubmitSingle(
        store_id=store.id,
        text="Water puddle on floor near produce aisle from cooler.",
        event_timestamp=now,
    )
    fb1, inc1, _ = ingestion_service.ingest_single(db, sub1)
    assert inc1.safety_flag is False

    # Second report: customer slipped and fell on the same puddle
    sub2 = FeedbackSubmitSingle(
        store_id=store.id,
        text="Water puddle near produce cooler, customer slipped and fell down and was bleeding.",
        event_timestamp=now + timedelta(hours=1),
    )
    fb2, inc2, _ = ingestion_service.ingest_single(db, sub2)

    # Consolidated, but upgraded to safety critical
    assert inc2.id == inc1.id
    assert inc2.safety_flag is True
    assert inc2.policy_escalated is True
    assert inc2.severity == IncidentSeverity.CRITICAL
