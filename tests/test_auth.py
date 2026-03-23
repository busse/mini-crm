"""Tests for authentication."""


def test_register(client):
    """POST /auth/register creates user."""
    pass


def test_login(client):
    """POST /auth/login returns token."""
    pass


def test_login_invalid_credentials(client):
    """POST /auth/login with bad credentials returns 401."""
    pass


def test_get_current_user(client, auth_headers):
    """GET /auth/me returns current user."""
    pass


def test_protected_route_without_token(client):
    """Protected routes return 401 without token."""
    pass
