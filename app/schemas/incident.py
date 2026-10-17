"""Incident request and response schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.feedback import FeedbackResponse


class IncidentResponse(BaseModel):
    id: str
    store_id: str
    category: str
    severity: str
    sentiment: str
    sentiment_score: float
    classification_confidence: float
    safety_flag: bool
    allergen_flag: bool
    policy_escalated: bool
    policy_escalation_reason: Optional[str] = None
    status: str
    first_seen_at: datetime
    last_seen_at: datetime
    feedback_count: int
    model_version: str
    policy_version: str
    evidence_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentDetailResponse(IncidentResponse):
    source_feedback: List[FeedbackResponse] = Field(
        default_factory=list,
        description="Linked raw feedback records preserving complete traceability",
    )


class IncidentStatusUpdate(BaseModel):
    status: str = Field(..., description="OPEN, UNDER_INVESTIGATION, RESOLVED, DISMISSED")
    notes: Optional[str] = Field(default=None, description="Resolution or investigation notes")
