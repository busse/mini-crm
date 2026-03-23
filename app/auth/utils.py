"""Authentication utilities.

JWT token creation/validation and password hashing helpers.
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    pass


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    pass
