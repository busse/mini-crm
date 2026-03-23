"""Tag schemas.

Pydantic models for tag request/response validation.
"""
from pydantic import BaseModel, ConfigDict


class TagCreate(BaseModel):
    """Fields for creating a tag."""

    name: str
    color: str | None = None


class TagResponse(BaseModel):
    """Tag response with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    color: str | None


class TagListResponse(BaseModel):
    """List of tags."""

    items: list[TagResponse]
    total: int


class DealTagRequest(BaseModel):
    """Request to add a tag to a deal."""

    tag_id: int
