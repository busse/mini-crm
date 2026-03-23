# mini-crm

A small CRM application built with Python, FastAPI, and SQLite.

## Setup

```bash
pip install -e ".[dev]"
alembic upgrade head
python scripts/seed.py
```

## Development

```bash
uvicorn app.main:app --reload
```

## Testing

```bash
pytest
```
