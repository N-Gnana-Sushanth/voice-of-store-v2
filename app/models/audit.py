"""Audit event log ORM model for administrative actions."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AuditAction:
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    STORE_CREATED = "STORE_CREATED"
    STORE_UPDATED = "STORE_UPDATED"
    FEEDBACK_INGESTED = "FEEDBACK_INGESTED"
    INCIDENT_STATUS_UPDATED = "INCIDENT_STATUS_UPDATED"
    ALERT_ACKNOWLEDGED = "ALERT_ACKNOWLEDGED"
    ALERT_RESOLVED = "ALERT_RESOLVED"
    REPLAY_STARTED = "REPLAY_STARTED"
    BASELINE_CALCULATED = "BASELINE_CALCULATED"


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_email = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True, index=True)
    
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utc_now, index=True)
    details_json = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<AuditEvent {self.action} on {self.resource_type}:{self.resource_id} by {self.actor_email}>"
