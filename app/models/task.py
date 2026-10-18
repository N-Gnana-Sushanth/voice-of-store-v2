"""Remediation Task ORM model for Action Queue."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TaskStatus:
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"

    ALL = [OPEN, IN_PROGRESS, RESOLVED]


class RemediationTask(Base):
    __tablename__ = "remediation_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "ACT-101"
    title = Column(String(255), nullable=False)
    store_id = Column(String(36), ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True)
    store_name = Column(String(255), nullable=False)
    owner = Column(String(100), nullable=False)
    owner_tag = Column(String(50), nullable=False)
    severity = Column(String(50), nullable=False, default="Medium")
    status = Column(String(50), nullable=False, default=TaskStatus.OPEN, index=True)
    sla_window = Column(String(100), nullable=False)
    sla_urgent = Column(Boolean, nullable=False, default=False)
    reported_date = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    store = relationship("Store")

    def __repr__(self) -> str:
        return f"<RemediationTask {self.task_id}: {self.title} ({self.status})>"
