"""FastAPI application creation, middleware, and startup configuration."""
import math
from pathlib import Path

from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.auth.router import router as auth_router
from app.routers.contacts import router as contacts_router
from app.routers.companies import router as companies_router
from app.routers.deals import router as deals_router
from app.routers.activities import router as activities_router
from app.routers.tags import router as tags_router
from app.database import get_db
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.activity import Activity

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="Mini CRM", version="0.1.0")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")

app.include_router(auth_router)
app.include_router(contacts_router)
app.include_router(companies_router)
app.include_router(deals_router)
app.include_router(activities_router)
app.include_router(tags_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
def root():
    """Redirect root to dashboard."""
    return RedirectResponse(url="/dashboard")


@app.get("/dashboard")
def dashboard(request: Request):
    """Render dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/contacts")
def contacts_page(
    request: Request,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
):
    """Render contacts list page."""
    offset = (page - 1) * per_page
    total = db.query(Contact).count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1

    contacts_query = (
        db.query(Contact)
        .options(joinedload(Contact.company), joinedload(Contact.deals))
        .offset(offset)
        .limit(per_page)
        .all()
    )

    contacts = []
    for c in contacts_query:
        contacts.append({
            "id": c.id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email,
            "company_name": c.company.name if c.company else None,
            "role": c.role,
            "deal_count": len(c.deals),
        })

    return templates.TemplateResponse(
        "contacts.html",
        {
            "request": request,
            "contacts": contacts,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    )


@app.get("/deals")
def deals_page(
    request: Request,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
):
    """Render deals list page."""
    offset = (page - 1) * per_page
    total = db.query(Deal).count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1

    deals_query = (
        db.query(Deal)
        .options(
            joinedload(Deal.contact),
            joinedload(Deal.stage),
            joinedload(Deal.activities),
        )
        .offset(offset)
        .limit(per_page)
        .all()
    )

    deals = []
    for d in deals_query:
        contact_name = None
        if d.contact:
            contact_name = f"{d.contact.first_name} {d.contact.last_name}"
        deals.append({
            "id": d.id,
            "title": d.title,
            "value": d.value,
            "currency": d.currency,
            "stage_name": d.stage.name if d.stage else None,
            "contact_name": contact_name,
            "activity_count": len(d.activities),
        })

    return templates.TemplateResponse(
        "deals.html",
        {
            "request": request,
            "deals": deals,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    )


@app.get("/deals/{deal_id}")
def deal_detail_page(
    request: Request,
    deal_id: int,
    db: Session = Depends(get_db),
):
    """Render deal detail page."""
    deal = (
        db.query(Deal)
        .options(
            joinedload(Deal.contact),
            joinedload(Deal.stage),
            joinedload(Deal.tags),
        )
        .filter(Deal.id == deal_id)
        .first()
    )

    if deal is None:
        return templates.TemplateResponse(
            "deal_detail.html",
            {"request": request, "deal": None, "activities": []},
            status_code=404,
        )

    contact_name = None
    if deal.contact:
        contact_name = f"{deal.contact.first_name} {deal.contact.last_name}"

    activities = (
        db.query(Activity)
        .filter(Activity.deal_id == deal_id)
        .order_by(Activity.occurred_at.desc())
        .all()
    )

    deal_data = {
        "id": deal.id,
        "title": deal.title,
        "value": deal.value,
        "currency": deal.currency,
        "expected_close": deal.expected_close,
        "contact_name": contact_name,
        "stage_name": deal.stage.name if deal.stage else None,
        "tags": [{"name": t.name, "color": t.color} for t in deal.tags],
        "created_at": deal.created_at,
    }

    return templates.TemplateResponse(
        "deal_detail.html",
        {"request": request, "deal": deal_data, "activities": activities},
    )
