"""Feedback submission and response schemas."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


def default_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FeedbackSubmitSingle(BaseModel):
    store_id: str = Field(..., description="Store UUID or store number")
    text: str = Field(..., min_length=3, max_length=10000, description="Raw feedback narrative")
    source: str = Field(default="customer", description="customer, employee, survey, web, inspection")
    event_timestamp: Optional[datetime] = Field(
        default=None,
        description="When the event occurred (ISO 8601). Normalized to UTC. Defaults to ingestion time if omitted.",
    )
    idempotency_key: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Client-provided unique key for safe retries and duplicate submission protection",
    )
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata context")

    @field_validator("event_timestamp", mode="before")
    @classmethod
    def normalize_utc_timestamp(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return None
        if isinstance(v, str):
            # Parse ISO string
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v.astimezone(timezone.utc)
        return v


class FeedbackSubmitBatch(BaseModel):
    items: List[FeedbackSubmitSingle] = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Batch array of feedback submissions (up to 500 records)",
    )


class FeedbackResponse(BaseModel):
    id: str
    store_id: str
    text: str
    source: str
    event_timestamp: datetime
    ingestion_timestamp: datetime
    idempotency_key: Optional[str] = None
    processing_status: str
    incident_id: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackBatchItemResult(BaseModel):
    index: int
    idempotency_key: Optional[str] = None
    status: str  # SUCCESS, DUPLICATE, ERROR
    feedback_id: Optional[str] = None
    incident_id: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    safety_flag: Optional[bool] = None
    allergen_flag: Optional[bool] = None
    error: Optional[str] = None


class FeedbackBatchResponse(BaseModel):
    total_received: int
    successful_count: int
    duplicate_count: int
    failed_count: int
    results: List[FeedbackBatchItemResult]
