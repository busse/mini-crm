"""Tests for tags endpoints."""
import pytest

from app.auth.utils import create_access_token, hash_password
from app.models.user import User
from app.models.contact import Contact
from app.models.company import Company
from app.models.deal import Deal
from app.models.deal_stage import DealStage
from app.models.tag import Tag


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
def test_tag(db):
    """Create a test tag."""
    tag = Tag(
        name="Hot Lead",
        color="#ff0000",
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@pytest.fixture
def test_tags(db):
    """Create multiple test tags."""
    tags = [
        Tag(name="Enterprise", color="#0000ff"),
        Tag(name="Hot Lead", color="#ff0000"),
        Tag(name="Renewal", color="#00ff00"),
    ]
    db.add_all(tags)
    db.commit()
    for tag in tags:
        db.refresh(tag)
    return tags


class TestListTags:
    """Tests for GET /api/tags."""

    def test_list_tags_empty(self, client):
        """List returns empty when no tags exist."""
        response = client.get("/api/tags")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_tags_with_data(self, client, test_tags):
        """List returns all tags sorted by name."""
        response = client.get("/api/tags")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        # Check alphabetical ordering
        names = [t["name"] for t in data["items"]]
        assert names == ["Enterprise", "Hot Lead", "Renewal"]


class TestAddTagToDeal:
    """Tests for POST /api/deals/{deal_id}/tags."""

    def test_add_tag_success(self, client, auth_headers, test_deal, test_tag):
        """Add tag returns the tag with 201."""
        payload = {"tag_id": test_tag.id}

        response = client.post(
            f"/api/deals/{test_deal.id}/tags",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == test_tag.id
        assert data["name"] == "Hot Lead"
        assert data["color"] == "#ff0000"

    def test_add_tag_deal_not_found(self, client, auth_headers, test_tag):
        """Add tag returns 404 for nonexistent deal."""
        payload = {"tag_id": test_tag.id}

        response = client.post(
            "/api/deals/9999/tags",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Deal not found"

    def test_add_tag_tag_not_found(self, client, auth_headers, test_deal):
        """Add tag returns 404 for nonexistent tag."""
        payload = {"tag_id": 9999}

        response = client.post(
            f"/api/deals/{test_deal.id}/tags",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Tag not found"

    def test_add_tag_duplicate(self, client, auth_headers, db, test_deal, test_tag):
        """Add tag returns 409 if tag already attached."""
        # First add the tag
        test_deal.tags.append(test_tag)
        db.commit()

        # Try to add again
        payload = {"tag_id": test_tag.id}

        response = client.post(
            f"/api/deals/{test_deal.id}/tags",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Tag already attached to deal"

    def test_add_tag_requires_auth(self, client, test_deal, test_tag):
        """Add tag returns 401 without auth."""
        payload = {"tag_id": test_tag.id}

        response = client.post(
            f"/api/deals/{test_deal.id}/tags",
            json=payload,
        )

        assert response.status_code == 401


class TestRemoveTagFromDeal:
    """Tests for DELETE /api/deals/{deal_id}/tags/{tag_id}."""

    def test_remove_tag_success(self, client, auth_headers, db, test_deal, test_tag):
        """Remove tag returns 204."""
        # First add the tag
        test_deal.tags.append(test_tag)
        db.commit()

        response = client.delete(
            f"/api/deals/{test_deal.id}/tags/{test_tag.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify tag was removed
        db.refresh(test_deal)
        assert test_tag not in test_deal.tags

    def test_remove_tag_deal_not_found(self, client, auth_headers, test_tag):
        """Remove tag returns 404 for nonexistent deal."""
        response = client.delete(
            f"/api/deals/9999/tags/{test_tag.id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Deal not found"

    def test_remove_tag_tag_not_found(self, client, auth_headers, test_deal):
        """Remove tag returns 404 for nonexistent tag."""
        response = client.delete(
            f"/api/deals/{test_deal.id}/tags/9999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Tag not found"

    def test_remove_tag_not_attached(self, client, auth_headers, test_deal, test_tag):
        """Remove tag returns 404 if tag not attached to deal."""
        response = client.delete(
            f"/api/deals/{test_deal.id}/tags/{test_tag.id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Tag not attached to deal"

    def test_remove_tag_requires_auth(self, client, db, test_deal, test_tag):
        """Remove tag returns 401 without auth."""
        # First add the tag
        test_deal.tags.append(test_tag)
        db.commit()

        response = client.delete(
            f"/api/deals/{test_deal.id}/tags/{test_tag.id}",
        )

        assert response.status_code == 401


class TestDealTagsCycle:
    """Test full add/remove cycle for deal tags."""

    def test_add_remove_cycle(self, client, auth_headers, db, test_deal, test_tags):
        """Test adding multiple tags and removing one."""
        tag1, tag2, tag3 = test_tags

        # Add two tags
        for tag in [tag1, tag2]:
            response = client.post(
                f"/api/deals/{test_deal.id}/tags",
                json={"tag_id": tag.id},
                headers=auth_headers,
            )
            assert response.status_code == 201

        # Verify deal has both tags via get_deal
        response = client.get(f"/api/deals/{test_deal.id}")
        assert response.status_code == 200
        deal_tags = response.json()["tags"]
        assert len(deal_tags) == 2

        # Remove one tag
        response = client.delete(
            f"/api/deals/{test_deal.id}/tags/{tag1.id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verify only one tag remains
        response = client.get(f"/api/deals/{test_deal.id}")
        deal_tags = response.json()["tags"]
        assert len(deal_tags) == 1
        assert deal_tags[0]["id"] == tag2.id
