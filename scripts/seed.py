"""Seed database with deterministic demo data.

Populates the database with realistic sample data for demos.
All values are deterministic so every run produces identical results.
"""
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.auth.utils import hash_password
from app.database import SessionLocal
from app.models import (
    Activity,
    Company,
    Contact,
    Deal,
    DealStage,
    DealTag,
    Tag,
    User,
)


def get_base_date() -> date:
    """Return a fixed base date for deterministic data."""
    return date(2025, 3, 15)


def seed_users(db):
    """Create demo users."""
    users_data = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "hashed_pw": hash_password("password123"),
            "is_active": True,
        },
        {
            "username": "demo",
            "email": "demo@example.com",
            "hashed_pw": hash_password("demo123"),
            "is_active": True,
        },
    ]

    users = []
    for data in users_data:
        user = User(**data)
        db.add(user)
        users.append(user)

    db.flush()
    print(f"Created {len(users)} users")
    return users


def seed_stages(db):
    """Create pipeline stages."""
    stages_data = [
        {"name": "Lead", "display_order": 1, "is_closed": False},
        {"name": "Qualified", "display_order": 2, "is_closed": False},
        {"name": "Proposal", "display_order": 3, "is_closed": False},
        {"name": "Negotiation", "display_order": 4, "is_closed": False},
        {"name": "Closed Won", "display_order": 5, "is_closed": True},
        {"name": "Closed Lost", "display_order": 6, "is_closed": True},
    ]

    stages = {}
    for data in stages_data:
        stage = DealStage(**data)
        db.add(stage)
        stages[data["name"]] = stage

    db.flush()
    print(f"Created {len(stages)} deal stages")
    return stages


def seed_companies(db):
    """Create sample companies."""
    companies_data = [
        {
            "name": "Acme Corp",
            "industry": "technology",
            "website": "https://acme.example.com",
        },
        {
            "name": "Greenfield Solar",
            "industry": "energy",
            "website": "https://greenfieldsolar.example.com",
        },
        {
            "name": "Meridian Health",
            "industry": "healthcare",
            "website": "https://meridianhealth.example.com",
        },
    ]

    companies = {}
    for data in companies_data:
        company = Company(**data)
        db.add(company)
        companies[data["name"]] = company

    db.flush()
    print(f"Created {len(companies)} companies")
    return companies


def seed_contacts(db, companies):
    """Create sample contacts."""
    contacts_data = [
        # Acme Corp
        {
            "first_name": "Jordan",
            "last_name": "Lee",
            "email": "jordan.lee@acme.example.com",
            "phone": "+1-555-0101",
            "role": "CTO",
            "company": "Acme Corp",
        },
        {
            "first_name": "Casey",
            "last_name": "Morgan",
            "email": "casey.morgan@acme.example.com",
            "phone": "+1-555-0102",
            "role": "VP Engineering",
            "company": "Acme Corp",
        },
        {
            "first_name": "Alex",
            "last_name": "Rivera",
            "email": "alex.rivera@acme.example.com",
            "phone": "+1-555-0103",
            "role": "Dev Lead",
            "company": "Acme Corp",
        },
        # Greenfield Solar
        {
            "first_name": "Sam",
            "last_name": "Patel",
            "email": "sam.patel@greenfieldsolar.example.com",
            "phone": "+1-555-0201",
            "role": "CEO",
            "company": "Greenfield Solar",
        },
        {
            "first_name": "Taylor",
            "last_name": "Kim",
            "email": "taylor.kim@greenfieldsolar.example.com",
            "phone": "+1-555-0202",
            "role": "VP Sales",
            "company": "Greenfield Solar",
        },
        {
            "first_name": "Jamie",
            "last_name": "Chen",
            "email": "jamie.chen@greenfieldsolar.example.com",
            "phone": "+1-555-0203",
            "role": "Operations",
            "company": "Greenfield Solar",
        },
        # Meridian Health
        {
            "first_name": "Morgan",
            "last_name": "Wells",
            "email": "morgan.wells@meridianhealth.example.com",
            "phone": "+1-555-0301",
            "role": "CFO",
            "company": "Meridian Health",
        },
        {
            "first_name": "Riley",
            "last_name": "Brooks",
            "email": "riley.brooks@meridianhealth.example.com",
            "phone": "+1-555-0302",
            "role": "Product Manager",
            "company": "Meridian Health",
        },
        {
            "first_name": "Drew",
            "last_name": "Simmons",
            "email": "drew.simmons@meridianhealth.example.com",
            "phone": "+1-555-0303",
            "role": "Data Analyst",
            "company": "Meridian Health",
        },
    ]

    contacts = {}
    for data in contacts_data:
        company_name = data.pop("company")
        contact = Contact(**data, company_id=companies[company_name].id)
        db.add(contact)
        full_name = f"{data['first_name']} {data['last_name']}"
        contacts[full_name] = contact

    db.flush()
    print(f"Created {len(contacts)} contacts")
    return contacts


