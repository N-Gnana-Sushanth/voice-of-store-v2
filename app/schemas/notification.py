"""User Notification request and response schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    message: str = Field(..., min_length=2)
    severity: str = Field(default="INFO", description="INFO, WARNING, HIGH, CRITICAL")
    alert_id: Optional[str] = None
    link: Optional[str] = None


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    severity: str
    alert_id: Optional[str] = None
    link: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UnreadCountResponse(BaseModel):
    unread_count: int
