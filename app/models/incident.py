"""Incident ORM model representing consolidated issues."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class IncidentCategory:
    CUSTOMER_SERVICE = "Customer service"
    CLEANLINESS_HYGIENE = "Cleanliness and hygiene"
    INVENTORY_AVAILABILITY = "Inventory and product availability"
    PRODUCT_FOOD_QUALITY = "Product or food quality"
    SAFETY = "Safety"
    ALLERGENS = "Allergens"
    BILLING_PAYMENTS = "Billing and payments"
    STAFF_BEHAVIOR = "Staff behavior"
    OTHER_UNKNOWN = "Other or unknown"

    ALL = [
        CUSTOMER_SERVICE,
        CLEANLINESS_HYGIENE,
        INVENTORY_AVAILABILITY,
        PRODUCT_FOOD_QUALITY,
        SAFETY,
        ALLERGENS,
        BILLING_PAYMENTS,
        STAFF_BEHAVIOR,
        OTHER_UNKNOWN,
    ]


class IncidentSeverity:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    ALL = [LOW, MEDIUM, HIGH, CRITICAL]


class IncidentStatus:
    OPEN = "OPEN"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"

    ALL = [OPEN, UNDER_INVESTIGATION, RESOLVED, DISMISSED]


class IncidentSentiment:
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"

    ALL = [POSITIVE, NEUTRAL, NEGATIVE]


class OwningFunction:
    STORE_OPS = "Store Ops"
    SUPPLY_CHAIN = "Supply Chain"
    MERCHANDISING = "Merchandising"
    DIGITAL = "Digital"
    HR = "HR"
    QUALITY_COMPLIANCE = "Quality & Compliance"

    ALL = [STORE_OPS, SUPPLY_CHAIN, MERCHANDISING, DIGITAL, HR, QUALITY_COMPLIANCE]


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id = Column(String(36), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    severity = Column(String(50), nullable=False, default=IncidentSeverity.MEDIUM, index=True)
    sentiment = Column(String(50), nullable=False, default=IncidentSentiment.NEGATIVE)
    sentiment_score = Column(Float, nullable=False, default=-0.5)
    classification_confidence = Column(Float, nullable=False, default=0.85)
    actionability_score = Column(Float, nullable=False, default=0.85)

    # Owning-function routing
    primary_owner = Column(String(50), nullable=False, default=OwningFunction.STORE_OPS, index=True)
    secondary_owner = Column(String(50), nullable=True)
    needs_human_review = Column(Boolean, nullable=False, default=False, index=True)
    routing_history = Column(JSON, nullable=True)

    # Deterministic policy flags
    safety_flag = Column(Boolean, nullable=False, default=False, index=True)
    allergen_flag = Column(Boolean, nullable=False, default=False, index=True)
    policy_escalated = Column(Boolean, nullable=False, default=False, index=True)
    policy_escalation_reason = Column(Text, nullable=True)

    status = Column(String(50), nullable=False, default=IncidentStatus.OPEN, index=True)
    first_seen_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=False, index=True)
    feedback_count = Column(Integer, nullable=False, default=1)

    # Traceability & ML version tracking
    model_version = Column(String(100), nullable=False)
    policy_version = Column(String(100), nullable=False)
    evidence_summary = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    store = relationship("Store", back_populates="incidents")
    feedback_records = relationship("FeedbackRecord", back_populates="incident")

    def __repr__(self):
        return f"<Incident {self.id[:8]} ({self.category}) - Store {self.store_id} [{self.severity}]>"
