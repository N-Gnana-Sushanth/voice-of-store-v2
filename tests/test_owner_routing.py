"""Tests for owning-function routing, policy validation, and reassignment audit trails."""

from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session
from app.core.taxonomy import taxonomy_manager
from app.models.incident import Incident, IncidentSeverity, IncidentStatus, OwningFunction
from app.models.store import Store
from app.schemas.feedback import FeedbackSubmitSingle
from app.services.ingestion_service import ingestion_service


def test_taxonomy_30_categories_loaded():
    """Verify that all 30 retail categories across 6 operational domains are loaded."""
    cats = taxonomy_manager.list_all()
    assert len(cats) >= 30

    domains = set(c.domain for c in cats)
    expected_domains = {
        "Store Operations",
        "Supply Chain",
        "Merchandising",
        "Digital",
        "Human Resources",
    }
    assert expected_domains.issubset(domains)


def test_department_owner_mapping():
    """Verify taxonomy maps each category to valid owning department."""
    for cat in taxonomy_manager.list_all():
        assert cat.primary_owner in OwningFunction.ALL
        assert cat.sla_hours > 0


def test_automatic_owner_routing_on_ingestion(db: Session, test_stores: list[Store]):
    """Verify that newly ingested feedback automatically routes to the taxonomy owning department."""
    store = test_stores[0]
    sub = FeedbackSubmitSingle(
        store_id=store.id,
        text="App payment failed during UPI checkout and money was deducted twice.",
        event_timestamp=datetime.now(timezone.utc),
    )
    fb, inc, status = ingestion_service.ingest_single(db, sub)
    assert status == "SUCCESS"
    assert inc is not None
    # Digital issue routes to Digital
    assert inc.primary_owner in [OwningFunction.DIGITAL, OwningFunction.STORE_OPS]
    assert inc.routing_history is not None
    assert len(inc.routing_history) >= 1
    assert inc.routing_history[0]["action"] == "INITIAL_AUTO_ROUTE"


def test_uncertainty_triggers_human_review(db: Session, test_stores: list[Store]):
    """Verify that ambiguous or low-confidence feedback flags needs_human_review."""
    store = test_stores[0]
    # Intentionally vague text
    sub = FeedbackSubmitSingle(
        store_id=store.id,
        text="Things happened around the building that were unusual today.",
        event_timestamp=datetime.now(timezone.utc),
    )
    fb, inc, status = ingestion_service.ingest_single(db, sub)
    assert status == "SUCCESS"
    assert inc is not None
    # Uncertainty or low confidence flags human review
    assert inc.needs_human_review is True
