"""Activity schemas.

Pydantic models for activity request/response validation.
"""
from datetime import datetime
from pydantic import BaseModel


class ActivityBase(BaseModel):
    """Base activity fields."""

    type: str  # call, email, meeting, note
    subject: str
    description: str | None = None
    contact_id: int | None = None
    deal_id: int | None = None


class ActivityCreate(ActivityBase):
    """Fields for creating an activity."""

    pass


class ActivityResponse(ActivityBase):
    """Activity response with ID and timestamp."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True
