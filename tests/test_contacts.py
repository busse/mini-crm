"""Tests for contacts endpoints."""
import pytest

from app.auth.utils import create_access_token, hash_password
from app.models.user import User
from app.models.contact import Contact
from app.models.company import Company


@pytest.fixture
def test_user(db):
    """Create a test user for authentication."""
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


@pytest.fixture
def auth_headers(test_user):
    """Provide auth headers with valid JWT token."""
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_company(db):
    """Create a test company."""
    company = Company(
        name="Acme Corp",
        industry="Technology",
        website="https://acme.example.com",
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@pytest.fixture
def test_contact(db, test_company):
    """Create a test contact."""
    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="555-1234",
        role="Engineer",
        company_id=test_company.id,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


class TestListContacts:
    """Tests for GET /api/contacts."""

    def test_list_contacts_empty(self, client):
        """List returns empty when no contacts exist."""
        response = client.get("/api/contacts")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["per_page"] == 20

    def test_list_contacts_with_data(self, client, test_contact):
        """List returns contacts with pagination info."""
        response = client.get("/api/contacts")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["first_name"] == "John"
        assert data["items"][0]["company_name"] == "Acme Corp"

    def test_list_contacts_pagination(self, client, db, test_company):
        """List respects pagination parameters."""
        for i in range(5):
            contact = Contact(
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@example.com",
                company_id=test_company.id,
            )
            db.add(contact)
        db.commit()

        response = client.get("/api/contacts?page=2&per_page=2")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 2
        assert data["per_page"] == 2


class TestGetContact:
    """Tests for GET /api/contacts/{id}."""

    def test_get_contact_success(self, client, test_contact):
        """Get returns contact with company name."""
        response = client.get(f"/api/contacts/{test_contact.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_contact.id
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "john@example.com"
        assert data["company_name"] == "Acme Corp"
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_contact_not_found(self, client):
        """Get returns 404 for nonexistent contact."""
        response = client.get("/api/contacts/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Contact not found"


class TestCreateContact:
    """Tests for POST /api/contacts."""

    def test_create_contact_success(self, client, auth_headers, test_company):
        """Create returns new contact with 201."""
        payload = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "phone": "555-5678",
            "role": "Manager",
            "company_id": test_company.id,
        }

        response = client.post("/api/contacts", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
        assert data["email"] == "jane@example.com"
        assert data["company_name"] == "Acme Corp"
        assert "id" in data

    def test_create_contact_minimal(self, client, auth_headers):
        """Create works with only required fields."""
        payload = {
            "first_name": "Bob",
            "last_name": "Jones",
            "email": "bob@example.com",
        }

        response = client.post("/api/contacts", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Bob"
        assert data["phone"] is None
        assert data["company_name"] is None

    def test_create_contact_requires_auth(self, client):
        """Create returns 401 without auth."""
        payload = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
        }

        response = client.post("/api/contacts", json=payload)

        assert response.status_code == 401


class TestUpdateContact:
    """Tests for PUT /api/contacts/{id}."""

    def test_update_contact_success(self, client, auth_headers, test_contact):
        """Update modifies contact fields."""
        payload = {"first_name": "Johnny", "role": "Senior Engineer"}

        response = client.put(
            f"/api/contacts/{test_contact.id}",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Johnny"
        assert data["role"] == "Senior Engineer"
        assert data["last_name"] == "Doe"  # unchanged

    def test_update_contact_not_found(self, client, auth_headers):
        """Update returns 404 for nonexistent contact."""
        response = client.put(
            "/api/contacts/9999",
            json={"first_name": "Test"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_contact_requires_auth(self, client, test_contact):
        """Update returns 401 without auth."""
        response = client.put(
            f"/api/contacts/{test_contact.id}",
            json={"first_name": "Test"},
        )

        assert response.status_code == 401


class TestDeleteContact:
    """Tests for DELETE /api/contacts/{id}."""

    def test_delete_contact_success(self, client, auth_headers, test_contact, db):
        """Delete removes contact and returns 204."""
        contact_id = test_contact.id

        response = client.delete(
            f"/api/contacts/{contact_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deleted
        deleted = db.query(Contact).filter(Contact.id == contact_id).first()
        assert deleted is None

    def test_delete_contact_not_found(self, client, auth_headers):
        """Delete returns 404 for nonexistent contact."""
        response = client.delete("/api/contacts/9999", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_contact_requires_auth(self, client, test_contact):
        """Delete returns 401 without auth."""
        response = client.delete(f"/api/contacts/{test_contact.id}")

        assert response.status_code == 401
