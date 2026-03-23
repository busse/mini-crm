"""Contact schemas.

Pydantic models for contact request/response validation.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContactCreate(BaseModel):
    """Fields for creating a contact."""

    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    role: str | None = None
    company_id: int | None = None


class ContactUpdate(BaseModel):
    """Fields for updating a contact (all optional)."""

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    role: str | None = None
    company_id: int | None = None


class ContactResponse(BaseModel):
    """Contact response with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    role: str | None
    company_id: int | None
    company_name: str | None = None
    created_at: datetime
    updated_at: datetime


class ContactListResponse(BaseModel):
    """Paginated list of contacts."""

    items: list[ContactResponse]
    total: int
    page: int
    per_page: int
