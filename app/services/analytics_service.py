"""Store analytics and exposure-normalized reporting service."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from app.models.alert import Alert, AlertStatus
from app.models.feedback import FeedbackRecord
from app.models.incident import Incident, IncidentStatus
from app.models.store import Store
from app.schemas.analytics import (
    CategoryBreakdownItem,
    DailyTrendItem,
    SeverityBreakdownItem,
    StoreComparisonItem,
    StoreSummaryAnalytics,
)


class AnalyticsService:
    """Computes distinct incident analytics with transaction-based exposure normalization."""

    @classmethod
    def get_store_analytics(
        cls,
        db: Session,
        store_id: Optional[str] = None,
        time_window_days: int = 30,
    ) -> StoreSummaryAnalytics:
        """
        Compute comprehensive analytics for a specific store or all stores combined
        over the specified time window.
        """
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(days=time_window_days)

        # Base filters
        fb_filter = [FeedbackRecord.event_timestamp >= window_start]
        inc_filter = [Incident.first_seen_at >= window_start]
        alert_filter = [Alert.status == AlertStatus.ACTIVE]

        target_store: Optional[Store] = None
        if store_id:
            target_store = db.query(Store).filter(Store.id == store_id).first()
            if target_store:
                fb_filter.append(FeedbackRecord.store_id == store_id)
                inc_filter.append(Incident.store_id == store_id)
                alert_filter.append(Alert.store_id == store_id)

        # 1. Total volumes
        total_feedback = db.query(func.count(FeedbackRecord.id)).filter(and_(*fb_filter)).scalar() or 0
        distinct_incidents = db.query(func.count(Incident.id)).filter(and_(*inc_filter)).scalar() or 0
        duplicate_count = max(0, total_feedback - distinct_incidents)
        dedup_ratio = round(duplicate_count / total_feedback, 4) if total_feedback > 0 else 0.0

        # 2. Lifecycle counts
        open_count = db.query(func.count(Incident.id)).filter(
            and_(*inc_filter, Incident.status == IncidentStatus.OPEN)
        ).scalar() or 0

        investigating_count = db.query(func.count(Incident.id)).filter(
            and_(*inc_filter, Incident.status == IncidentStatus.UNDER_INVESTIGATION)
        ).scalar() or 0

        resolved_count = db.query(func.count(Incident.id)).filter(
            and_(*inc_filter, Incident.status == IncidentStatus.RESOLVED)
        ).scalar() or 0

        # 3. Policy escalation counts
        safety_count = db.query(func.count(Incident.id)).filter(
            and_(*inc_filter, Incident.safety_flag == True)
        ).scalar() or 0

        allergen_count = db.query(func.count(Incident.id)).filter(
            and_(*inc_filter, Incident.allergen_flag == True)
        ).scalar() or 0

        active_alerts = db.query(func.count(Alert.id)).filter(and_(*alert_filter)).scalar() or 0

        # 4. Exposure normalization
        # Primary measure: Customer Transactions. Fallback: Store Square Footage.
        exposure_metric = "transactions"
        if target_store:
            daily_tx = target_store.avg_daily_transactions
            if daily_tx and daily_tx > 0:
                total_exposure = daily_tx * time_window_days
            else:
                exposure_metric = "sqft"
                total_exposure = max(target_store.size_sqft, 1000.0)
        else:
            # Aggregate across all active stores
            stores = db.query(Store).filter(Store.is_active == True).all()
            total_daily_tx = sum(s.avg_daily_transactions for s in stores if s.avg_daily_transactions)
            total_exposure = total_daily_tx * time_window_days if total_daily_tx > 0 else 1.0

        overall_normalized_rate = (
            round((distinct_incidents / total_exposure) * 1000.0, 4) if total_exposure > 0 else 0.0
        )

        # Sample size confidence indicator
        if distinct_incidents >= 30:
            sample_conf = "HIGH"
        elif distinct_incidents >= 10:
            sample_conf = "MODERATE"
        else:
            sample_conf = "LOW"

        # 5. Breakdown by category
        cat_query = (
            db.query(Incident.category, func.count(Incident.id))
            .filter(and_(*inc_filter))
            .group_by(Incident.category)
            .all()
        )
        by_category = [
            CategoryBreakdownItem(
                category=cat,
                incident_count=count,
                percentage=round((count / distinct_incidents) * 100, 2) if distinct_incidents > 0 else 0.0,
                normalized_rate=round((count / total_exposure) * 1000.0, 4) if total_exposure > 0 else 0.0,
            )
            for cat, count in cat_query
        ]

        # 6. Breakdown by severity
        sev_query = (
            db.query(Incident.severity, func.count(Incident.id))
            .filter(and_(*inc_filter))
            .group_by(Incident.severity)
            .all()
        )
        by_severity = [
            SeverityBreakdownItem(
                severity=sev,
                incident_count=count,
                percentage=round((count / distinct_incidents) * 100, 2) if distinct_incidents > 0 else 0.0,
            )
            for sev, count in sev_query
        ]

        # 7. Daily trends
        all_incidents = (
            db.query(Incident)
            .filter(and_(*inc_filter))
            .all()
        )
        all_feedbacks = (
            db.query(FeedbackRecord)
            .filter(and_(*fb_filter))
            .all()
        )

        daily_inc_map: Dict[str, int] = defaultdict(int)
        daily_esc_map: Dict[str, int] = defaultdict(int)
        for inc in all_incidents:
            date_key = inc.first_seen_at.strftime("%Y-%m-%d")
            daily_inc_map[date_key] += 1
            if inc.policy_escalated or inc.safety_flag or inc.allergen_flag:
                daily_esc_map[date_key] += 1

        daily_fb_map: Dict[str, int] = defaultdict(int)
        for fb in all_feedbacks:
            date_key = fb.event_timestamp.strftime("%Y-%m-%d")
            daily_fb_map[date_key] += 1

        daily_trends: List[DailyTrendItem] = []
        for d in range(time_window_days):
            day_dt = (window_start + timedelta(days=d)).strftime("%Y-%m-%d")
            inc_c = daily_inc_map.get(day_dt, 0)
            fb_c = daily_fb_map.get(day_dt, 0)
            esc_c = daily_esc_map.get(day_dt, 0)
            daily_exposure = total_exposure / time_window_days if time_window_days > 0 else 1.0
            norm_r = round((inc_c / daily_exposure) * 1000.0, 4) if daily_exposure > 0 else 0.0
            daily_trends.append(DailyTrendItem(
                date=day_dt,
                feedback_volume=fb_c,
                incident_count=inc_c,
                escalated_count=esc_c,
                normalized_rate=norm_r,
            ))

        return StoreSummaryAnalytics(
            store_id=target_store.id if target_store else None,
            store_name=target_store.name if target_store else "All Stores Consolidated",
            time_window_days=time_window_days,
            total_feedback_volume=total_feedback,
            total_distinct_incidents=distinct_incidents,
            duplicate_feedback_count=duplicate_count,
            deduplication_ratio=dedup_ratio,
            open_incidents=open_count,
            under_investigation_incidents=investigating_count,
            resolved_incidents=resolved_count,
            safety_escalations=safety_count,
            allergen_escalations=allergen_count,
            active_alerts_count=active_alerts,
            exposure_metric=exposure_metric,
            total_exposure=round(total_exposure, 1),
            overall_normalized_rate=overall_normalized_rate,
            sample_size_confidence=sample_conf,
            by_category=by_category,
            by_severity=by_severity,
            daily_trends=daily_trends,
        )

    @classmethod
    def get_store_comparisons(
        cls,
        db: Session,
        time_window_days: int = 30,
    ) -> List[StoreComparisonItem]:
        """
        Compare stores using normalized rates to prevent unfair raw volume comparisons
        between stores of different sizes.
        """
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(days=time_window_days)

        stores = db.query(Store).filter(Store.is_active == True).all()
        comparisons: List[StoreComparisonItem] = []

        for store in stores:
            # Feedback volume
            fb_count = (
                db.query(func.count(FeedbackRecord.id))
                .filter(
                    FeedbackRecord.store_id == store.id,
                    FeedbackRecord.event_timestamp >= window_start,
                )
                .scalar() or 0
            )

            # Distinct incidents
            inc_count = (
                db.query(func.count(Incident.id))
                .filter(
                    Incident.store_id == store.id,
                    Incident.first_seen_at >= window_start,
                )
                .scalar() or 0
            )

            # Safety escalations
            safety_count = (
                db.query(func.count(Incident.id))
                .filter(
                    Incident.store_id == store.id,
                    Incident.safety_flag == True,
                    Incident.first_seen_at >= window_start,
                )
                .scalar() or 0
            )

            # Active alerts
            alert_count = (
                db.query(func.count(Alert.id))
                .filter(
                    Alert.store_id == store.id,
                    Alert.status == AlertStatus.ACTIVE,
                )
                .scalar() or 0
            )

            # Exposure calculation
            exposure_type = "transactions"
            daily_tx = store.avg_daily_transactions
            if daily_tx and daily_tx > 0:
                exposure_vol = daily_tx * time_window_days
            else:
                exposure_type = "size_sqft"
                exposure_vol = store.size_sqft

            norm_rate = round((inc_count / exposure_vol) * 1000.0, 4) if exposure_vol > 0 else 0.0

            comparisons.append(StoreComparisonItem(
                store_id=store.id,
                store_number=store.store_number,
                store_name=store.name,
                exposure_type=exposure_type,
                exposure_volume=round(exposure_vol, 1),
                total_feedback=fb_count,
                distinct_incidents=inc_count,
                duplicate_count=max(0, fb_count - inc_count),
                normalized_rate=norm_rate,
                safety_escalations=safety_count,
                active_alerts=alert_count,
            ))

        # Sort stores by normalized rate descending
        comparisons.sort(key=lambda s: s.normalized_rate, reverse=True)
        return comparisons


# Singleton instance
analytics_service = AnalyticsService()
