"""Store ORM model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Store(Base):
    __tablename__ = "stores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    store_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    region = Column(String(50), nullable=True, index=True)
    size_sqft = Column(Float, nullable=False, default=10000.0)
    avg_daily_transactions = Column(Float, nullable=False, default=1500.0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    users = relationship("User", back_populates="store", cascade="all, delete-orphan")
    feedback_records = relationship("FeedbackRecord", back_populates="store", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="store", cascade="all, delete-orphan")
    baselines = relationship("HistoricalBaseline", back_populates="store", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="store", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Store {self.store_number}: {self.name}>"
