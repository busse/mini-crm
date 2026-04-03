# mini-crm

A small CRM application built with Python, FastAPI, and SQLite.

## Quick Start

Requires **Python 3.10+**

```bash
git clone <repo-url> && cd mini-crm
python3 scripts/check_python.py          # verify Python version
python3 -m venv .venv && source .venv/bin/activate
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

## Troubleshooting

**Wrong Python version?**
Run `python3 --version`. You need 3.10 or newer.

- **macOS (Homebrew):** `brew install python@3.12` then use `python3.12 -m venv .venv`
- **Ubuntu / Debian:** `sudo apt install python3.12 python3.12-venv`
- **pyenv:** `pyenv install 3.12 && pyenv local 3.12`
- **Windows:** Download from https://www.python.org/downloads/

**`pip install` fails with "requires-python"?**
Your Python is too old. See above.

**`ModuleNotFoundError: No module named 'venv'`?**
On Ubuntu/Debian: `sudo apt install python3.X-venv` (replace `3.X` with your version).
