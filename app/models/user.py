"""User ORM model with role-based access control."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserRole:
    ADMIN = "admin"
    STORE_MANAGER = "store_manager"
    ANALYST = "analyst"

    ALL = [ADMIN, STORE_MANAGER, ANALYST]


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.ANALYST, index=True)
    # Store-level isolation for STORE_MANAGER role
    store_id = Column(String(36), ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    store = relationship("Store", back_populates="users")
    acknowledged_alerts = relationship("Alert", foreign_keys="Alert.acknowledged_by_id", back_populates="acknowledged_by")
    resolved_alerts = relationship("Alert", foreign_keys="Alert.resolved_by_id", back_populates="resolved_by")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
