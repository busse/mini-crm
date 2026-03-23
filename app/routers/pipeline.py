"""Pipeline router.

Endpoints for the kanban-style pipeline view.
Routes: GET /api/pipeline, PUT /api/pipeline/move
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.get("")
def get_pipeline():
    """Get deals grouped by stage for pipeline view."""
    pass


@router.put("/move")
def move_deal():
    """Move a deal to a different stage."""
    pass


@router.get("/stages")
def list_stages():
    """List all pipeline stages."""
    pass
