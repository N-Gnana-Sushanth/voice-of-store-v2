"""Escalation precision service for computing verified actionability metrics."""

from datetime import datetime, timedelta, timezone
import math
from typing import Any, Dict, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.exceptions import EntityNotFoundError
from app.models.escalation_review import EscalationReview
from app.models.incident import Incident, IncidentSeverity
from app.models.store import Store


class EscalationPrecisionService:
    """Computes verified precision of escalated incidents based on human review."""

    @classmethod
    def get_precision_metrics(
        cls,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        region: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate: Precision = True Positives / (True Positives + False Positives).
        Unreviewed cases are explicitly isolated and NEVER counted as false positives.
        """
        if end_date is None:
            end_date = datetime.now(timezone.utc)
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        # Base query for escalated incidents in the time window
        incident_query = (
            db.query(Incident)
            .join(Store, Incident.store_id == Store.id)
            .filter(
                Incident.policy_escalated == True,
                Incident.first_seen_at >= start_date,
                Incident.first_seen_at <= end_date,
            )
        )

        if region and region != "All":
            incident_query = incident_query.filter(Store.region == region)

        escalated_incidents = incident_query.all()
        total_escalated = len(escalated_incidents)

        if total_escalated == 0:
            return {
                "evaluation_window": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": (end_date - start_date).days,
                },
                "region_filter": region or "All",
                "sample_size": 0,
                "numerator_tp": 0,
                "denominator_total": 0,
                "unreviewed_count": 0,
                "precision": None,
                "precision_percentage": None,
                "confidence_interval_95": None,
                "breakdowns": {"by_category": {}, "by_severity": {}, "by_region": {}},
                "limitations": [
                    "Zero escalated incidents found in the specified evaluation window.",
                    "No ground-truth review outcomes available."
                ],
            }

        incident_ids = [inc.id for inc in escalated_incidents]
        reviews = (
            db.query(EscalationReview)
            .filter(EscalationReview.incident_id.in_(incident_ids))
            .all()
        )
        review_map = {r.incident_id: r for r in reviews}

        true_positives = 0
        false_positives = 0
        unreviewed = 0

        # Breakdowns
        by_category: Dict[str, Dict[str, int]] = {}
        by_severity: Dict[str, Dict[str, int]] = {}
        by_region: Dict[str, Dict[str, int]] = {}

        for inc in escalated_incidents:
            rev = review_map.get(inc.id)
            cat = inc.category
            sev = inc.severity
            reg = inc.store.region if inc.store and inc.store.region else "Unknown"

            for b_dict, key in [(by_category, cat), (by_severity, sev), (by_region, reg)]:
                if key not in b_dict:
                    b_dict[key] = {"tp": 0, "fp": 0, "unreviewed": 0}

            if rev is None or rev.is_truly_actionable is None:
                unreviewed += 1
                by_category[cat]["unreviewed"] += 1
                by_severity[sev]["unreviewed"] += 1
                by_region[reg]["unreviewed"] += 1
            elif rev.is_truly_actionable is True:
                true_positives += 1
                by_category[cat]["tp"] += 1
                by_severity[sev]["tp"] += 1
                by_region[reg]["tp"] += 1
            else:
                false_positives += 1
                by_category[cat]["fp"] += 1
                by_severity[sev]["fp"] += 1
                by_region[reg]["fp"] += 1

        evaluated_count = true_positives + false_positives
        limitations = []

        if evaluated_count == 0:
            precision = None
            precision_pct = None
            ci_95 = None
            limitations.append("All escalated cases are currently pending human review. No confirmed labels available.")
        else:
            precision = true_positives / evaluated_count
            precision_pct = round(precision * 100.0, 1)

            # Wilson score interval for binomial proportion
            z = 1.96
            n = evaluated_count
            p = precision
            denominator = 1 + (z**2 / n)
            center = (p + (z**2 / (2 * n))) / denominator
            margin = (z * math.sqrt((p * (1 - p) / n) + (z**2 / (4 * n**2)))) / denominator
            ci_lower = max(0.0, round((center - margin) * 100.0, 1))
            ci_upper = min(100.0, round((center + margin) * 100.0, 1))
            ci_95 = [ci_lower, ci_upper]

            if evaluated_count < 15:
                limitations.append(
                    f"Sample size ({evaluated_count} reviewed cases) is below recommended statistical threshold (N >= 30)."
                )

        if unreviewed > 0:
            limitations.append(
                f"{unreviewed} of {total_escalated} escalated cases are awaiting review. These are excluded from the denominator to avoid false-positive distortion."
            )

        return {
            "evaluation_window": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days,
            },
            "region_filter": region or "All",
            "total_escalations": total_escalated,
            "sample_size_evaluated": evaluated_count,
            "numerator_tp": true_positives,
            "denominator_total": evaluated_count,
            "unreviewed_count": unreviewed,
            "precision": round(precision, 4) if precision is not None else None,
            "precision_percentage": precision_pct,
            "confidence_interval_95": ci_95,
            "breakdowns": {
                "by_category": by_category,
                "by_severity": by_severity,
                "by_region": by_region,
            },
            "limitations": limitations,
            "ground_truth_definition": "True Positive = Incident confirmed actionable by Store Ops/Compliance. False Positive = Spurious or unneeded escalation.",
        }

    @classmethod
    def record_review(
        cls,
        db: Session,
        incident_id: str,
        is_truly_actionable: bool,
        reviewer_id: Optional[str] = None,
        review_notes: Optional[str] = None,
    ) -> EscalationReview:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise EntityNotFoundError("Incident", incident_id)

        review = (
            db.query(EscalationReview)
            .filter(EscalationReview.incident_id == incident_id)
            .first()
        )
        if review:
            review.is_truly_actionable = is_truly_actionable
            review.review_notes = review_notes
            review.reviewer_id = reviewer_id
            review.reviewed_at = datetime.now(timezone.utc)
        else:
            review = EscalationReview(
                incident_id=incident_id,
                is_truly_actionable=is_truly_actionable,
                review_notes=review_notes,
                reviewer_id=reviewer_id,
                reviewed_at=datetime.now(timezone.utc),
            )
            db.add(review)

        db.commit()
        db.refresh(review)
        return review


precision_service = EscalationPrecisionService()
