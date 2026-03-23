"""Activity schemas.

Pydantic models for activity request/response validation.
"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ActivityType(str, Enum):
    """Valid activity types."""

    call = "call"
    email = "email"
    meeting = "meeting"
    note = "note"


class ActivityCreate(BaseModel):
    """Fields for creating an activity."""

    type: ActivityType
    subject: str
    notes: str | None = None
    occurred_at: datetime


class ActivityResponse(BaseModel):
    """Activity response with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    subject: str
    notes: str | None
    occurred_at: datetime
    deal_id: int | None
    contact_id: int | None
    created_at: datetime


class ActivityListResponse(BaseModel):
    """List of activities."""

    items: list[ActivityResponse]
    total: int
