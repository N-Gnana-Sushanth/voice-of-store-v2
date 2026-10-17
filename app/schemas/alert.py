"""Emerging-issue Alert request and response schemas."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    id: str
    store_id: str
    category: str
    alert_type: str
    severity: str
    status: str
    current_count: int
    current_rate: float
    baseline_rate: float
    rate_ratio: float
    z_score: Optional[float] = None
    observation_window_days: int
    exposure_volume: float
    sample_size: int
    confidence_score: float
    first_detected_at: datetime
    last_detected_at: datetime
    detection_count: int
    acknowledged_by_id: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by_id: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertDetailResponse(AlertResponse):
    evidence_json: Dict[str, Any] = Field(..., description="Explainable evidence breakdown")
    peer_comparison_json: Optional[Dict[str, Any]] = Field(default=None, description="Peer stores comparison data")


class AlertAcknowledgeRequest(BaseModel):
    notes: Optional[str] = Field(default=None, description="Optional acknowledgment note")


class AlertResolveRequest(BaseModel):
    resolution_notes: str = Field(..., min_length=3, description="Mandatory explanation of resolution action taken")
