"""Unit and integration tests for emerging-issue detection engine."""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.alert import Alert, AlertStatus, AlertType
from app.models.incident import Incident, IncidentCategory, IncidentSeverity, IncidentStatus
from app.models.store import Store
from app.services.emerging_detector import emerging_detector


def test_low_sample_guard_prevents_false_alerts(db: Session, test_stores: list[Store]):
    """Verify detector does NOT trigger alerts on isolated single counts (low sample guard)."""
    store = test_stores[0]
    now = datetime.now(timezone.utc)

    # Insert just 1 isolated minor customer service incident
    inc = Incident(
        store_id=store.id,
        category=IncidentCategory.CUSTOMER_SERVICE,
        severity=IncidentSeverity.LOW,
        sentiment="NEGATIVE",
        sentiment_score=-0.4,
        classification_confidence=0.8,
        status=IncidentStatus.OPEN,
        first_seen_at=now - timedelta(days=1),
        last_seen_at=now - timedelta(days=1),
        feedback_count=1,
        model_version="v1.0.0",
        policy_version="v1.0.0",
    )
    db.add(inc)
    db.commit()

    alerts = emerging_detector.scan_for_emerging_issues(db=db, store_id=store.id, as_of_time=now)
    # Should not trigger an alert because sample size < 3
    assert len(alerts) == 0


def test_detect_spike_and_duplicate_suppression(db: Session, test_stores: list[Store]):
    """
    Test detection of genuine rate surge and verify duplicate suppression
    updates the existing active alert rather than creating duplicate alerts.
    """
    store = test_stores[0]
    now = datetime.now(timezone.utc)

    # 1. Seed historical baseline in [-37 days, -7 days]: 2 incidents in 30 days
    for d in [10, 20]:
        db.add(Incident(
            store_id=store.id,
            category=IncidentCategory.BILLING_PAYMENTS,
            severity=IncidentSeverity.MEDIUM,
            sentiment="NEGATIVE",
            sentiment_score=-0.6,
            classification_confidence=0.85,
            status=IncidentStatus.RESOLVED,
            first_seen_at=now - timedelta(days=d),
            last_seen_at=now - timedelta(days=d),
            feedback_count=1,
            model_version="v1.0.0",
            policy_version="v1.0.0",
        ))

    # 2. Seed sudden surge in current observation window [now - 7 days, now]: 6 billing incidents!
    for i in range(6):
        db.add(Incident(
            store_id=store.id,
            category=IncidentCategory.BILLING_PAYMENTS,
            severity=IncidentSeverity.HIGH,
            sentiment="NEGATIVE",
            sentiment_score=-0.8,
            classification_confidence=0.9,
            status=IncidentStatus.OPEN,
            first_seen_at=now - timedelta(days=1, hours=i * 2),
            last_seen_at=now - timedelta(days=1, hours=i * 2),
            feedback_count=1,
            model_version="v1.0.0",
            policy_version="v1.0.0",
        ))
    db.commit()

    # Initial scan: should detect spike
    alerts1 = emerging_detector.scan_for_emerging_issues(db=db, store_id=store.id, as_of_time=now)
    assert len(alerts1) >= 1
    alert = alerts1[0]
    assert alert.category == IncidentCategory.BILLING_PAYMENTS
    assert alert.current_count == 6
    assert alert.detection_count == 1
    assert alert.status == AlertStatus.ACTIVE
    assert "metrics" in alert.evidence_json

    # Repeat scan immediately: should update the same alert (cooldown/suppression), NOT create a new one!
    alerts2 = emerging_detector.scan_for_emerging_issues(db=db, store_id=store.id, as_of_time=now)
    assert len(alerts2) >= 1
    alert2 = alerts2[0]
    assert alert2.id == alert.id
    assert alert2.detection_count == 2

    # Database should only contain 1 alert row for this store and category
    total_db_alerts = db.query(Alert).filter(Alert.store_id == store.id, Alert.category == IncidentCategory.BILLING_PAYMENTS).count()
    assert total_db_alerts == 1


def test_change_detection_strategies_comparison():
    """Verify EWMA, CUSUM, and Bayesian Poisson-Gamma strategies on normal vs surge counts."""
    from app.services.emerging_detector import (
        PoissonGammaStrategy,
        EWMAStrategy,
        CUSUMStrategy,
        compare_detection_strategies,
    )

    # Normal count: 1 observed when 1.0 expected
    normal_res = compare_detection_strategies(current_count=1, expected_count=1.0)
    assert normal_res["poisson_gamma"]["is_alert"] is False
    assert normal_res["ewma"]["is_alert"] is False
    assert normal_res["cusum"]["is_alert"] is False
    assert normal_res["consensus_alert"] is False

    # Surge count: 6 observed when 1.0 expected
    surge_res = compare_detection_strategies(current_count=6, expected_count=1.0)
    assert surge_res["poisson_gamma"]["is_alert"] is True
    assert surge_res["ewma"]["is_alert"] is True
    assert surge_res["cusum"]["is_alert"] is True
    assert surge_res["consensus_alert"] is True
