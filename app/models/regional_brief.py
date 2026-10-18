"""Regional Brief ORM model for weekly one-page regional executive briefs."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, JSON
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RegionalBrief(Base):
    __tablename__ = "regional_briefs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    region = Column(String(50), nullable=False, index=True)
    week_start = Column(DateTime(timezone=True), nullable=False, index=True)
    week_end = Column(DateTime(timezone=True), nullable=False)

    executive_summary = Column(Text, nullable=False)
    top_issues_json = Column(JSON, nullable=False)  # List of top 5 issues with rank, counts, trends, quotes, owner, SLA
    low_volume_safety_json = Column(JSON, nullable=True)  # Low-volume critical safety warnings
    metrics_json = Column(JSON, nullable=False)  # Total feedback, incident rate, active stores, SLA adherence
    html_content = Column(Text, nullable=True)  # Formatted HTML report optimized for 1-page print/PDF export

    generated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    def __repr__(self):
        return f"<RegionalBrief {self.region} [{self.week_start.date()} to {self.week_end.date()}]>"
