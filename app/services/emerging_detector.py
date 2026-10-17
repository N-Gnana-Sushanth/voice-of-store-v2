"""Emerging-issue detection engine with statistical baselines and explainable alerts."""

from datetime import datetime, timedelta, timezone
import math
from typing import Any, Dict, List, Optional
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.models.alert import Alert, AlertSeverity, AlertStatus, AlertType
from app.models.baseline import HistoricalBaseline
from app.models.incident import Incident, IncidentCategory, IncidentSeverity
from app.models.store import Store


class EmergingIssueDetector:
    """Detects unusual increases in incident rates using historical and peer comparisons."""

    BASELINE_VERSION = "v1.2.0-poisson-zscore"

    def __init__(
        self,
        observation_window_days: int = 7,
        baseline_window_days: int = 30,
        min_current_count: int = 3,
        rate_ratio_threshold: float = 2.0,
        z_score_threshold: float = 2.0,
    ):
        self.observation_window_days = observation_window_days
        self.baseline_window_days = baseline_window_days
        self.min_current_count = min_current_count
        self.rate_ratio_threshold = rate_ratio_threshold
        self.z_score_threshold = z_score_threshold

    def calculate_or_get_baseline(
        self,
        db: Session,
        store: Store,
        category: str,
        as_of_time: datetime,
    ) -> HistoricalBaseline:
        """
        Calculate historical baseline strictly using data prior to the observation window
        to avoid future data leakage.
        """
        obs_start = as_of_time - timedelta(days=self.observation_window_days)
        base_start = obs_start - timedelta(days=self.baseline_window_days)

        # Count historical incidents in [base_start, obs_start)
        hist_count = (
            db.query(func.count(Incident.id))
            .filter(
                Incident.store_id == store.id,
                Incident.category == category,
                Incident.first_seen_at >= base_start,
                Incident.first_seen_at < obs_start,
            )
            .scalar() or 0
        )

        daily_tx = store.avg_daily_transactions if store.avg_daily_transactions > 0 else 1000.0
        exposure_units = daily_tx * self.baseline_window_days
        normalized_rate = (hist_count / exposure_units) * 1000.0

        min_sample_met = hist_count >= 5

        # Check existing baseline or create/update
        baseline = (
            db.query(HistoricalBaseline)
            .filter(
                HistoricalBaseline.store_id == store.id,
                HistoricalBaseline.category == category,
                HistoricalBaseline.time_window_days == self.baseline_window_days,
                HistoricalBaseline.baseline_version == self.BASELINE_VERSION,
            )
            .first()
        )

        if not baseline:
            baseline = HistoricalBaseline(
                store_id=store.id,
                category=category,
                time_window_days=self.baseline_window_days,
                historical_incident_count=hist_count,
                exposure_units=exposure_units,
                normalized_rate=round(normalized_rate, 4),
                baseline_mean=round(normalized_rate, 4),
                baseline_std=round(math.sqrt(max(hist_count, 1.0)) / exposure_units * 1000.0, 4),
                min_sample_met=min_sample_met,
                baseline_version=self.BASELINE_VERSION,
                calculated_at=as_of_time,
            )
            db.add(baseline)
        else:
            baseline.historical_incident_count = hist_count
            baseline.exposure_units = exposure_units
            baseline.normalized_rate = round(normalized_rate, 4)
            baseline.baseline_mean = round(normalized_rate, 4)
            baseline.min_sample_met = min_sample_met
            baseline.calculated_at = as_of_time

        db.flush()
        return baseline

    def compute_peer_median_rate(
        self,
        db: Session,
        category: str,
        target_store_id: str,
        obs_start: datetime,
        obs_end: datetime,
    ) -> Optional[float]:
        """Compute median normalized rate for this category across peer stores in the same window."""
        peer_stores = (
            db.query(Store)
            .filter(Store.id != target_store_id, Store.is_active == True)
            .all()
        )
        if not peer_stores:
            return None

        peer_rates: List[float] = []
        for s in peer_stores:
            count = (
                db.query(func.count(Incident.id))
                .filter(
                    Incident.store_id == s.id,
                    Incident.category == category,
                    Incident.first_seen_at >= obs_start,
                    Incident.first_seen_at <= obs_end,
                )
                .scalar() or 0
            )
            daily_tx = s.avg_daily_transactions if s.avg_daily_transactions > 0 else 1000.0
            exp = daily_tx * self.observation_window_days
            rate = (count / exp) * 1000.0
            peer_rates.append(rate)

        if not peer_rates:
            return None

        peer_rates.sort()
        mid = len(peer_rates) // 2
        return peer_rates[mid]

    def scan_for_emerging_issues(
        self,
        db: Session,
        store_id: Optional[str] = None,
        as_of_time: Optional[datetime] = None,
    ) -> List[Alert]:
        """
        Scan stores and categories for emerging issues as of a given timestamp.
        Returns list of newly generated or updated active alerts.
        """
        if as_of_time is None:
            as_of_time = datetime.now(timezone.utc)
        elif as_of_time.tzinfo is None:
            as_of_time = as_of_time.replace(tzinfo=timezone.utc)

        obs_start = as_of_time - timedelta(days=self.observation_window_days)

        # Stores to evaluate
        store_query = db.query(Store).filter(Store.is_active == True)
        if store_id:
            store_query = store_query.filter(Store.id == store_id)
        stores = store_query.all()

        categories = IncidentCategory.ALL
        generated_alerts: List[Alert] = []

        for store in stores:
            daily_tx = store.avg_daily_transactions if store.avg_daily_transactions > 0 else 1000.0
            current_exposure = daily_tx * self.observation_window_days

            for category in categories:
                # 1. Fetch current window incidents
                current_incidents: List[Incident] = (
                    db.query(Incident)
                    .filter(
                        Incident.store_id == store.id,
                        Incident.category == category,
                        Incident.first_seen_at >= obs_start,
                        Incident.first_seen_at <= as_of_time,
                    )
                    .all()
                )
                current_count = len(current_incidents)

                # Check if there are urgent safety escalations in the current window
                has_safety_escalation = any(
                    inc.safety_flag or inc.allergen_flag or inc.severity == IncidentSeverity.CRITICAL
                    for inc in current_incidents
                )

                # Low sample protection: skip if fewer than min count UNLESS urgent safety
                if current_count < self.min_current_count and not has_safety_escalation:
                    continue

                # 2. Retrieve baseline (leak-free: before obs_start)
                baseline = self.calculate_or_get_baseline(db, store, category, as_of_time)
                base_rate = float(baseline.normalized_rate)

                # Calculate current rate
                curr_rate = (current_count / current_exposure) * 1000.0

                # Expected count based on historical baseline
                expected_count = (base_rate / 1000.0) * current_exposure
                expected_count = max(expected_count, 0.5)  # Avoid zero division

                rate_ratio = curr_rate / max(base_rate, 0.05)

                # Poisson / Normal approximation Z-Score
                z_score = (current_count - expected_count) / math.sqrt(expected_count)

                # 3. Peer store comparison
                peer_median = self.compute_peer_median_rate(
                    db, category, store.id, obs_start, as_of_time
                )

                # 4. Determine alert qualification
                alert_type: Optional[str] = None
                severity: Optional[str] = None
                confidence = 0.80

                if has_safety_escalation:
                    alert_type = AlertType.URGENT_SAFETY
                    severity = AlertSeverity.CRITICAL
                    confidence = 0.95
                elif rate_ratio >= 3.0 and z_score >= 2.5:
                    alert_type = AlertType.SPIKE
                    severity = AlertSeverity.HIGH
                    confidence = min(0.95, 0.70 + (z_score * 0.05))
                elif rate_ratio >= self.rate_ratio_threshold and z_score >= self.z_score_threshold:
                    alert_type = AlertType.SUSTAINED_INCREASE
                    severity = AlertSeverity.WARNING
                    confidence = 0.85
                elif peer_median is not None and peer_median > 0 and (curr_rate / peer_median) >= 2.5:
                    alert_type = AlertType.PEER_DEVIATION
                    severity = AlertSeverity.WARNING
                    confidence = 0.80

                if not alert_type:
                    continue  # Did not breach detection thresholds

                # 5. Build explainable evidence payload
                evidence = {
                    "store_id": store.id,
                    "store_number": store.store_number,
                    "store_name": store.name,
                    "category": category,
                    "alert_type": alert_type,
                    "detection_timestamp": as_of_time.isoformat(),
                    "observation_window": {
                        "days": self.observation_window_days,
                        "start_utc": obs_start.isoformat(),
                        "end_utc": as_of_time.isoformat(),
                    },
                    "metrics": {
                        "current_count": current_count,
                        "current_rate_per_1000": round(curr_rate, 4),
                        "baseline_rate_per_1000": round(base_rate, 4),
                        "expected_count": round(expected_count, 2),
                        "rate_ratio": round(rate_ratio, 2),
                        "z_score": round(z_score, 2),
                        "exposure_volume": round(current_exposure, 1),
                        "exposure_unit": "transactions",
                    },
                    "peer_comparison": {
                        "peer_median_rate_per_1000": round(peer_median, 4) if peer_median is not None else None,
                        "ratio_to_peer_median": round(curr_rate / peer_median, 2) if peer_median and peer_median > 0 else None,
                    },
                    "sample_size_info": {
                        "current_sample_size": current_count,
                        "baseline_sample_size": baseline.historical_incident_count,
                        "baseline_sample_met": baseline.min_sample_met,
                    },
                    "severity_rationale": (
                        f"Incident rate ({curr_rate:.2f}/1k) is {rate_ratio:.1f}x higher than baseline ({base_rate:.2f}/1k) "
                        f"with Z-score of {z_score:.2f} over {self.observation_window_days} days."
                    ),
                    "representative_incidents": [
                        {
                            "incident_id": inc.id,
                            "severity": inc.severity,
                            "first_seen": inc.first_seen_at.isoformat(),
                            "summary": inc.evidence_summary[:200] if inc.evidence_summary else "",
                        }
                        for inc in current_incidents[:5]
                    ],
                }

                # 6. Check for duplicate suppression / cooldown
                existing_alert: Optional[Alert] = (
                    db.query(Alert)
                    .filter(
                        Alert.store_id == store.id,
                        Alert.category == category,
                        Alert.status.in_([AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]),
                    )
                    .first()
                )

                if existing_alert:
                    # Update existing alert in-place
                    existing_alert.current_count = current_count
                    existing_alert.current_rate = round(curr_rate, 4)
                    existing_alert.baseline_rate = round(base_rate, 4)
                    existing_alert.rate_ratio = round(rate_ratio, 2)
                    existing_alert.z_score = round(z_score, 2)
                    existing_alert.exposure_volume = round(current_exposure, 1)
                    existing_alert.sample_size = current_count
                    existing_alert.confidence_score = round(confidence, 4)
                    existing_alert.evidence_json = evidence
                    existing_alert.peer_comparison_json = evidence.get("peer_comparison")
                    existing_alert.last_detected_at = as_of_time
                    existing_alert.detection_count += 1
                    # Escalate severity if new severity is higher
                    if severity == AlertSeverity.CRITICAL and existing_alert.severity != AlertSeverity.CRITICAL:
                        existing_alert.severity = AlertSeverity.CRITICAL
                    generated_alerts.append(existing_alert)
                else:
                    new_alert = Alert(
                        store_id=store.id,
                        category=category,
                        alert_type=alert_type,
                        severity=severity or AlertSeverity.WARNING,
                        status=AlertStatus.ACTIVE,
                        current_count=current_count,
                        current_rate=round(curr_rate, 4),
                        baseline_rate=round(base_rate, 4),
                        rate_ratio=round(rate_ratio, 2),
                        z_score=round(z_score, 2),
                        observation_window_days=self.observation_window_days,
                        exposure_volume=round(current_exposure, 1),
                        sample_size=current_count,
                        confidence_score=round(confidence, 4),
                        evidence_json=evidence,
                        peer_comparison_json=evidence.get("peer_comparison"),
                        first_detected_at=as_of_time,
                        last_detected_at=as_of_time,
                        detection_count=1,
                    )
                    db.add(new_alert)
                    generated_alerts.append(new_alert)

        db.commit()
        return generated_alerts


# Singleton instance
emerging_detector = EmergingIssueDetector()
