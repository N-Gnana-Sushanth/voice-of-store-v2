"""Chronological replay and evaluation schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReplayRunCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Name for this replay experiment")
    description: Optional[str] = Field(default=None, description="Experiment description / hypothesis")
    time_range_start: datetime = Field(..., description="Simulated start time (UTC)")
    time_range_end: datetime = Field(..., description="Simulated end time (UTC)")
    include_planted_evaluations: bool = Field(
        default=True,
        description="Whether to evaluate the 3 synthetic ground-truth planted incidents",
    )


class PlantedIncidentEvaluation(BaseModel):
    code: str
    name: str
    store_number: str
    category: str
    onset_timestamp: datetime
    detected: bool
    detection_timestamp: Optional[datetime] = None
    detection_lead_time_hours: Optional[float] = None
    alert_severity: Optional[str] = None
    evidence_summary: Optional[str] = None


class ReplayEvaluationMetrics(BaseModel):
    total_records_processed: int
    incidents_formed: int
    alerts_triggered: int
    planted_incidents_total: int
    planted_incidents_detected: int
    planted_recall: float
    precision_estimate: float
    mean_lead_time_hours: Optional[float] = None
    future_data_leakage_prevented: bool
    planted_evaluations: List[PlantedIncidentEvaluation]


class ReplayRunResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    time_range_start: datetime
    time_range_end: datetime
    status: str
    total_records: int
    processed_records: int
    incidents_created: int
    alerts_generated: int
    evaluation_metrics: Optional[ReplayEvaluationMetrics] = None
    model_version: str
    baseline_version: str
    start_time: datetime
    completion_time: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
