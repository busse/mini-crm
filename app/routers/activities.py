"""Activities router.

Endpoints for logging and viewing activities.
Routes: GET/POST /api/activities, GET /api/activities/{id}
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.get("")
def list_activities():
    """List activities with pagination and filters."""
    pass


@router.post("")
def create_activity():
    """Log a new activity."""
    pass


@router.get("/{activity_id}")
def get_activity(activity_id: int):
    """Get a single activity by ID."""
    pass
