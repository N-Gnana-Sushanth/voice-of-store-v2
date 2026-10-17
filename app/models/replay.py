"""Historical replay run ORM model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Text, JSON
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ReplayStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    ALL = [PENDING, RUNNING, COMPLETED, FAILED]


class ReplayRun(Base):
    __tablename__ = "replay_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Historical simulated window
    time_range_start = Column(DateTime(timezone=True), nullable=False)
    time_range_end = Column(DateTime(timezone=True), nullable=False)

    status = Column(String(50), nullable=False, default=ReplayStatus.PENDING, index=True)
    config_json = Column(JSON, nullable=False)

    # Execution metrics
    total_records = Column(Integer, nullable=False, default=0)
    processed_records = Column(Integer, nullable=False, default=0)
    incidents_created = Column(Integer, nullable=False, default=0)
    alerts_generated = Column(Integer, nullable=False, default=0)

    # Detailed evaluation results (lead time, precision, recall, false positives)
    evaluation_metrics_json = Column(JSON, nullable=True)

    model_version = Column(String(50), nullable=False)
    baseline_version = Column(String(50), nullable=False)

    start_time = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    completion_time = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    def __repr__(self):
        return f"<ReplayRun {self.name} [{self.status}] ({self.processed_records}/{self.total_records})>"
