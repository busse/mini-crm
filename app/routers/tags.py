"""Tags router.

CRUD endpoints for managing tags.
Routes: GET/POST /api/tags, DELETE /api/tags/{id}
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("")
def list_tags():
    """List all tags."""
    pass


@router.post("")
def create_tag():
    """Create a new tag."""
    pass


@router.delete("/{tag_id}")
def delete_tag(tag_id: int):
    """Delete a tag."""
    pass
