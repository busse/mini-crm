"""Contact schemas.

Pydantic models for contact request/response validation.
"""
from pydantic import BaseModel


class ContactBase(BaseModel):
    """Base contact fields."""

    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    company_id: int | None = None
    notes: str | None = None


class ContactCreate(ContactBase):
    """Fields for creating a contact."""

    pass


class ContactUpdate(BaseModel):
    """Fields for updating a contact (all optional)."""

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    company_id: int | None = None
    notes: str | None = None


class ContactResponse(ContactBase):
    """Contact response with ID."""

    id: int

    class Config:
        from_attributes = True
