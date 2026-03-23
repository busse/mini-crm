"""Authentication routes.

Handles /auth/login, /auth/register, and /auth/me endpoints.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login():
    """Authenticate user and return JWT token."""
    pass


@router.post("/register")
def register():
    """Register a new user."""
    pass


@router.get("/me")
def get_current_user_info():
    """Get current authenticated user info."""
    pass
