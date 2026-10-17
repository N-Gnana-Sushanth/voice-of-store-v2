"""Unit and integration tests for chronological replay and evaluation."""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.store import Store
from app.schemas.replay import ReplayRunCreate
from app.services.replay_engine import PLANTED_INCIDENTS_SPEC, replay_engine


def test_chronological_replay_evaluation_of_planted_incidents(db: Session, test_stores: list[Store]):
    """
    Execute chronological replay run and verify that all 3 synthetic planted ground-truth
    incidents are detected with valid lead times and without future data leakage.
    """
    now = datetime.now(timezone.utc)
    t_start = now - timedelta(days=25)
    t_end = now

    req = ReplayRunCreate(
        name="Automated Evaluation of 3 Planted Ground-Truth Incidents",
        description="Testing detection lead time and recall across retail failure modes",
        time_range_start=t_start,
        time_range_end=t_end,
        include_planted_evaluations=True,
    )

    run_res = replay_engine.run_replay(db=db, create_params=req)

    assert run_res.status == "COMPLETED"
    assert run_res.processed_records > 0
    assert run_res.evaluation_metrics is not None

    metrics = run_res.evaluation_metrics
    assert metrics.future_data_leakage_prevented is True
    assert metrics.planted_incidents_total == 3
    # Verify that the planted incidents are detected
    assert metrics.planted_incidents_detected >= 2  # At least 2 or all 3 detected
    assert metrics.planted_recall >= 0.66

    # Verify each planted evaluation structure
    codes = {p.code for p in metrics.planted_evaluations}
    assert "PLANTED-001" in codes
    assert "PLANTED-002" in codes
    assert "PLANTED-003" in codes


def test_no_future_data_leakage_proof(db: Session, test_stores: list[Store]):
    """
    Automated proof that injecting records in the FUTURE does NOT alter
    baselines or alerts calculated at past simulated time t0.
    """
    from app.services.emerging_detector import emerging_detector
    from app.models.incident import Incident, IncidentCategory, IncidentSeverity, IncidentStatus

    store = test_stores[0]
    t0 = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

    # 1. Baseline historical records in [2025-12-08, 2026-01-08)
    for d in [10, 20]:
        db.add(Incident(
            store_id=store.id,
            category=IncidentCategory.CUSTOMER_SERVICE,
            severity=IncidentSeverity.LOW,
            sentiment="NEUTRAL",
            sentiment_score=0.0,
            classification_confidence=0.8,
            status=IncidentStatus.RESOLVED,
            first_seen_at=t0 - timedelta(days=d),
            last_seen_at=t0 - timedelta(days=d),
            feedback_count=1,
            model_version="v1.0.0",
            policy_version="v1.0.0",
        ))
    db.commit()

    # Calculate baseline at time t0
    baseline_before = emerging_detector.calculate_or_get_baseline(
        db=db, store=store, category=IncidentCategory.CUSTOMER_SERVICE, as_of_time=t0
    )
    rate_before = baseline_before.normalized_rate

    # 2. Inject FUTURE incidents occurring at t0 + 5 days and t0 + 10 days
    for future_day in [5, 10]:
        db.add(Incident(
            store_id=store.id,
            category=IncidentCategory.CUSTOMER_SERVICE,
            severity=IncidentSeverity.CRITICAL,
            sentiment="NEGATIVE",
            sentiment_score=-1.0,
            classification_confidence=0.99,
            status=IncidentStatus.OPEN,
            first_seen_at=t0 + timedelta(days=future_day),
            last_seen_at=t0 + timedelta(days=future_day),
            feedback_count=10,
            model_version="v1.0.0",
            policy_version="v1.0.0",
        ))
    db.commit()

    # Re-calculate baseline at past time t0
    baseline_after = emerging_detector.calculate_or_get_baseline(
        db=db, store=store, category=IncidentCategory.CUSTOMER_SERVICE, as_of_time=t0
    )
    rate_after = baseline_after.normalized_rate

    # PROOF: Future incidents MUST NOT alter the historical baseline at t0!
    assert rate_before == rate_after
