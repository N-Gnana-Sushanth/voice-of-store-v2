"""Feedback record ORM model preserving raw customer and employee inputs."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FeedbackSource:
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    SURVEY = "survey"
    WEB = "web"
    INSPECTION = "inspection"

    ALL = [CUSTOMER, EMPLOYEE, SURVEY, WEB, INSPECTION]


class ProcessingStatus:
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

    ALL = [PENDING, PROCESSED, FAILED]


class FeedbackRecord(Base):
    __tablename__ = "feedback_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id = Column(String(36), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    source = Column(String(50), nullable=False, default=FeedbackSource.CUSTOMER)
    
    # Event timestamp (normalized to UTC) vs Ingestion timestamp
    event_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    ingestion_timestamp = Column(DateTime(timezone=True), nullable=False, default=utc_now, index=True)

    # Protection against duplicate API submissions / retries
    idempotency_key = Column(String(255), nullable=True, unique=True, index=True)

    # Processing lifecycle
    processing_status = Column(String(50), nullable=False, default=ProcessingStatus.PENDING, index=True)
    error_message = Column(Text, nullable=True)

    # Link to consolidated incident
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)

    # Arbitrary metadata provided during ingestion (e.g. shift, channel, customer_loyalty_tier)
    metadata_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    store = relationship("Store", back_populates="feedback_records")
    incident = relationship("Incident", back_populates="feedback_records")

    def __repr__(self):
        return f"<FeedbackRecord {self.id[:8]} - Store {self.store_id} [{self.processing_status}]>"
