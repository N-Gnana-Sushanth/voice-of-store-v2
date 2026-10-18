"""Remediation Task request and response schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    task_id: str = Field(..., min_length=2, max_length=50)
    title: str = Field(..., min_length=3, max_length=255)
    store_id: Optional[str] = None
    store_name: str = Field(..., min_length=2, max_length=255)
    owner: str = Field(..., min_length=2, max_length=100)
    owner_tag: str = Field(..., min_length=2, max_length=50)
    severity: str = Field(default="Medium")
    status: str = Field(default="Open")
    sla_window: str = Field(..., min_length=2, max_length=100)
    sla_urgent: bool = False
    reported_date: str = Field(..., min_length=2, max_length=50)
    notes: Optional[str] = None


class TaskStatusUpdate(BaseModel):
    status: str = Field(..., description="Open, In Progress, Resolved")
    notes: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    task_id: str
    title: str
    store_id: Optional[str] = None
    store_name: str
    owner: str
    owner_tag: str
    severity: str
    status: str
    sla_window: str
    sla_urgent: bool
    reported_date: str
    notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
