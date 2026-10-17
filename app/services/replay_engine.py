"""Chronological Replay and Evaluation Engine.

Executes event-time simulations without future data leakage and measures
detection lead times, precision, and recall on synthetic ground-truth incidents.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
import uuid
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.models.alert import Alert, AlertStatus
from app.models.feedback import FeedbackRecord, FeedbackSource
from app.models.incident import IncidentCategory
from app.models.replay import ReplayRun, ReplayStatus
from app.models.store import Store
from app.schemas.feedback import FeedbackSubmitSingle
from app.schemas.replay import (
    PlantedIncidentEvaluation,
    ReplayEvaluationMetrics,
    ReplayRunCreate,
    ReplayRunResponse,
)
from app.services.emerging_detector import EmergingIssueDetector
from app.services.ingestion_service import IngestionService


# 3 Documented Synthetic Planted Ground-Truth Incidents for Evaluation
PLANTED_INCIDENTS_SPEC: List[Dict[str, Any]] = [
    {
        "code": "PLANTED-001",
        "name": "Deli Cross-Contamination and Walnut Allergen Outbreak",
        "store_number": "STORE-101",
        "category": IncidentCategory.ALLERGENS,
        "offset_days": 10,
        "records": [
            "Customer developed hives after eating roast beef sliced on same counter as walnut dessert.",
            "Severe allergic reaction to deli turkey! Employee used same knife that had peanut butter residue.",
            "Allergen warning missing on deli sandwich, child broke out in severe hives and had difficulty breathing.",
            "Deli slicer was not cleaned between nut-topped ham and allergen-free turkey sandwich.",
        ],
    },
    {
        "code": "PLANTED-002",
        "name": "POS Terminal Software Freeze and Double Billing Spike",
        "store_number": "STORE-102",
        "category": IncidentCategory.BILLING_PAYMENTS,
        "offset_days": 14,
        "records": [
            "Card reader froze at checkout and double charged my credit card for groceries.",
            "Self-checkout register charged my account twice and cashier was unable to void duplicate swipe.",
            "Credit card chip error charged me $142.50 twice on receipt at lane 4.",
            "POS system rebooted in middle of transaction and debit card was billed two times.",
            "Register scanner overcharged items and card machine displayed payment error but debited bank.",
        ],
    },
    {
        "code": "PLANTED-003",
        "name": "HVAC Ceiling Water Leak Slip-and-Fall Hazard",
        "store_number": "STORE-103",
        "category": IncidentCategory.SAFETY,
        "offset_days": 18,
        "records": [
            "Customer slipped and fell on large water puddle from ceiling leak in front of bakery.",
            "Water dripping from HVAC ceiling unit onto produce floor without caution cones, elderly customer fell down.",
            "Elderly lady slipped on wet floor near aisle 2 and hurt her hip, paramedics called.",
            "Ceiling leak created a slick puddle, customer slipped on water and nearly hit display shelf.",
        ],
    },
]


class ReplayEngine:
    """Manages strictly chronological event-time processing and evaluation."""

    def __init__(self, observation_window_days: int = 7, baseline_window_days: int = 14):
        self.obs_window_days = observation_window_days
        self.base_window_days = baseline_window_days

    @classmethod
    def generate_synthetic_replay_dataset(
        cls,
        base_start_time: datetime,
        stores: List[Store],
    ) -> List[Dict[str, Any]]:
        """
        Generate chronological sequence of normal background store feedback
        interleaved with the 3 synthetic planted ground-truth incidents.
        """
        dataset: List[Dict[str, Any]] = []

        # Background noise examples across stores
        background_samples = [
            ("Produce section was clean and staff was polite.", IncidentCategory.CUSTOMER_SERVICE, 0),
            ("Floor in aisle 3 was clean and well kept.", IncidentCategory.CLEANLINESS_HYGIENE, 0),
            ("Could not find brand of whole wheat bread on shelf.", IncidentCategory.INVENTORY_AVAILABILITY, 0),
            ("Strawberries were fresh and tasted sweet.", IncidentCategory.PRODUCT_FOOD_QUALITY, 0),
            ("Fast checkout at register 2.", IncidentCategory.CUSTOMER_SERVICE, 0),
            ("Prices matched the advertised sales tag on shelf.", IncidentCategory.BILLING_PAYMENTS, 0),
            ("Store associate assisted me with heavy pet food bag.", IncidentCategory.CUSTOMER_SERVICE, 0),
        ]

        # 1. Generate 25 days of normal baseline noise across stores
        for day in range(25):
            day_dt = base_start_time + timedelta(days=day)
            for s_idx, store in enumerate(stores):
                # 2-3 feedback records per store per day
                for rec_idx in range(2):
                    sample_text, cat, _ = background_samples[(day * 3 + s_idx + rec_idx) % len(background_samples)]
                    event_dt = day_dt + timedelta(hours=8 + (rec_idx * 4), minutes=15 * s_idx)
                    dataset.append({
                        "id": str(uuid.uuid4()),
                        "store_id": store.id,
                        "store_number": store.store_number,
                        "text": sample_text,
                        "event_timestamp": event_dt,
                        "is_planted": False,
                        "planted_code": None,
                    })

        # 2. Inject the 3 Planted Incidents with known onset times
        store_map = {s.store_number: s for s in stores}
        for planted in PLANTED_INCIDENTS_SPEC:
            s_num = planted["store_number"]
            store = store_map.get(s_num)
            if not store:
                continue

            onset_time = base_start_time + timedelta(days=planted["offset_days"], hours=10)
            for i, text in enumerate(planted["records"]):
                event_dt = onset_time + timedelta(hours=i * 5, minutes=10)
                dataset.append({
                    "id": str(uuid.uuid4()),
                    "store_id": store.id,
                    "store_number": store.store_number,
                    "text": text,
                    "event_timestamp": event_dt,
                    "is_planted": True,
                    "planted_code": planted["code"],
                })

        # 3. Sort chronologically by (event_timestamp, id) for deterministic sequence
        dataset.sort(key=lambda x: (x["event_timestamp"], x["id"]))
        return dataset

    def run_replay(
        self,
        db: Session,
        create_params: ReplayRunCreate,
    ) -> ReplayRunResponse:
        """
        Execute chronological replay simulation.
        Step through records in strict event-time order with tie-breaking.
        Baselines are calculated strictly at simulated time without future data leakage.
        """
        run_id = str(uuid.uuid4())
        start_exec_time = datetime.now(timezone.utc)

        replay_record = ReplayRun(
            id=run_id,
            name=create_params.name,
            description=create_params.description,
            time_range_start=create_params.time_range_start,
            time_range_end=create_params.time_range_end,
            status=ReplayStatus.RUNNING,
            config_json={
                "obs_window_days": self.obs_window_days,
                "base_window_days": self.base_window_days,
                "planted_evaluation": create_params.include_planted_evaluations,
            },
            model_version=settings.MODEL_VERSION,
            baseline_version=settings.POLICY_VERSION,
            start_time=start_exec_time,
        )
        db.add(replay_record)
        db.commit()

        # Ensure demo stores exist
        stores = db.query(Store).filter(Store.is_active == True).all()
        if not stores:
            # Create evaluation stores if empty
            stores = [
                Store(id=str(uuid.uuid4()), store_number="STORE-101", name="Downtown Grocery 101", size_sqft=15000, avg_daily_transactions=2500),
                Store(id=str(uuid.uuid4()), store_number="STORE-102", name="Westside Market 102", size_sqft=12000, avg_daily_transactions=2000),
                Store(id=str(uuid.uuid4()), store_number="STORE-103", name="Uptown Express 103", size_sqft=8000, avg_daily_transactions=1500),
            ]
            db.add_all(stores)
            db.commit()

        # Generate deterministic synthetic event dataset
        dataset = self.generate_synthetic_replay_dataset(
            base_start_time=create_params.time_range_start,
            stores=stores,
        )

        detector = EmergingIssueDetector(
            observation_window_days=self.obs_window_days,
            baseline_window_days=self.base_window_days,
            min_current_count=2,
            rate_ratio_threshold=1.8,
            z_score_threshold=1.5,
        )

        detector_alerts: List[Alert] = []
        planted_evaluations: List[PlantedIncidentEvaluation] = []
        planted_detections: Dict[str, Tuple[datetime, str, str]] = {}

        # Track planted ground-truth metadata
        planted_onsets: Dict[str, datetime] = {}
        for p in PLANTED_INCIDENTS_SPEC:
            planted_onsets[p["code"]] = create_params.time_range_start + timedelta(days=p["offset_days"], hours=10)

        # Ingest records in strict event-time order
        processed_count = 0
        incidents_created = 0

        for record in dataset:
            simulated_time: datetime = record["event_timestamp"]
            if simulated_time > create_params.time_range_end:
                break

            processed_count += 1

            # Ingest single feedback
            sub = FeedbackSubmitSingle(
                store_id=record["store_id"],
                text=record["text"],
                source=FeedbackSource.CUSTOMER,
                event_timestamp=simulated_time,
                idempotency_key=f"replay-{run_id}-{record['id']}",
            )

            fb, inc, status = IngestionService.ingest_single(db, sub)
            if status == "SUCCESS" and inc:
                incidents_created += 1

            # Periodic scan for emerging issues as of simulated_time
            # Evaluates baselines ONLY using data prior to simulated_time
            if processed_count % 3 == 0:
                alerts = detector.scan_for_emerging_issues(
                    db=db,
                    store_id=record["store_id"],
                    as_of_time=simulated_time,
                )
                for alert in alerts:
                    detector_alerts.append(alert)
                    # Check if this alert corresponds to any planted incident
                    for p in PLANTED_INCIDENTS_SPEC:
                        p_code = p["code"]
                        if (
                            p_code not in planted_detections
                            and alert.category == p["category"]
                            and simulated_time >= planted_onsets[p_code]
                        ):
                            lead_time = (simulated_time - planted_onsets[p_code]).total_seconds() / 3600.0
                            planted_detections[p_code] = (
                                simulated_time,
                                alert.severity,
                                f"Detected after {lead_time:.1f} hours from onset with rate {alert.current_rate:.2f}/1k.",
                            )

        # Build Planted Evaluations
        lead_times: List[float] = []
        for p in PLANTED_INCIDENTS_SPEC:
            code = p["code"]
            onset = planted_onsets[code]
            if code in planted_detections:
                det_time, sev, evidence = planted_detections[code]
                lead_h = max(0.0, (det_time - onset).total_seconds() / 3600.0)
                lead_times.append(lead_h)
                planted_evaluations.append(PlantedIncidentEvaluation(
                    code=code,
                    name=p["name"],
                    store_number=p["store_number"],
                    category=p["category"],
                    onset_timestamp=onset,
                    detected=True,
                    detection_timestamp=det_time,
                    detection_lead_time_hours=round(lead_h, 2),
                    alert_severity=sev,
                    evidence_summary=evidence,
                ))
            else:
                planted_evaluations.append(PlantedIncidentEvaluation(
                    code=code,
                    name=p["name"],
                    store_number=p["store_number"],
                    category=p["category"],
                    onset_timestamp=onset,
                    detected=False,
                    detection_timestamp=None,
                    detection_lead_time_hours=None,
                    alert_severity=None,
                    evidence_summary="Not detected within simulation window.",
                ))

        detected_count = sum(1 for e in planted_evaluations if e.detected)
        total_planted = len(PLANTED_INCIDENTS_SPEC)
        recall = round(detected_count / total_planted, 4) if total_planted > 0 else 0.0

        distinct_alert_keys = {f"{a.store_id}:{a.category}" for a in detector_alerts}
        total_distinct_alerts = len(distinct_alert_keys)
        # False positives: alerts on categories other than the 3 planted issues
        false_positives = max(0, total_distinct_alerts - detected_count)
        precision = round(detected_count / total_distinct_alerts, 4) if total_distinct_alerts > 0 else 1.0

        mean_lead = round(sum(lead_times) / len(lead_times), 2) if lead_times else None

        metrics = ReplayEvaluationMetrics(
            total_records_processed=processed_count,
            incidents_formed=incidents_created,
            alerts_triggered=total_distinct_alerts,
            planted_incidents_total=total_planted,
            planted_incidents_detected=detected_count,
            planted_recall=recall,
            precision_estimate=precision,
            mean_lead_time_hours=mean_lead,
            future_data_leakage_prevented=True,
            planted_evaluations=planted_evaluations,
        )

        completion_time = datetime.now(timezone.utc)
        replay_record.status = ReplayStatus.COMPLETED
        replay_record.total_records = len(dataset)
        replay_record.processed_records = processed_count
        replay_record.incidents_created = incidents_created
        replay_record.alerts_generated = total_distinct_alerts
        replay_record.evaluation_metrics_json = metrics.model_dump(mode="json")
        replay_record.completion_time = completion_time
        db.commit()

        return ReplayRunResponse(
            id=replay_record.id,
            name=replay_record.name,
            description=replay_record.description,
            time_range_start=replay_record.time_range_start,
            time_range_end=replay_record.time_range_end,
            status=replay_record.status,
            total_records=replay_record.total_records,
            processed_records=replay_record.processed_records,
            incidents_created=replay_record.incidents_created,
            alerts_generated=replay_record.alerts_generated,
            evaluation_metrics=metrics,
            model_version=replay_record.model_version,
            baseline_version=replay_record.baseline_version,
            start_time=replay_record.start_time,
            completion_time=replay_record.completion_time,
            created_at=replay_record.created_at,
        )


# Singleton instance
replay_engine = ReplayEngine()
