"""Authentication dependencies.

Provides get_current_user dependency for protecting routes.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validate JWT token and return current user.

    Raises HTTPException 401 if token is invalid or expired.
    """
    pass
