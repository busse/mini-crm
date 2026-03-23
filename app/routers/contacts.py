"""Contacts router.

CRUD endpoints for managing contacts.
Routes: GET/POST /api/contacts, GET/PUT/DELETE /api/contacts/{id}
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.get("")
def list_contacts():
    """List contacts with pagination."""
    pass


@router.post("")
def create_contact():
    """Create a new contact."""
    pass


@router.get("/{contact_id}")
def get_contact(contact_id: int):
    """Get a single contact by ID."""
    pass


@router.put("/{contact_id}")
def update_contact(contact_id: int):
    """Update a contact."""
    pass


@router.delete("/{contact_id}")
def delete_contact(contact_id: int):
    """Delete a contact."""
    pass
