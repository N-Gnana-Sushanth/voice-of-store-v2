"""Unit and integration tests for store analytics and exposure normalization."""

from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.store import Store
from app.schemas.feedback import FeedbackSubmitSingle
from app.services.analytics_service import analytics_service
from app.services.ingestion_service import ingestion_service


def test_empty_dataset_analytics(db: Session, test_stores: list[Store]):
    """Verify analytics on empty store returns zero counts without zero division."""
    store = test_stores[0]
    analytics = analytics_service.get_store_analytics(db=db, store_id=store.id, time_window_days=30)
    assert analytics.total_feedback_volume == 0
    assert analytics.total_distinct_incidents == 0
    assert analytics.overall_normalized_rate == 0.0
    assert analytics.sample_size_confidence == "LOW"


def test_distinct_incident_count_and_exposure_normalization(db: Session, test_stores: list[Store]):
    """
    Verify analytics distinguishes raw feedback volume from distinct incidents
    and correctly calculates incidents per 1,000 transactions.
    """
    store = test_stores[0]  # avg_daily_transactions = 3000
    now = datetime.now(timezone.utc)

    # Ingest 3 feedbacks: 2 duplicates about register freeze (forming 1 incident) + 1 feedback about clean floors (forming 2nd incident)
    sub1 = FeedbackSubmitSingle(
        store_id=store.id,
        text="Card reader froze at checkout lane 1 and double charged credit card.",
        event_timestamp=now,
    )
    sub2 = FeedbackSubmitSingle(
        store_id=store.id,
        text="Card reader froze at register lane 1 and double charged swipe.",
        event_timestamp=now,
    )
    sub3 = FeedbackSubmitSingle(
        store_id=store.id,
        text="Produce floor was clean and well stocked with organic apples.",
        event_timestamp=now,
    )

    ingestion_service.ingest_single(db, sub1)
    ingestion_service.ingest_single(db, sub2)
    ingestion_service.ingest_single(db, sub3)

    analytics = analytics_service.get_store_analytics(db=db, store_id=store.id, time_window_days=30)

    # 3 total feedback records ingested
    assert analytics.total_feedback_volume == 3
    # 2 distinct incidents formed (due to deduplication)
    assert analytics.total_distinct_incidents == 2
    assert analytics.duplicate_feedback_count == 1
    assert analytics.deduplication_ratio > 0.0

    # Total exposure = 3000 tx/day * 30 days = 90,000 transactions
    expected_exposure = 3000.0 * 30.0
    assert analytics.total_exposure == expected_exposure
    # Normalized rate = (2 / 90,000) * 1000 = ~0.0222 per 1k transactions
    assert analytics.overall_normalized_rate > 0.0


def test_store_comparisons_api(client: TestClient, test_stores: list[Store], admin_headers: dict):
    """Test side-by-side store comparisons endpoint."""
    res = client.get("/api/v1/analytics/comparisons", headers=admin_headers)
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 2
    # Ensure items contain exposure-normalized fields
    for item in items:
        assert "normalized_rate" in item
        assert "exposure_volume" in item
        assert "distinct_incidents" in item
