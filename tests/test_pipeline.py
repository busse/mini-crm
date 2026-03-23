"""Tests for pipeline endpoints."""
import pytest

from app.models.deal import Deal
from app.models.deal_stage import DealStage
from app.models.contact import Contact
from app.models.company import Company


@pytest.fixture
def test_company(db):
    """Create a test company."""
    company = Company(
        name="Acme Corp",
        industry="Technology",
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
        company_id=test_company.id,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@pytest.fixture
def test_stages(db):
    """Create test deal stages."""
    stages = [
        DealStage(name="Lead", display_order=1, is_closed=False),
        DealStage(name="Qualified", display_order=2, is_closed=False),
        DealStage(name="Proposal", display_order=3, is_closed=False),
        DealStage(name="Closed Won", display_order=4, is_closed=True),
        DealStage(name="Closed Lost", display_order=5, is_closed=True),
    ]
    db.add_all(stages)
    db.commit()
    for stage in stages:
        db.refresh(stage)
    return stages


class TestListStages:
    """Tests for GET /api/pipeline/stages."""

    def test_list_stages_empty(self, client):
        """List returns empty when no stages exist."""
        response = client.get("/api/pipeline/stages")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_stages_returns_all(self, client, test_stages):
        """List returns all stages ordered by display_order."""
        response = client.get("/api/pipeline/stages")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 5

        names = [s["name"] for s in data["items"]]
        assert names == ["Lead", "Qualified", "Proposal", "Closed Won", "Closed Lost"]

    def test_list_stages_includes_deal_counts(self, client, db, test_stages, test_contact):
        """List returns stages with accurate deal counts."""
        lead_stage, qualified_stage, proposal_stage, _, _ = test_stages

        deals = [
            Deal(title="Deal 1", value=1000, contact_id=test_contact.id, stage_id=lead_stage.id),
            Deal(title="Deal 2", value=2000, contact_id=test_contact.id, stage_id=lead_stage.id),
            Deal(title="Deal 3", value=3000, contact_id=test_contact.id, stage_id=qualified_stage.id),
        ]
        db.add_all(deals)
        db.commit()

        response = client.get("/api/pipeline/stages")

        assert response.status_code == 200
        data = response.json()

        stages_by_name = {s["name"]: s for s in data["items"]}
        assert stages_by_name["Lead"]["deal_count"] == 2
        assert stages_by_name["Qualified"]["deal_count"] == 1
        assert stages_by_name["Proposal"]["deal_count"] == 0
        assert stages_by_name["Closed Won"]["deal_count"] == 0
        assert stages_by_name["Closed Lost"]["deal_count"] == 0

    def test_list_stages_includes_closed_flag(self, client, test_stages):
        """List returns is_closed flag for each stage."""
        response = client.get("/api/pipeline/stages")

        assert response.status_code == 200
        data = response.json()

        stages_by_name = {s["name"]: s for s in data["items"]}
        assert stages_by_name["Lead"]["is_closed"] is False
        assert stages_by_name["Qualified"]["is_closed"] is False
        assert stages_by_name["Closed Won"]["is_closed"] is True
        assert stages_by_name["Closed Lost"]["is_closed"] is True
