"""Escalation Review ORM model for measuring verified precision of escalated issues."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EscalationReview(Base):
    __tablename__ = "escalation_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Review status:
    # True  = Verified True Positive (actionable)
    # False = Verified False Positive (spurious / unneeded escalation)
    # None  = Pending human review (MUST NOT be counted as false positive)
    is_truly_actionable = Column(Boolean, nullable=True, index=True)

    review_notes = Column(Text, nullable=True)
    reviewer_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    incident = relationship("Incident")
    reviewer = relationship("User")

    def __repr__(self):
        status = "UNREVIEWED" if self.is_truly_actionable is None else ("TP" if self.is_truly_actionable else "FP")
        return f"<EscalationReview {self.id[:8]} - Incident {self.incident_id[:8]} [{status}]>"
