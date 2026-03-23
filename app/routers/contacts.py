"""Contacts router.

CRUD endpoints for managing contacts.
Routes: GET/POST /api/contacts, GET/PUT/DELETE /api/contacts/{id}
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.contact import Contact
from app.models.user import User
from app.schemas.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
)

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


def _contact_to_response(contact: Contact) -> ContactResponse:
    """Convert Contact model to response schema with company name."""
    return ContactResponse(
        id=contact.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        role=contact.role,
        company_id=contact.company_id,
        company_name=contact.company.name if contact.company else None,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
    )


@router.get("", response_model=ContactListResponse)
def list_contacts(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
) -> ContactListResponse:
    """List contacts with pagination."""
    offset = (page - 1) * per_page
    total = db.query(Contact).count()
    contacts = (
        db.query(Contact)
        .options(joinedload(Contact.company))
        .offset(offset)
        .limit(per_page)
        .all()
    )
    return ContactListResponse(
        items=[_contact_to_response(c) for c in contacts],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
) -> ContactResponse:
    """Get a single contact by ID with company and deals eager-loaded."""
    contact = (
        db.query(Contact)
        .options(joinedload(Contact.company), joinedload(Contact.deals))
        .filter(Contact.id == contact_id)
        .first()
    )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return _contact_to_response(contact)


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact_in: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    """Create a new contact."""
    contact = Contact(
        first_name=contact_in.first_name,
        last_name=contact_in.last_name,
        email=contact_in.email,
        phone=contact_in.phone,
        role=contact_in.role,
        company_id=contact_in.company_id,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return _contact_to_response(contact)


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact_in: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    """Update a contact."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    update_data = contact_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)

    if contact.company_id:
        db.refresh(contact, ["company"])

    return _contact_to_response(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a contact."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    db.delete(contact)
    db.commit()
