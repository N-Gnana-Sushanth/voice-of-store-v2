"""Audit logging service for tracking administrative events."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditEvent
from app.models.user import User


class AuditService:
    """Records audit logs for sensitive operations with scrubbed credentials."""

    @classmethod
    def log_event(
        cls,
        db: Session,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        actor: Optional[User] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Create and persist an audit event."""
        # Sanitize details to avoid logging passwords or authorization tokens
        clean_details = {}
        if details:
            for k, v in details.items():
                if any(secret_term in k.lower() for secret_term in ["password", "token", "secret", "key"]):
                    clean_details[k] = "[REDACTED]"
                else:
                    clean_details[k] = v

        event = AuditEvent(
            actor_id=actor.id if actor else None,
            actor_email=actor.email if actor else "system",
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            timestamp=datetime.now(timezone.utc),
            details_json=clean_details,
        )
        db.add(event)
        db.commit()
        return event


# Singleton instance
audit_service = AuditService()
