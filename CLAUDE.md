# mini-crm

A small CRM application built with Python, FastAPI, and SQLite.

## Quick Reference

- **Run server:** `uvicorn app.main:app --reload`
- **Run tests:** `pytest` (or `pytest -x` to stop on first failure)
- **Seed database:** `python scripts/seed.py`
- **Reset database:** `python scripts/reset_db.py && python scripts/seed.py`

## Architecture

- FastAPI app in `app/main.py`, routers in `app/routers/`
- SQLAlchemy models in `app/models/`, Pydantic schemas in `app/schemas/`
- Auth via JWT tokens — see `app/auth/`
- SQLite database at `data/crm.db`
- Templates in `app/templates/`, static files in `static/`

## Conventions

- All API routes are prefixed with `/api/` except auth (`/auth/`)
- Routers use dependency injection for DB sessions and current user
- Tests use a separate in-memory SQLite database (see `tests/conftest.py`)
- Pagination follows `?page=1&per_page=20` pattern
- Dates are ISO 8601 format

## Known Issues

- Search is not yet implemented
- Dashboard shows placeholder data
- Some endpoints lack input validation
