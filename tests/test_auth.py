"""Tests for authentication endpoints."""
import pytest

from app.auth.utils import create_access_token, hash_password
from app.models.user import User


@pytest.fixture
def test_user(db):
    """Create a test user in the database."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_pw=hash_password("testpassword"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestLogin:
    """Tests for POST /auth/login."""

    def test_login_success(self, client, test_user):
        """Successful login returns access token."""
        response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "testpassword"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Login with wrong password returns 401."""
        response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

    def test_login_nonexistent_user(self, client):
        """Login with nonexistent user returns 401."""
        response = client.post(
            "/auth/login",
            data={"username": "nouser", "password": "anypassword"},
        )

        assert response.status_code == 401


class TestMe:
    """Tests for GET /auth/me."""

    def test_me_with_valid_token(self, client, test_user):
        """GET /auth/me with valid token returns user info."""
        token = create_access_token(data={"sub": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["is_active"] is True

    def test_me_without_token(self, client):
        """GET /auth/me without token returns 401."""
        response = client.get("/auth/me")

        assert response.status_code == 401

    def test_me_with_invalid_token(self, client):
        """GET /auth/me with invalid token returns 401."""
        headers = {"Authorization": "Bearer invalid-token"}

        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 401
