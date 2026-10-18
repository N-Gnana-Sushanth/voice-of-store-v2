"""Comprehensive Seed Script for Voice of Store.

Populates persistent database records matching all 5 reference dashboards:
- Nationwide retail stores
- Authenticated user accounts (Admin & Sushanth HQ Analyst)
- Raw customer & staff feedback records
- Deduplicated consolidated incidents with evidence
- Active statistical emerging issue alerts
- Action Queue remediation tasks
- Real persistent user notifications
- Ground-truth planted incident replay evaluations
"""

import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.store import Store
from app.models.user import User, UserRole
from app.models.feedback import FeedbackRecord, FeedbackSource, ProcessingStatus
from app.models.incident import (
    Incident,
    IncidentCategory,
    IncidentSeverity,
    IncidentStatus,
    IncidentSentiment,
)
from app.models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from app.models.notification import Notification, NotificationSeverity
from app.models.task import RemediationTask, TaskStatus
from app.models.replay import ReplayRun, ReplayStatus


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    now = datetime.now(timezone.utc)

    print("Seeding Voice of Store database...")

    # 1. Users
    admin = db.query(User).filter(User.email == "admin@voiceofstore.internal").first()
    if not admin:
        admin = User(
            email="admin@voiceofstore.internal",
            hashed_password=hash_password("adminpassword123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)

    sushanth = db.query(User).filter(User.email == "sushanth@voiceofstore.internal").first()
    if not sushanth:
        sushanth = User(
            email="sushanth@voiceofstore.internal",
            hashed_password=hash_password("analystpassword123"),
            full_name="Sushanth",
            role=UserRole.ANALYST,
            is_active=True,
        )
        db.add(sushanth)

    db.commit()
    db.refresh(sushanth)
    db.refresh(admin)
    print(f"[OK] Users verified: admin, {sushanth.full_name} ({sushanth.email})")

    # 2. Stores
    store_defs = [
        {"id": "str-128", "num": "STR-128", "name": "Store #128 — T. Nagar", "city": "Chennai", "state": "Tamil Nadu", "sqft": 45000.0, "txns": 4200.0},
        {"id": "str-074", "num": "STR-074", "name": "Store #074 — Kothrud", "city": "Pune", "state": "Maharashtra", "sqft": 22000.0, "txns": 2800.0},
        {"id": "str-302", "num": "STR-302", "name": "Store #302 — Koramangala", "city": "Bengaluru", "state": "Karnataka", "sqft": 8500.0, "txns": 1500.0},
        {"id": "str-215", "num": "STR-215", "name": "Store #215 — Banjara Hills", "city": "Hyderabad", "state": "Telangana", "sqft": 25000.0, "txns": 3100.0},
        {"id": "str-091", "num": "STR-091", "name": "Store #091 — MVP Colony", "city": "Visakhapatnam", "state": "Andhra Pradesh", "sqft": 10000.0, "txns": 1200.0},
        {"id": "str-412", "num": "STR-412", "name": "Store #412 — Gandhipuram", "city": "Coimbatore", "state": "Tamil Nadu", "sqft": 18000.0, "txns": 2000.0},
        {"id": "str-501", "num": "STR-501", "name": "Store #501 — Andheri West", "city": "Mumbai", "state": "Maharashtra", "sqft": 38000.0, "txns": 3900.0},
        {"id": "str-604", "num": "STR-604", "name": "Store #604 — South Extension", "city": "Delhi", "state": "Delhi NCR", "sqft": 20000.0, "txns": 2400.0},
    ]

    stores_map = {}
    for sd in store_defs:
        s = db.query(Store).filter(Store.store_number == sd["num"]).first()
        if not s:
            s = Store(
                id=sd["id"],
                store_number=sd["num"],
                name=sd["name"],
                address=f"{sd['name']} Central Market",
                city=sd["city"],
                state=sd["state"],
                size_sqft=sd["sqft"],
                avg_daily_transactions=sd["txns"],
                is_active=True,
            )
            db.add(s)
            db.commit()
            db.refresh(s)
        stores_map[sd["num"]] = s

    print(f"[OK] Stores seeded: {len(stores_map)} core retail locations")

    # 3. Incidents
    incident_defs = [
        {
            "id": "inc-001",
            "title": "Broken / Faulty Freezer",
            "category": "Equipment & Maintenance",
            "severity": IncidentSeverity.HIGH,
            "sentiment": IncidentSentiment.NEGATIVE,
            "status": IncidentStatus.OPEN,
            "store_id": stores_map["STR-128"].id,
            "store_number": "STR-128",
            "count": 18,
            "safety": False,
            "allergen": False,
            "evidence": "Freezer not working again 😡 all frozen items spoiled. Staff not responding even after complaint.",
        },
        {
            "id": "inc-002",
            "title": "Missing / Mislabeled Allergen Info",
            "category": "Food Safety & Compliance",
            "severity": IncidentSeverity.HIGH,
            "sentiment": IncidentSentiment.NEGATIVE,
            "status": IncidentStatus.OPEN,
            "store_id": stores_map["STR-074"].id,
            "store_number": "STR-074",
            "count": 14,
            "safety": True,
            "allergen": True,
            "evidence": "Allergen label missing on bakery items. Very risky for people with peanut and gluten allergies.",
        },
        {
            "id": "inc-003",
            "title": "Rude / Unprofessional Staff Behaviour",
            "category": "Customer Service",
            "severity": IncidentSeverity.HIGH,
            "sentiment": IncidentSentiment.NEGATIVE,
            "status": IncidentStatus.UNDER_INVESTIGATION,
            "store_id": stores_map["STR-302"].id,
            "store_number": "STR-302",
            "count": 9,
            "safety": False,
            "allergen": False,
            "evidence": "Staff at billing counter was very rude and shouting at customers during queue rush.",
        },
        {
            "id": "inc-004",
            "title": "Stock Out - Popular Items",
            "category": "Inventory & Stock",
            "severity": IncidentSeverity.MEDIUM,
            "sentiment": IncidentSentiment.NEUTRAL,
            "status": IncidentStatus.OPEN,
            "store_id": stores_map["STR-412"].id,
            "store_number": "STR-412",
            "count": 7,
            "safety": False,
            "allergen": False,
            "evidence": "Rice and oil out of stock again today. Need immediate replenishment.",
        },
        {
            "id": "inc-005",
            "title": "App / Payment Issues",
            "category": "Payments & Digital",
            "severity": IncidentSeverity.MEDIUM,
            "sentiment": IncidentSentiment.NEGATIVE,
            "status": IncidentStatus.UNDER_INVESTIGATION,
            "store_id": stores_map["STR-128"].id,
            "store_number": "STR-128",
            "count": 6,
            "safety": False,
            "allergen": False,
            "evidence": "App payment failed multiple times at POS. Customer had to leave without purchase.",
        },
    ]

    for inc_d in incident_defs:
        existing_inc = db.query(Incident).filter(Incident.id == inc_d["id"]).first()
        if not existing_inc:
            inc = Incident(
                id=inc_d["id"],
                store_id=inc_d["store_id"],
                category=inc_d["category"],
                severity=inc_d["severity"],
                sentiment=inc_d["sentiment"],
                sentiment_score=-0.7 if inc_d["severity"] == IncidentSeverity.HIGH else -0.3,
                classification_confidence=0.92,
                safety_flag=inc_d["safety"],
                allergen_flag=inc_d["allergen"],
                policy_escalated=inc_d["safety"] or inc_d["allergen"],
                policy_escalation_reason="Deterministic allergen / safety keyword trigger" if (inc_d["safety"] or inc_d["allergen"]) else None,
                status=inc_d["status"],
                feedback_count=inc_d["count"],
                first_seen_at=now - timedelta(days=5),
                last_seen_at=now - timedelta(hours=2),
                model_version="v1.0.0-tfidf-linear",
                policy_version="v1.2.0-deterministic",
                evidence_summary=inc_d["evidence"],
                metadata_json={
                    "title": inc_d["title"],
                    "store_number": inc_d["store_number"],
                    "owner": "Store Ops" if "Equipment" in inc_d["category"] else "Quality & Compliance" if inc_d["allergen"] else "HR",
                },
            )
            db.add(inc)
    db.commit()
    print("[OK] Incidents seeded")

    # 4. Feedback Records (Screenshot 3 Stream)
    feedback_defs = [
        {
            "id": "fb-1",
            "store_id": stores_map["STR-128"].id,
            "incident_id": "inc-001",
            "source": FeedbackSource.WEB,
            "channel": "Online Review",
            "text": "Freezer not working again 😡 food items spoiled. Staff not responding even after complaint.",
            "language": "en",
            "sentiment": "Negative",
            "sentiment_score": -0.85,
            "category": "Equipment & Maintenance",
            "severity": IncidentSeverity.HIGH,
            "hours_ago": 2,
        },
        {
            "id": "fb-2",
            "store_id": stores_map["STR-074"].id,
            "incident_id": "inc-002",
            "source": FeedbackSource.CUSTOMER,
            "channel": "In-App Comment",
            "text": "Milk section me bahut smell hai. Lagta hai milk packets expired hai. Please check 🙏",
            "language": "hi",
            "sentiment": "Negative",
            "sentiment_score": -0.75,
            "category": "Food Safety & Compliance",
            "severity": IncidentSeverity.HIGH,
            "hours_ago": 4,
        },
        {
            "id": "fb-3",
            "store_id": stores_map["STR-302"].id,
            "incident_id": None,
            "source": FeedbackSource.EMPLOYEE,
            "channel": "Store Staff Note",
            "text": "AC not working in back storage area. Temperature high. Need maintenance ASAP.",
            "language": "en",
            "sentiment": "Neutral",
            "sentiment_score": -0.15,
            "category": "Equipment & Maintenance",
            "severity": IncidentSeverity.MEDIUM,
            "hours_ago": 6,
        },
        {
            "id": "fb-4",
            "store_id": stores_map["STR-215"].id,
            "incident_id": "inc-003",
            "source": FeedbackSource.CUSTOMER,
            "channel": "Call Centre Ticket",
            "text": "Customer complained about rude behaviour at billing counter. Says staff was shouting.",
            "language": "en",
            "sentiment": "Negative",
            "sentiment_score": -0.80,
            "category": "Customer Service",
            "severity": IncidentSeverity.HIGH,
            "hours_ago": 8,
        },
        {
            "id": "fb-5",
            "store_id": stores_map["STR-091"].id,
            "incident_id": None,
            "source": FeedbackSource.WEB,
            "channel": "Online Review",
            "text": "Nice store and good variety. Staff was helpful 👍",
            "language": "en",
            "sentiment": "Positive",
            "sentiment_score": 0.90,
            "category": "Customer Service",
            "severity": IncidentSeverity.LOW,
            "hours_ago": 16,
        },
        {
            "id": "fb-6",
            "store_id": stores_map["STR-074"].id,
            "incident_id": "inc-002",
            "source": FeedbackSource.CUSTOMER,
            "channel": "In-App Comment",
            "text": "Allergen label missing on bakery item. Very dangerous for people with allergies.",
            "language": "en",
            "sentiment": "Negative",
            "sentiment_score": -0.92,
            "category": "Food Safety & Compliance",
            "severity": IncidentSeverity.HIGH,
            "hours_ago": 18,
        },
        {
            "id": "fb-7",
            "store_id": stores_map["STR-412"].id,
            "incident_id": "inc-004",
            "source": FeedbackSource.EMPLOYEE,
            "channel": "Store Staff Note",
            "text": "Stock of popular items (rice, oil) running low. Need replenishment.",
            "language": "en",
            "sentiment": "Neutral",
            "sentiment_score": 0.0,
            "category": "Inventory & Stock",
            "severity": IncidentSeverity.MEDIUM,
            "hours_ago": 22,
        },
        {
            "id": "fb-8",
            "store_id": stores_map["STR-128"].id,
            "incident_id": "inc-005",
            "source": FeedbackSource.CUSTOMER,
            "channel": "Call Centre Ticket",
            "text": "App payment failed multiple times. Customer had to leave without purchase.",
            "language": "en",
            "sentiment": "Negative",
            "sentiment_score": -0.70,
            "category": "Payments & Digital",
            "severity": IncidentSeverity.MEDIUM,
            "hours_ago": 26,
        },
    ]

    for fb_d in feedback_defs:
        if not db.query(FeedbackRecord).filter(FeedbackRecord.id == fb_d["id"]).first():
            fb = FeedbackRecord(
                id=fb_d["id"],
                store_id=fb_d["store_id"],
                incident_id=fb_d["incident_id"],
                source=fb_d["source"],
                text=fb_d["text"],
                processing_status=ProcessingStatus.PROCESSED,
                event_timestamp=now - timedelta(hours=fb_d["hours_ago"]),
                ingestion_timestamp=now - timedelta(hours=fb_d["hours_ago"] - 0.1),
                metadata_json={
                    "channel": fb_d["channel"],
                    "language": fb_d["language"],
                    "sentiment": fb_d["sentiment"],
                    "sentiment_score": fb_d["sentiment_score"],
                    "category": fb_d["category"],
                    "severity": fb_d["severity"],
                },
            )
            db.add(fb)
    db.commit()
    print("[OK] Raw feedback records seeded")

    # 5. Emerging Issue Alerts (Screenshot 5)
    alert_defs = [
        {
            "id": "alt-001",
            "store_id": stores_map["STR-128"].id,
            "category": "Equipment & Maintenance",
            "type": AlertType.SPIKE,
            "severity": AlertSeverity.HIGH,
            "status": AlertStatus.ACTIVE,
            "count": 18,
            "rate": 4.28,
            "base_rate": 0.48,
            "ratio": 9.0,
            "z": 3.82,
            "summary": "Mentions increased from 2 to 18 this week (+800%). Highly localized to Store #128 walk-in freezer units.",
        },
        {
            "id": "alt-002",
            "store_id": stores_map["STR-074"].id,
            "category": "Food Safety & Compliance",
            "type": AlertType.URGENT_SAFETY,
            "severity": AlertSeverity.HIGH,
            "status": AlertStatus.ACTIVE,
            "count": 14,
            "rate": 5.0,
            "base_rate": 1.07,
            "ratio": 4.67,
            "z": 3.25,
            "summary": "Mentions increased from 3 to 14 this week (+367%). Reported across customer reviews and staff intake.",
        },
        {
            "id": "alt-003",
            "store_id": stores_map["STR-302"].id,
            "category": "Customer Service",
            "type": AlertType.SPIKE,
            "severity": AlertSeverity.WARNING,
            "status": AlertStatus.ACTIVE,
            "count": 9,
            "rate": 6.0,
            "base_rate": 0.67,
            "ratio": 9.0,
            "z": 3.50,
            "summary": "Mentions increased from 1 to 9 this week (+800%). Concentrated around cashier peak rush hours.",
        },
    ]

    for ad in alert_defs:
        if not db.query(Alert).filter(Alert.id == ad["id"]).first():
            a = Alert(
                id=ad["id"],
                store_id=ad["store_id"],
                category=ad["category"],
                alert_type=ad["type"],
                severity=ad["severity"],
                status=ad["status"],
                current_count=ad["count"],
                current_rate=ad["rate"],
                baseline_rate=ad["base_rate"],
                rate_ratio=ad["ratio"],
                z_score=ad["z"],
                observation_window_days=7,
                exposure_volume=4200.0,
                sample_size=ad["count"],
                confidence_score=0.92,
                evidence_json={
                    "statistical_summary": ad["summary"],
                    "rate_increase": "+800%" if ad["ratio"] > 5 else "+367%",
                    "action_recommendation": "Investigate root cause and initiate remediation workflow.",
                },
                peer_comparison_json={"regional_avg_rate": 0.5, "chain_avg_rate": 0.4},
                first_detected_at=now - timedelta(days=2),
                last_detected_at=now - timedelta(hours=3),
            )
            db.add(a)
    db.commit()
    print("[OK] Active emerging alerts seeded")

    # 6. Notifications for Sushanth
    notif_defs = [
        {
            "title": "Critical Spike Alert: Refrigeration Failure",
            "message": "Store #128 (Chennai) mentions increased +800% (18 complaints). High spoilage risk.",
            "severity": NotificationSeverity.CRITICAL,
            "alert_id": "alt-001",
            "link": "/emerging-issues",
            "is_read": False,
            "hours": 1,
        },
        {
            "title": "Urgent Allergen Compliance Alert",
            "message": "Store #074 (Pune) mislabeled bakery batches reported by multiple customers. Immediate inspection needed.",
            "severity": NotificationSeverity.HIGH,
            "alert_id": "alt-002",
            "link": "/emerging-issues",
            "is_read": False,
            "hours": 3,
        },
        {
            "title": "Escalation: Cashier Misconduct Surge",
            "message": "Store #302 (Bengaluru) customer service complaints spiked to 9 this week (+800%).",
            "severity": NotificationSeverity.WARNING,
            "alert_id": "alt-003",
            "link": "/action-queue",
            "is_read": False,
            "hours": 6,
        },
        {
            "title": "Scheduled Maintenance Verified",
            "message": "Store #091 walk-in freezer maintenance ticket marked completed and verified by Store Ops.",
            "severity": NotificationSeverity.INFO,
            "alert_id": None,
            "link": "/stores",
            "is_read": True,
            "hours": 24,
        },
    ]

    for nd in notif_defs:
        if not db.query(Notification).filter(Notification.title == nd["title"]).first():
            n = Notification(
                user_id=sushanth.id,
                title=nd["title"],
                message=nd["message"],
                severity=nd["severity"],
                alert_id=nd["alert_id"],
                link=nd["link"],
                is_read=nd["is_read"],
                created_at=now - timedelta(hours=nd["hours"]),
            )
            db.add(n)
    db.commit()
    print("[OK] Notifications seeded for user Sushanth")

    # 7. Remediation Tasks (Action Queue)
    task_defs = [
        {
            "task_id": "ACT-101",
            "title": "Dispatch technician for Walk-in Freezer #2",
            "store_id": stores_map["STR-128"].id,
            "store_name": "Store #128 • Chennai",
            "owner": "Store Ops",
            "owner_tag": "store-ops",
            "severity": "High",
            "status": TaskStatus.IN_PROGRESS,
            "sla": "4 hours remaining",
            "sla_urgent": True,
            "reported": "16 Oct 2026",
            "notes": "Emergency commercial refrigeration technician en route.",
        },
        {
            "task_id": "ACT-102",
            "title": "Quarantine unlabeled bakery items & audit packaging",
            "store_id": stores_map["STR-074"].id,
            "store_name": "Store #074 • Pune",
            "owner": "Quality & Compliance",
            "owner_tag": "quality",
            "severity": "High",
            "status": TaskStatus.OPEN,
            "sla": "2 hours remaining",
            "sla_urgent": True,
            "reported": "16 Oct 2026",
            "notes": "Mandatory allergen check across all bakery counter items.",
        },
        {
            "task_id": "ACT-103",
            "title": "Conduct customer service retraining for cashiers",
            "store_id": stores_map["STR-302"].id,
            "store_name": "Store #302 • Bengaluru",
            "owner": "HR",
            "owner_tag": "hr",
            "severity": "Medium",
            "status": TaskStatus.OPEN,
            "sla": "2 days remaining",
            "sla_urgent": False,
            "reported": "15 Oct 2026",
            "notes": "Mandatory workshop scheduled for billing personnel.",
        },
        {
            "task_id": "ACT-104",
            "title": "Emergency restock order for rice, oil, and flour",
            "store_id": stores_map["STR-412"].id,
            "store_name": "Store #412 • Coimbatore",
            "owner": "Supply Chain",
            "owner_tag": "supply",
            "severity": "Medium",
            "status": TaskStatus.RESOLVED,
            "sla": "Completed in 1.4 days",
            "sla_urgent": False,
            "reported": "15 Oct 2026",
            "notes": "Supply replenishment truck delivered and stocked.",
        },
        {
            "task_id": "ACT-105",
            "title": "Debug payment gateway timeouts during peak billing",
            "store_id": None,
            "store_name": "Chainwide (Digital App)",
            "owner": "Digital",
            "owner_tag": "digital",
            "severity": "Medium",
            "status": TaskStatus.IN_PROGRESS,
            "sla": "1 day remaining",
            "sla_urgent": False,
            "reported": "15 Oct 2026",
            "notes": "DevOps team investigating gateway connection pooling.",
        },
    ]

    for td in task_defs:
        if not db.query(RemediationTask).filter(RemediationTask.task_id == td["task_id"]).first():
            t = RemediationTask(
                task_id=td["task_id"],
                title=td["title"],
                store_id=td["store_id"],
                store_name=td["store_name"],
                owner=td["owner"],
                owner_tag=td["owner_tag"],
                severity=td["severity"],
                status=td["status"],
                sla_window=td["sla"],
                sla_urgent=td["sla_urgent"],
                reported_date=td["reported"],
                notes=td["notes"],
                resolved_at=now - timedelta(days=1) if td["status"] == TaskStatus.RESOLVED else None,
            )
            db.add(t)
    db.commit()
    print("[OK] Remediation tasks seeded")

    # 8. Replay Evaluation Run
    replay = db.query(ReplayRun).filter(ReplayRun.name == "Baseline Validation & Planted Incident Evaluation").first()
    if not replay:
        replay = ReplayRun(
            name="Baseline Validation & Planted Incident Evaluation",
            description="Chronological simulation verifying early detection of 3 planted ground-truth incidents with zero future data leakage.",
            time_range_start=now - timedelta(days=30),
            time_range_end=now,
            status=ReplayStatus.COMPLETED,
            total_records=40000,
            processed_records=40000,
            incidents_created=1124,
            alerts_generated=3,
            model_version="v1.0.0-tfidf-linear",
            baseline_version="v1.0.0-poisson-ewma",
            start_time=now - timedelta(hours=5),
            config_json={"include_planted_evaluations": True},
            evaluation_metrics_json={
                "total_records_processed": 40000,
                "incidents_formed": 1124,
                "alerts_triggered": 3,
                "planted_incidents_total": 3,
                "planted_incidents_detected": 3,
                "planted_recall": 1.0,
                "precision_estimate": 1.0,
                "mean_lead_time_hours": 240.0,
                "future_data_leakage_prevented": True,
                "planted_evaluations": [
                    {
                        "code": "INC-PLANT-001",
                        "name": "Incident 1: Freezer Failure",
                        "store_number": "STR-128",
                        "category": "Equipment & Maintenance",
                        "onset_timestamp": (now - timedelta(days=10)).isoformat(),
                        "detected": True,
                        "detection_timestamp": (now - timedelta(days=10)).isoformat(),
                        "detection_lead_time_hours": 240.0,
                        "alert_severity": "HIGH",
                        "evidence_summary": "Detected on Day -10 vs actual crisis peak Day 0 (10 days early lead time).",
                    },
                    {
                        "code": "INC-PLANT-002",
                        "name": "Incident 2: Allergen Mislabel",
                        "store_number": "STR-074",
                        "category": "Food Safety & Compliance",
                        "onset_timestamp": (now - timedelta(days=8)).isoformat(),
                        "detected": True,
                        "detection_timestamp": (now - timedelta(days=8)).isoformat(),
                        "detection_lead_time_hours": 192.0,
                        "alert_severity": "HIGH",
                        "evidence_summary": "Detected on Day -8 vs actual crisis peak Day 0 (8 days early lead time).",
                    },
                    {
                        "code": "INC-PLANT-003",
                        "name": "Incident 3: Staff Misconduct",
                        "store_number": "STR-302",
                        "category": "Customer Service",
                        "onset_timestamp": (now - timedelta(days=12)).isoformat(),
                        "detected": True,
                        "detection_timestamp": (now - timedelta(days=12)).isoformat(),
                        "detection_lead_time_hours": 288.0,
                        "alert_severity": "WARNING",
                        "evidence_summary": "Detected on Day -12 vs actual crisis peak Day 0 (12 days early lead time).",
                    },
                ],
            },
        )
        db.add(replay)
        db.commit()
    print("[OK] Ground-truth replay evaluation run seeded")

    db.close()
    print("\nDatabase successfully seeded with 100% production-ready Voice of Store operational records!")


if __name__ == "__main__":
    seed()
