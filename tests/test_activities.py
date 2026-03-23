"""Tests for activities endpoints."""
import pytest
from datetime import datetime

from app.auth.utils import create_access_token, hash_password
from app.models.user import User
from app.models.contact import Contact
from app.models.company import Company
from app.models.deal import Deal
from app.models.deal_stage import DealStage
from app.models.activity import Activity


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


@pytest.fixture
def test_activity(db, test_deal, test_contact):
    """Create a test activity."""
    activity = Activity(
        type="call",
        subject="Initial discovery call",
        notes="Discussed requirements",
        occurred_at=datetime(2024, 1, 15, 10, 0, 0),
        deal_id=test_deal.id,
        contact_id=test_contact.id,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


class TestListActivities:
    """Tests for GET /api/deals/{deal_id}/activities."""

    def test_list_activities_empty(self, client, test_deal):
        """List returns empty when no activities exist."""
        response = client.get(f"/api/deals/{test_deal.id}/activities")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_activities_with_data(self, client, test_deal, test_activity):
        """List returns activities for deal."""
        response = client.get(f"/api/deals/{test_deal.id}/activities")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["subject"] == "Initial discovery call"
        assert data["items"][0]["type"] == "call"
        assert data["items"][0]["deal_id"] == test_deal.id

    def test_list_activities_deal_not_found(self, client):
        """List returns 404 for nonexistent deal."""
        response = client.get("/api/deals/9999/activities")

        assert response.status_code == 404


class TestCreateActivity:
    """Tests for POST /api/deals/{deal_id}/activities."""

    def test_create_activity_success(self, client, auth_headers, test_deal):
        """Create returns new activity with 201."""
        payload = {
            "type": "meeting",
            "subject": "Demo presentation",
            "notes": "Showed product features",
            "occurred_at": "2024-02-01T14:00:00",
        }

        response = client.post(
            f"/api/deals/{test_deal.id}/activities",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "meeting"
        assert data["subject"] == "Demo presentation"
        assert data["notes"] == "Showed product features"
        assert data["deal_id"] == test_deal.id
        assert "id" in data
        assert "created_at" in data

    def test_create_activity_all_types(self, client, auth_headers, test_deal):
        """Create works for all activity types."""
        for activity_type in ["call", "email", "meeting", "note"]:
            payload = {
                "type": activity_type,
                "subject": f"Test {activity_type}",
                "occurred_at": "2024-02-01T14:00:00",
            }

            response = client.post(
                f"/api/deals/{test_deal.id}/activities",
                json=payload,
                headers=auth_headers,
            )

            assert response.status_code == 201
            assert response.json()["type"] == activity_type

    def test_create_activity_invalid_type(self, client, auth_headers, test_deal):
        """Create returns 422 for invalid activity type."""
        payload = {
            "type": "invalid_type",
            "subject": "Test",
            "occurred_at": "2024-02-01T14:00:00",
        }

        response = client.post(
            f"/api/deals/{test_deal.id}/activities",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_create_activity_deal_not_found(self, client, auth_headers):
        """Create returns 404 for nonexistent deal."""
        payload = {
            "type": "call",
            "subject": "Test call",
            "occurred_at": "2024-02-01T14:00:00",
        }

        response = client.post(
            "/api/deals/9999/activities",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_create_activity_requires_auth(self, client, test_deal):
        """Create returns 401 without auth."""
        payload = {
            "type": "call",
            "subject": "Test call",
            "occurred_at": "2024-02-01T14:00:00",
        }

        response = client.post(
            f"/api/deals/{test_deal.id}/activities",
            json=payload,
        )

        assert response.status_code == 401

    def test_create_activity_links_contact(self, client, auth_headers, test_deal, test_contact):
        """Create automatically links activity to deal's contact."""
        payload = {
            "type": "email",
            "subject": "Follow-up email",
            "occurred_at": "2024-02-01T14:00:00",
        }

        response = client.post(
            f"/api/deals/{test_deal.id}/activities",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["contact_id"] == test_contact.id
