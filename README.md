# mini-crm

A small CRM application built with Python, FastAPI, and SQLite.

## Quick Start

```bash
git clone <repo-url> && cd mini-crm
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

Open http://localhost:8000 — API docs at http://localhost:8000/docs

## Tests

```bash
pytest                # run all tests
pytest -x             # stop on first failure
pytest --cov=app      # with coverage
```

## Project Structure

```
app/
├── auth/           # JWT authentication
├── models/         # SQLAlchemy models
├── routers/        # API endpoints
├── schemas/        # Pydantic schemas
├── services/       # Business logic
├── templates/      # Jinja2 templates
└── main.py         # FastAPI app
scripts/            # seed.py, reset_db.py
tests/              # pytest test suite
data/               # SQLite database (crm.db)
```

## API Endpoints

| Resource   | Endpoints                                      |
|------------|------------------------------------------------|
| Auth       | `POST /auth/login`, `GET /auth/me`             |
| Contacts   | `GET/POST /api/contacts`, `GET/PUT/DELETE /api/contacts/{id}` |
| Companies  | `GET/POST /api/companies`, `GET/PUT/DELETE /api/companies/{id}` |
| Deals      | `GET/POST /api/deals`, `GET/PUT/DELETE /api/deals/{id}`, `PATCH /api/deals/{id}/stage` |
| Activities | `GET/POST /api/activities`, `GET /api/deals/{id}/activities` |
| Tags       | `GET/POST /api/tags`, `POST/DELETE /api/deals/{id}/tags/{tag_id}` |
| Pipeline   | `GET /api/pipeline/stages`                     |

All `/api/*` endpoints require JWT authentication via `Authorization: Bearer <token>`.
