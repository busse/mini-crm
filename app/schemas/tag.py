"""Tag schemas.

Pydantic models for tag request/response validation.
"""
from pydantic import BaseModel


class TagBase(BaseModel):
    """Base tag fields."""

    name: str
    color: str | None = None


class TagCreate(TagBase):
    """Fields for creating a tag."""

    pass


class TagResponse(TagBase):
    """Tag response with ID."""

    id: int

    class Config:
        from_attributes = True
