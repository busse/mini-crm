"""Tests for deals endpoints."""
import pytest

from app.auth.utils import create_access_token, hash_password
from app.models.user import User
from app.models.contact import Contact
from app.models.company import Company
from app.models.deal import Deal
from app.models.deal_stage import DealStage


# TODO: add tests for PATCH stage endpoint


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


@pytest.fixture
def test_stage(db):
    """Create a test deal stage."""
    stage = DealStage(
        name="Qualified",
        display_order=1,
        is_closed=False,
    )
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return stage


@pytest.fixture
def test_stage_closed(db):
    """Create a closed deal stage."""
    stage = DealStage(
        name="Closed Won",
        display_order=5,
        is_closed=True,
    )
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return stage


@pytest.fixture
def test_deal(db, test_contact, test_stage):
    """Create a test deal."""
    deal = Deal(
        title="Enterprise License",
        value=50000,
        currency="USD",
        contact_id=test_contact.id,
        stage_id=test_stage.id,
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


class TestListDeals:
    """Tests for GET /api/deals."""

    def test_list_deals_empty(self, client):
        """List returns empty when no deals exist."""
        response = client.get("/api/deals")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["per_page"] == 20

    def test_list_deals_with_data(self, client, test_deal):
        """List returns deals with pagination info."""
        response = client.get("/api/deals")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Enterprise License"
        assert data["items"][0]["contact_name"] == "John Doe"
        assert data["items"][0]["stage_name"] == "Qualified"

    def test_list_deals_filter_by_stage(self, client, db, test_contact, test_stage, test_stage_closed):
        """List filters deals by stage_id."""
        deal1 = Deal(
            title="Deal in Qualified",
            value=10000,
            currency="USD",
            contact_id=test_contact.id,
            stage_id=test_stage.id,
        )
        deal2 = Deal(
            title="Deal in Closed Won",
            value=20000,
            currency="USD",
            contact_id=test_contact.id,
            stage_id=test_stage_closed.id,
        )
        db.add_all([deal1, deal2])
        db.commit()

        response = client.get(f"/api/deals?stage_id={test_stage.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Deal in Qualified"

    def test_list_deals_pagination(self, client, db, test_contact, test_stage):
        """List respects pagination parameters."""
        for i in range(5):
            deal = Deal(
                title=f"Deal {i}",
                value=1000 * (i + 1),
                currency="USD",
                contact_id=test_contact.id,
                stage_id=test_stage.id,
            )
            db.add(deal)
        db.commit()

        response = client.get("/api/deals?page=2&per_page=2")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 2
        assert data["per_page"] == 2


class TestGetDeal:
    """Tests for GET /api/deals/{id}."""

    def test_get_deal_success(self, client, test_deal):
        """Get returns deal with related data."""
        response = client.get(f"/api/deals/{test_deal.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_deal.id
        assert data["title"] == "Enterprise License"
        assert data["value"] == "50000.00"
        assert data["currency"] == "USD"
        assert data["contact_name"] == "John Doe"
        assert data["stage_name"] == "Qualified"
        assert data["activity_count"] == 0
        assert "tags" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_deal_not_found(self, client):
        """Get returns 404 for nonexistent deal."""
        response = client.get("/api/deals/9999")

        assert response.status_code == 404


class TestCreateDeal:
    """Tests for POST /api/deals."""

    def test_create_deal_success(self, client, auth_headers, test_contact, test_stage):
        """Create returns new deal with 201."""
        payload = {
            "title": "New Opportunity",
            "value": "25000",
            "currency": "USD",
            "contact_id": test_contact.id,
            "stage_id": test_stage.id,
        }

        response = client.post("/api/deals", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Opportunity"
        assert data["value"] == "25000.00"
        assert data["currency"] == "USD"
        assert data["contact_name"] == "John Doe"
        assert data["stage_name"] == "Qualified"
        assert "id" in data

    def test_create_deal_with_expected_close(self, client, auth_headers, test_contact, test_stage):
        """Create works with expected_close date."""
        payload = {
            "title": "Q4 Deal",
            "value": "15000",
            "currency": "EUR",
            "expected_close": "2024-12-31",
            "contact_id": test_contact.id,
            "stage_id": test_stage.id,
        }

        response = client.post("/api/deals", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Q4 Deal"
        assert data["expected_close"] == "2024-12-31"
        assert data["currency"] == "EUR"

    def test_create_deal_requires_auth(self, client, test_contact, test_stage):
        """Create returns 401 without auth."""
        payload = {
            "title": "Test Deal",
            "value": "1000",
            "contact_id": test_contact.id,
            "stage_id": test_stage.id,
        }

        response = client.post("/api/deals", json=payload)

        assert response.status_code == 401


class TestUpdateDeal:
    """Tests for PUT /api/deals/{id}."""

    def test_update_deal_success(self, client, auth_headers, test_deal):
        """Update modifies deal fields."""
        payload = {"title": "Updated Deal Title", "value": "75000"}

        response = client.put(
            f"/api/deals/{test_deal.id}",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Deal Title"
        assert data["value"] == "75000.00"
        assert data["currency"] == "USD"  # unchanged

    def test_update_deal_not_found(self, client, auth_headers):
        """Update returns 404 for nonexistent deal."""
        response = client.put(
            "/api/deals/9999",
            json={"title": "Test"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_deal_requires_auth(self, client, test_deal):
        """Update returns 401 without auth."""
        response = client.put(
            f"/api/deals/{test_deal.id}",
            json={"title": "Test"},
        )

        assert response.status_code == 401


class TestCRUDCycle:
    """Test full CRUD cycle for deals."""

    def test_crud_cycle(self, client, auth_headers, test_contact, test_stage):
        """Test complete create, read, update cycle."""
        # Create
        create_payload = {
            "title": "CRUD Test Deal",
            "value": "10000",
            "currency": "USD",
            "contact_id": test_contact.id,
            "stage_id": test_stage.id,
        }
        create_response = client.post(
            "/api/deals", json=create_payload, headers=auth_headers
        )
        assert create_response.status_code == 201
        deal_id = create_response.json()["id"]

        # Read
        get_response = client.get(f"/api/deals/{deal_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "CRUD Test Deal"

        # Update
        update_payload = {"title": "Updated CRUD Deal", "value": "20000"}
        update_response = client.put(
            f"/api/deals/{deal_id}",
            json=update_payload,
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated CRUD Deal"
        assert update_response.json()["value"] == "20000.00"

        # Verify update persisted
        verify_response = client.get(f"/api/deals/{deal_id}")
        assert verify_response.json()["title"] == "Updated CRUD Deal"
