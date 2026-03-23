"""Deals router.

CRUD endpoints for managing deals.
Routes: GET/POST /api/deals, GET/PUT/DELETE /api/deals/{id}
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/deals", tags=["deals"])


@router.get("")
def list_deals():
    """List deals with pagination."""
    pass


@router.post("")
def create_deal():
    """Create a new deal."""
    pass


@router.get("/{deal_id}")
def get_deal(deal_id: int):
    """Get a single deal by ID."""
    pass


@router.put("/{deal_id}")
def update_deal(deal_id: int):
    """Update a deal."""
    pass


@router.delete("/{deal_id}")
def delete_deal(deal_id: int):
    """Delete a deal."""
    pass
