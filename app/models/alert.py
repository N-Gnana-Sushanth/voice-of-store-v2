"""Emerging-issue Alert ORM model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AlertType:
    SPIKE = "SPIKE"
    SUSTAINED_INCREASE = "SUSTAINED_INCREASE"
    PEER_DEVIATION = "PEER_DEVIATION"
    URGENT_SAFETY = "URGENT_SAFETY"

    ALL = [SPIKE, SUSTAINED_INCREASE, PEER_DEVIATION, URGENT_SAFETY]


class AlertSeverity:
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    ALL = [INFO, WARNING, HIGH, CRITICAL]


class AlertStatus:
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"

    ALL = [ACTIVE, ACKNOWLEDGED, RESOLVED]


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id = Column(String(36), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    
    alert_type = Column(String(50), nullable=False, default=AlertType.SPIKE, index=True)
    severity = Column(String(50), nullable=False, default=AlertSeverity.WARNING, index=True)
    status = Column(String(50), nullable=False, default=AlertStatus.ACTIVE, index=True)

    # Statistical observations
    current_count = Column(Integer, nullable=False)
    current_rate = Column(Float, nullable=False)  # Normalized rate
    baseline_rate = Column(Float, nullable=False)
    rate_ratio = Column(Float, nullable=False)
    z_score = Column(Float, nullable=True)

    observation_window_days = Column(Integer, nullable=False, default=7)
    exposure_volume = Column(Float, nullable=False)  # Total transactions/exposure in current window
    sample_size = Column(Integer, nullable=False)  # Feedback/incident sample size
    confidence_score = Column(Float, nullable=False, default=0.8)

    # Detailed explainability evidence
    evidence_json = Column(JSON, nullable=False)
    peer_comparison_json = Column(JSON, nullable=True)

    # Cooldown & deduplication tracking
    first_detected_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    last_detected_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    detection_count = Column(Integer, nullable=False, default=1)

    # Acknowledgment & Resolution lifecycle
    acknowledged_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    
    resolved_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    store = relationship("Store", back_populates="alerts")
    acknowledged_by = relationship("User", foreign_keys=[acknowledged_by_id], back_populates="acknowledged_alerts")
    resolved_by = relationship("User", foreign_keys=[resolved_by_id], back_populates="resolved_alerts")

    def __repr__(self):
        return f"<Alert {self.id[:8]} Store {self.store_id} ({self.category}) [{self.severity}|{self.status}]>"