def seed_tags(db):
    """Create deal tags."""
    tags_data = [
        {"name": "enterprise", "color": "#2563eb"},
        {"name": "startup", "color": "#16a34a"},
        {"name": "referral", "color": "#ca8a04"},
        {"name": "hot-lead", "color": "#dc2626"},
        {"name": "renewal", "color": "#7c3aed"},
        {"name": "at-risk", "color": "#ea580c"},
    ]

    tags = {}
    for data in tags_data:
        tag = Tag(**data)
        db.add(tag)
        tags[data["name"]] = tag

    db.flush()
    print(f"Created {len(tags)} tags")
    return tags


def seed_deals(db, stages, contacts, tags):
    """Create sample deals."""
    base_date = get_base_date()

    deals_data = [
        {
            "title": "Acme Platform Upgrade",
            "value": Decimal("120000.00"),
            "currency": "USD",
            "expected_close": base_date + timedelta(days=30),
            "contact": "Jordan Lee",
            "stage": "Negotiation",
            "tags": ["enterprise", "hot-lead"],
        },
        {
            "title": "Greenfield CRM Migration",
            "value": Decimal("45000.00"),
            "currency": "USD",
            "expected_close": base_date + timedelta(days=45),
            "contact": "Sam Patel",
            "stage": "Proposal",
            "tags": ["referral"],
        },
        {
            "title": "Meridian Data Pipeline",
            "value": Decimal("250000.00"),
            "currency": "USD",
            "expected_close": base_date + timedelta(days=60),
            "contact": "Morgan Wells",
            "stage": "Qualified",
            "tags": [],
        },
        {
            "title": "Acme DevOps Retainer",
            "value": Decimal("96000.00"),
            "currency": "USD",
            "expected_close": base_date + timedelta(days=90),
            "contact": "Casey Morgan",
            "stage": "Lead",
            "tags": [],
        },
        {
            "title": "Greenfield IoT Dashboard",
            "value": Decimal("35000.00"),
            "currency": "USD",
            "expected_close": base_date - timedelta(days=10),
            "contact": "Taylor Kim",
            "stage": "Closed Won",
            "tags": [],
        },
        {
            "title": "Meridian Compliance Audit",
            "value": Decimal("15000.00"),
            "currency": "USD",
            "expected_close": base_date - timedelta(days=5),
            "contact": "Riley Brooks",
            "stage": "Closed Lost",
            "tags": [],
        },
        {
            "title": "Acme Mobile App",
            "value": Decimal("180000.00"),
            "currency": "USD",
            "expected_close": base_date - timedelta(days=14),  # Overdue
            "contact": "Alex Rivera",
            "stage": "Proposal",
            "tags": ["enterprise", "at-risk"],
        },
    ]

    deals = {}
    for data in deals_data:
        contact_name = data.pop("contact")
        stage_name = data.pop("stage")
        tag_names = data.pop("tags")

        deal = Deal(
            **data,
            contact_id=contacts[contact_name].id,
            stage_id=stages[stage_name].id,
        )
        db.add(deal)
        db.flush()

        # Add tags
        for tag_name in tag_names:
            deal_tag = DealTag(deal_id=deal.id, tag_id=tags[tag_name].id)
            db.add(deal_tag)

        deals[data["title"]] = deal

    db.flush()
    print(f"Created {len(deals)} deals")
    return deals


