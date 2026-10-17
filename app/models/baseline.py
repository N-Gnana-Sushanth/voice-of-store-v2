"""Historical baseline ORM model for emerging-issue detection."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HistoricalBaseline(Base):
    __tablename__ = "historical_baselines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id = Column(String(36), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    time_window_days = Column(Integer, nullable=False, default=30)
    
    historical_incident_count = Column(Integer, nullable=False, default=0)
    exposure_units = Column(Float, nullable=False, default=0.0)  # e.g., total transactions in window
    normalized_rate = Column(Float, nullable=False, default=0.0)  # incidents per 1,000 transactions
    
    baseline_mean = Column(Float, nullable=False, default=0.0)
    baseline_std = Column(Float, nullable=False, default=0.0)
    min_sample_met = Column(Boolean, nullable=False, default=False)
    
    baseline_version = Column(String(50), nullable=False, default="v1.0.0")
    calculated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    # Relationships
    store = relationship("Store", back_populates="baselines")

    __table_args__ = (
        UniqueConstraint("store_id", "category", "time_window_days", "baseline_version", name="uq_store_category_window_version"),
    )

    def __repr__(self):
        return f"<HistoricalBaseline {self.store_id} - {self.category} (Rate: {self.normalized_rate:.2f})>"
