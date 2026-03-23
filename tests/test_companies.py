"""Tests for companies endpoints."""
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
def test_company_with_contacts(db, test_company):
    """Create a company with contacts."""
    for i in range(3):
        contact = Contact(
            first_name=f"User{i}",
            last_name="Test",
            email=f"user{i}@example.com",
            company_id=test_company.id,
        )
        db.add(contact)
    db.commit()
    db.refresh(test_company)
    return test_company


class TestListCompanies:
    """Tests for GET /api/companies."""

    def test_list_companies_empty(self, client):
        """List returns empty when no companies exist."""
        response = client.get("/api/companies")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["per_page"] == 20

    def test_list_companies_with_data(self, client, test_company):
        """List returns companies with pagination info."""
        response = client.get("/api/companies")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Acme Corp"
        assert data["items"][0]["contact_count"] == 0

    def test_list_companies_with_contact_count(self, client, test_company_with_contacts):
        """List includes correct contact count."""
        response = client.get("/api/companies")

        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["contact_count"] == 3

    def test_list_companies_pagination(self, client, db):
        """List respects pagination parameters."""
        for i in range(5):
            company = Company(
                name=f"Company {i}",
                industry="Technology",
            )
            db.add(company)
        db.commit()

        response = client.get("/api/companies?page=2&per_page=2")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 2
        assert data["per_page"] == 2


class TestGetCompany:
    """Tests for GET /api/companies/{id}."""

    def test_get_company_success(self, client, test_company):
        """Get returns company with details."""
        response = client.get(f"/api/companies/{test_company.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_company.id
        assert data["name"] == "Acme Corp"
        assert data["industry"] == "Technology"
        assert data["website"] == "https://acme.example.com"
        assert data["contact_count"] == 0
        assert data["contacts"] == []
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_company_with_contacts(self, client, test_company_with_contacts):
        """Get returns company with contacts list."""
        response = client.get(f"/api/companies/{test_company_with_contacts.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["contact_count"] == 3
        assert len(data["contacts"]) == 3
        assert "first_name" in data["contacts"][0]
        assert "last_name" in data["contacts"][0]
        assert "email" in data["contacts"][0]

    def test_get_company_not_found(self, client):
        """Get returns 404 for nonexistent company."""
        response = client.get("/api/companies/9999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Company not found"


class TestCreateCompany:
    """Tests for POST /api/companies."""

    def test_create_company_success(self, client, auth_headers):
        """Create returns new company with 201."""
        payload = {
            "name": "New Corp",
            "industry": "Finance",
            "website": "https://newcorp.example.com",
        }

        response = client.post("/api/companies", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Corp"
        assert data["industry"] == "Finance"
        assert data["website"] == "https://newcorp.example.com"
        assert data["contact_count"] == 0
        assert "id" in data

    def test_create_company_minimal(self, client, auth_headers):
        """Create works with only required fields."""
        payload = {"name": "Minimal Corp"}

        response = client.post("/api/companies", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Corp"
        assert data["industry"] is None
        assert data["website"] is None

    def test_create_company_requires_auth(self, client):
        """Create returns 401 without auth."""
        payload = {"name": "Test Corp"}

        response = client.post("/api/companies", json=payload)

        assert response.status_code == 401


class TestUpdateCompany:
    """Tests for PUT /api/companies/{id}."""

    def test_update_company_success(self, client, auth_headers, test_company):
        """Update modifies company fields."""
        payload = {"name": "Acme Industries", "industry": "Manufacturing"}

        response = client.put(
            f"/api/companies/{test_company.id}",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Acme Industries"
        assert data["industry"] == "Manufacturing"
        assert data["website"] == "https://acme.example.com"  # unchanged

    def test_update_company_partial(self, client, auth_headers, test_company):
        """Update works with partial data."""
        payload = {"industry": "Retail"}

        response = client.put(
            f"/api/companies/{test_company.id}",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Acme Corp"  # unchanged
        assert data["industry"] == "Retail"

    def test_update_company_not_found(self, client, auth_headers):
        """Update returns 404 for nonexistent company."""
        response = client.put(
            "/api/companies/9999",
            json={"name": "Test"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_company_requires_auth(self, client, test_company):
        """Update returns 401 without auth."""
        response = client.put(
            f"/api/companies/{test_company.id}",
            json={"name": "Test"},
        )

        assert response.status_code == 401