def seed_activities(db, deals, contacts):
    """Create sample activities across deals."""
    base_date = get_base_date()

    activities_data = [
        # Acme Platform Upgrade activities
        {
            "type": "call",
            "subject": "Initial discovery call",
            "notes": "Discussed current platform limitations. Jordan mentioned they need better scalability for Q3 launch.",
            "occurred_at": datetime.combine(base_date - timedelta(days=45), datetime.min.time().replace(hour=10)),
            "deal": "Acme Platform Upgrade",
            "contact": "Jordan Lee",
        },
        {
            "type": "email",
            "subject": "Follow-up with technical requirements",
            "notes": "Sent detailed questionnaire about their infrastructure and integration needs.",
            "occurred_at": datetime.combine(base_date - timedelta(days=43), datetime.min.time().replace(hour=14)),
            "deal": "Acme Platform Upgrade",
            "contact": "Jordan Lee",
        },
        {
            "type": "meeting",
            "subject": "Technical deep-dive with engineering team",
            "notes": "Met with Jordan and Casey. Walked through architecture proposal. They had concerns about migration timeline.",
            "occurred_at": datetime.combine(base_date - timedelta(days=30), datetime.min.time().replace(hour=15)),
            "deal": "Acme Platform Upgrade",
            "contact": "Jordan Lee",
        },
        {
            "type": "note",
            "subject": "Internal: pricing strategy",
            "notes": "Discussed with team - recommend 15% volume discount given potential for DevOps retainer add-on.",
            "occurred_at": datetime.combine(base_date - timedelta(days=20), datetime.min.time().replace(hour=9)),
            "deal": "Acme Platform Upgrade",
            "contact": "Jordan Lee",
        },
        # Greenfield CRM Migration activities
        {
            "type": "call",
            "subject": "Referral introduction call",
            "notes": "Sam was referred by mutual contact at SolarTech conference. Looking to replace legacy CRM system.",
            "occurred_at": datetime.combine(base_date - timedelta(days=25), datetime.min.time().replace(hour=11)),
            "deal": "Greenfield CRM Migration",
            "contact": "Sam Patel",
        },
        {
            "type": "email",
            "subject": "Proposal draft sent",
            "notes": "Sent initial proposal with three tier options. Recommended mid-tier based on their team size.",
            "occurred_at": datetime.combine(base_date - timedelta(days=18), datetime.min.time().replace(hour=16)),
            "deal": "Greenfield CRM Migration",
            "contact": "Sam Patel",
        },
        {
            "type": "meeting",
            "subject": "Proposal review meeting",
            "notes": "Walked through proposal with Sam and Taylor. They want to add custom reporting module - updating quote.",
            "occurred_at": datetime.combine(base_date - timedelta(days=10), datetime.min.time().replace(hour=14)),
            "deal": "Greenfield CRM Migration",
            "contact": "Sam Patel",
        },
        # Meridian Data Pipeline activities
        {
            "type": "call",
            "subject": "Initial outreach",
            "notes": "Cold call converted to qualified lead. Morgan expressed pain points with current data infrastructure.",
            "occurred_at": datetime.combine(base_date - timedelta(days=35), datetime.min.time().replace(hour=10)),
            "deal": "Meridian Data Pipeline",
            "contact": "Morgan Wells",
        },
        {
            "type": "email",
            "subject": "Case study and references sent",
            "notes": "Sent healthcare industry case studies. They're particularly interested in HIPAA compliance aspects.",
            "occurred_at": datetime.combine(base_date - timedelta(days=32), datetime.min.time().replace(hour=9)),
            "deal": "Meridian Data Pipeline",
            "contact": "Morgan Wells",
        },
        {
            "type": "meeting",
            "subject": "Requirements gathering session",
            "notes": "2-hour workshop with Morgan and Drew. Documented current data flows and pain points.",
            "occurred_at": datetime.combine(base_date - timedelta(days=22), datetime.min.time().replace(hour=13)),
            "deal": "Meridian Data Pipeline",
            "contact": "Morgan Wells",
        },
        # Acme DevOps Retainer activities
        {
            "type": "email",
            "subject": "Service introduction",
            "notes": "Casey reached out after hearing about our DevOps services from Jordan. Sent service overview.",
            "occurred_at": datetime.combine(base_date - timedelta(days=15), datetime.min.time().replace(hour=11)),
            "deal": "Acme DevOps Retainer",
            "contact": "Casey Morgan",
        },
        {
            "type": "call",
            "subject": "Needs assessment call",
            "notes": "Discussed their CI/CD pain points. They're spending too much time on manual deployments.",
            "occurred_at": datetime.combine(base_date - timedelta(days=12), datetime.min.time().replace(hour=15)),
            "deal": "Acme DevOps Retainer",
            "contact": "Casey Morgan",
        },
        # Greenfield IoT Dashboard activities (Closed Won)
        {
            "type": "call",
            "subject": "Initial requirements call",
            "notes": "Taylor needs real-time monitoring dashboard for solar installations. 6-week timeline.",
            "occurred_at": datetime.combine(base_date - timedelta(days=55), datetime.min.time().replace(hour=10)),
            "deal": "Greenfield IoT Dashboard",
            "contact": "Taylor Kim",
        },
        {
            "type": "meeting",
            "subject": "Contract signing",
            "notes": "Signed contract and kicked off project. Implementation starts next week.",
            "occurred_at": datetime.combine(base_date - timedelta(days=12), datetime.min.time().replace(hour=14)),
            "deal": "Greenfield IoT Dashboard",
            "contact": "Taylor Kim",
        },
        # Meridian Compliance Audit activities (Closed Lost)
        {
            "type": "call",
            "subject": "Compliance requirements discussion",
            "notes": "Riley outlined their audit timeline and compliance gaps.",
            "occurred_at": datetime.combine(base_date - timedelta(days=40), datetime.min.time().replace(hour=11)),
            "deal": "Meridian Compliance Audit",
            "contact": "Riley Brooks",
        },
        {
            "type": "email",
            "subject": "Lost deal follow-up",
            "notes": "They went with an incumbent vendor due to existing relationship. Keep warm for future.",
            "occurred_at": datetime.combine(base_date - timedelta(days=5), datetime.min.time().replace(hour=16)),
            "deal": "Meridian Compliance Audit",
            "contact": "Riley Brooks",
        },
        # Acme Mobile App activities (Overdue)
        {
            "type": "meeting",
            "subject": "Mobile app kickoff",
            "notes": "Alex presented their mobile app vision. Cross-platform requirement for iOS and Android.",
            "occurred_at": datetime.combine(base_date - timedelta(days=50), datetime.min.time().replace(hour=10)),
            "deal": "Acme Mobile App",
            "contact": "Alex Rivera",
        },
        {
            "type": "email",
            "subject": "Revised timeline sent",
            "notes": "Sent updated proposal with extended timeline. Waiting for budget approval from leadership.",
            "occurred_at": datetime.combine(base_date - timedelta(days=8), datetime.min.time().replace(hour=14)),
            "deal": "Acme Mobile App",
            "contact": "Alex Rivera",
        },
    ]

    activities = []
    for data in activities_data:
        deal_title = data.pop("deal")
        contact_name = data.pop("contact")

        activity = Activity(
            **data,
            deal_id=deals[deal_title].id,
            contact_id=contacts[contact_name].id,
        )
        db.add(activity)
        activities.append(activity)

    db.flush()
    print(f"Created {len(activities)} activities")
    return activities


def main():
    """Run all seed functions in order."""
    print("Seeding database with demo data...")

    db = SessionLocal()
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("Database already has data. Run reset_db.py first to clear it.")
            return

        users = seed_users(db)
        stages = seed_stages(db)
        companies = seed_companies(db)
        contacts = seed_contacts(db, companies)
        tags = seed_tags(db)
        deals = seed_deals(db, stages, contacts, tags)
        activities = seed_activities(db, deals, contacts)

        db.commit()
        print("\nSeed complete!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
