"""Store analytics request and response schemas."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CategoryBreakdownItem(BaseModel):
    category: str
    incident_count: int
    percentage: float
    normalized_rate: float  # Incidents per 1,000 exposure units


class SeverityBreakdownItem(BaseModel):
    severity: str
    incident_count: int
    percentage: float


class DailyTrendItem(BaseModel):
    date: str  # YYYY-MM-DD
    feedback_volume: int
    incident_count: int
    escalated_count: int
    normalized_rate: float


class StoreComparisonItem(BaseModel):
    store_id: str
    store_number: str
    store_name: str
    exposure_type: str  # "transactions" or "size_sqft"
    exposure_volume: float
    total_feedback: int
    distinct_incidents: int
    duplicate_count: int
    normalized_rate: float  # Incidents per 1,000 exposure units
    safety_escalations: int
    active_alerts: int


class StoreSummaryAnalytics(BaseModel):
    store_id: Optional[str] = None
    store_name: Optional[str] = None
    time_window_days: int
    
    # Core volume metrics
    total_feedback_volume: int
    total_distinct_incidents: int
    duplicate_feedback_count: int
    deduplication_ratio: float
    
    # Lifecycle & Policy counts
    open_incidents: int
    under_investigation_incidents: int
    resolved_incidents: int
    safety_escalations: int
    allergen_escalations: int
    active_alerts_count: int

    # Exposure-normalized rates
    exposure_metric: str  # "transactions" or "sqft"
    total_exposure: float
    overall_normalized_rate: float  # per 1,000 transactions/units
    sample_size_confidence: str  # "HIGH", "MODERATE", "LOW"

    # Breakdowns
    by_category: List[CategoryBreakdownItem]
    by_severity: List[SeverityBreakdownItem]
    daily_trends: List[DailyTrendItem]
