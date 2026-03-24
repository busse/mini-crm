# Demo Repo Spec: `mini-crm`

## Purpose

A purpose-built small CRM application used as the shared codebase for the *Stop Typing, Start Orchestrating* workshop. Every demo and exercise runs against this repo. It needs to be instantly understandable, realistically imperfect, and rich enough to support feature additions across all workshop blocks.

**Companion docs:** [workshop-run-of-show.md](workshop-run-of-show.md) | [workshop-approach.md](workshop-approach.md)

---

## Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Language | Python 3.11+ | Broadest comfort zone for a data-summit audience |
| Framework | FastAPI | Auto-generated OpenAPI docs, async-friendly, minimal boilerplate |
| Database | SQLite via SQLAlchemy | Zero install (no DB server), single file, easy to reset |
| Migrations | Alembic | Realistic project structure without heavyweight infra |
| Frontend | Vanilla JS + HTML templates (Jinja2) | No build step, no React/Node dependency, accessible to all skill levels |
| CSS | Simple utility CSS (e.g., Pico CSS or classless) | Looks decent without requiring framework knowledge |
| Tests | pytest + httpx (async test client) | Standard Python testing, ~70% coverage target |
| Seed data | Python script (`scripts/seed.py`) | Populates realistic sample data for demos |

### Why not TypeScript/Node?

Python wins for this audience. A data summit crowd is more likely to read Python fluently. SQLite means zero infrastructure. FastAPI's type hints give Claude Code strong signals for code generation. The tradeoff (less natural frontend story) is acceptable because the frontend is intentionally thin.

---

## Data Model

```
┌──────────────┐     ┌──────────────┐
│   companies  │     │   contacts   │
├──────────────┤     ├──────────────┤
│ id           │◄────│ company_id   │
│ name         │     │ id           │
│ industry     │     │ first_name   │
│ website      │     │ last_name    │
│ created_at   │     │ email        │
│ updated_at   │     │ phone        │
└──────────────┘     │ role         │
                     │ created_at   │
                     │ updated_at   │
                     └──────┬───────┘
                            │
┌──────────────┐     ┌──────┴───────┐     ┌──────────────┐
│  deal_stages │     │    deals     │     │  activities  │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ id           │◄────│ stage_id     │     │ id           │
│ name         │     │ id           │     │ deal_id (FK) │
│ display_order│     │ contact_id   │────►│ contact_id   │
│ is_closed    │     │ title        │     │ type         │
└──────────────┘     │ value        │     │ subject      │
                     │ currency     │     │ notes        │
                     │ expected_close│    │ occurred_at  │
                     │ created_at   │     │ created_at   │
                     │ updated_at   │     └──────────────┘
                     └──────────────┘
                            │
                     ┌──────┴───────┐
                     │  deal_tags   │     ┌──────────────┐
                     ├──────────────┤     │    tags      │
                     │ deal_id      │────►├──────────────┤
                     │ tag_id       │     │ id           │
                     └──────────────┘     │ name         │
                                          │ color        │
┌──────────────┐                          └──────────────┘
│    users     │
├──────────────┤
│ id           │
│ username     │
│ email        │
│ hashed_pw    │
│ is_active    │
│ created_at   │
└──────────────┘
```

**Models: 7** — companies, contacts, deals, deal_stages, activities, tags, users
**Join table: 1** — deal_tags

---

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Returns JWT token |
| GET | `/auth/me` | Current user info |

### Contacts
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/contacts` | List contacts (paginated) |
| GET | `/api/contacts/{id}` | Get contact with company and deals |
| POST | `/api/contacts` | Create contact |
| PUT | `/api/contacts/{id}` | Update contact |
| DELETE | `/api/contacts/{id}` | Delete contact |

### Companies
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/companies` | List companies (paginated) |
| GET | `/api/companies/{id}` | Get company with contacts |
| POST | `/api/companies` | Create company |
| PUT | `/api/companies/{id}` | Update company |

### Deals
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/deals` | List deals (paginated, filterable by stage) |
| GET | `/api/deals/{id}` | Get deal with contact, activities, tags |
| POST | `/api/deals` | Create deal |
| PUT | `/api/deals/{id}` | Update deal (including stage changes) |
| PATCH | `/api/deals/{id}/stage` | Move deal to new stage |

### Activities
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/deals/{id}/activities` | List activities for a deal |
| POST | `/api/deals/{id}/activities` | Log an activity |

### Pipeline (reporting)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/pipeline/summary` | Deal count and value by stage |

### Tags
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tags` | List all tags |
| POST | `/api/deals/{id}/tags` | Add tag to deal |
| DELETE | `/api/deals/{id}/tags/{tag_id}` | Remove tag from deal |

**Total: ~20 endpoints** — enough to explore, not so many that it's overwhelming.

---

## Project Structure

```
mini-crm/
├── README.md
├── pyproject.toml
├── alembic.ini
├── alembic/
│   └── versions/
│       └── 001_initial.py
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app creation, middleware, startup
│   ├── config.py                # Settings via pydantic-settings
│   ├── database.py              # SQLAlchemy engine, session factory
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py            # /auth routes
│   │   ├── dependencies.py      # get_current_user dependency
│   │   └── utils.py             # JWT creation, password hashing
│   ├── models/
│   │   ├── __init__.py          # Imports all models for Alembic
│   │   ├── company.py
│   │   ├── contact.py
│   │   ├── deal.py
│   │   ├── deal_stage.py
│   │   ├── activity.py
│   │   ├── tag.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── company.py           # Pydantic request/response models
│   │   ├── contact.py
│   │   ├── deal.py
│   │   ├── activity.py
│   │   └── tag.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── companies.py
│   │   ├── contacts.py
│   │   ├── deals.py
│   │   ├── activities.py
│   │   ├── pipeline.py
│   │   └── tags.py
│   ├── services/                # Business logic (optional layer)
│   │   ├── __init__.py
│   │   └── deal_service.py      # Stage transition logic
│   └── templates/
│       ├── base.html
│       ├── dashboard.html       # Pipeline view
│       ├── contacts.html        # Contact list
│       └── deal_detail.html     # Single deal view
├── scripts/
│   ├── seed.py                  # Populate sample data
│   └── reset_db.py              # Drop and recreate (for workshop resets)
├── tests/
│   ├── conftest.py              # Fixtures: test client, test DB, auth headers
│   ├── test_contacts.py
│   ├── test_companies.py
│   ├── test_deals.py
│   ├── test_activities.py
│   ├── test_pipeline.py
│   └── test_auth.py
├── static/
│   ├── style.css
│   └── app.js                   # Minimal frontend interactions
├── .claude/
│   └── CLAUDE.md                # Project-level instructions for Claude Code
└── .gitignore
```

**File count: ~40** | **Estimated LOC: 2,000–2,500**

---

## Seed Data

The seed script should generate data that feels real and supports demos:

- **3 companies:** "Acme Corp" (technology), "Greenfield Solar" (energy), "Meridian Health" (healthcare)
- **8-10 contacts:** Distributed across companies, with realistic names and roles (CEO, VP Sales, Engineer, etc.)
- **6-8 deals:** Spread across pipeline stages, a mix of values ($5K–$500K), some with expected close dates in the past (overdue)
- **15-20 activities:** Mix of types: `call`, `email`, `meeting`, `note` — spread across deals with realistic timestamps over the past 60 days
- **5 deal stages:** Lead → Qualified → Proposal → Negotiation → Closed Won / Closed Lost
- **5-6 tags:** "enterprise", "startup", "referral", "hot-lead", "renewal", "at-risk"
- **2 users:** `admin` / `password123`, `demo` / `demo123`

The data should be deterministic (seeded random) so every workshop attendee sees the same state.

---

## Intentional Imperfections

These are seeded into the repo by design, so exercises produce satisfying discoveries:

### For Block 2 (Navigation / "Find bugs")
1. **Missing input validation** on `POST /api/contacts` — no email format check, no length limits on `first_name`
2. **N+1 query** in `GET /api/deals` — loads contact and company via lazy loading instead of joined eager loading
3. **TODO comment** in `deal_service.py`: `# TODO: send notification when deal moves to Closed Won` — breadcrumb for Block 4 exercise
4. **Inconsistent error handling** — some routers return 404 with a message, others raise bare `HTTPException` with no detail

### For Block 3 (Prompt Structuring)
5. **No search endpoint exists** — the vague-vs-structured demo asks Claude to *add* search, so it shouldn't already be there
6. **No favorites/bookmarking** — exercise feature to add via structured prompt

### For Block 4 (Orchestration)
7. **No email notification system** — the demo feature to build end-to-end
8. **Test coverage gap** — `test_deals.py` covers CRUD but not stage transitions, so Claude's implementation will surface a real test failure to debug

### For Block 5 (Multi-Agent)
9. **No CSV import/export** — natural parallel-sessions feature (backend endpoint + frontend upload form)
10. **No reporting dashboard** — `GET /api/pipeline/summary` exists but the frontend `dashboard.html` only shows a placeholder; good for a multi-agent build

---

## Exercise Mapping

| Block | Exercise | Target area in repo | What attendees do |
|-------|----------|--------------------|--------------------|
| 2 | Navigate the CRM | Whole repo | Ask Claude Code to explain the project, trace request lifecycle, find auth, spot code smells |
| 3 | Add favorites | `contacts`, `schemas`, `routers`, `tests` | Write structured prompt to add a "favorite contacts" feature |
| 3 (demo) | Add search | `contacts` router | Live demo: vague prompt vs. structured prompt |
| 4 | Build a feature | Varies (rate limiting, CSV export, admin role, notifications) | Explore → Plan → Implement → Test → Fix loop |
| 4 (demo) | Email notifications | `deal_service`, new `notifications` module | End-to-end orchestration demo |
| 5A | Writer/Reviewer | Any feature from Block 4 | Implement in one session, review in another |
| 5B | Subagent research | `auth/`, `routers/` | Subagent investigates patterns, main session implements |
| 5C | Parallel build | `routers/` + `templates/` | Backend in one session, frontend in another |

---

## Setup Requirements

### For attendees (pre-work)
```bash
# Prerequisites
python --version    # 3.11+
claude --version    # Claude Code installed and authenticated

# Clone and setup
git clone <repo-url>
cd mini-crm
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Initialize database with sample data
python scripts/seed.py

# Verify everything works
pytest                    # Should see ~70% pass rate (intentional gaps)
uvicorn app.main:app      # Visit http://localhost:8000
```

### For presenter (before workshop)
```bash
# Reset to clean state
python scripts/reset_db.py
python scripts/seed.py

# Verify all demos work with current Claude Code version
# Pre-cache any large dependencies
```

### Reset during workshop
If an attendee gets their repo into a bad state:
```bash
git checkout main
git clean -fd
python scripts/reset_db.py && python scripts/seed.py
```

---

## CLAUDE.md (Shipped with repo)

The repo ships with a `.claude/CLAUDE.md` that gives Claude Code project context:

```markdown
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
```

---

## Scope Guard

**In scope:**
- All models, routes, schemas, and tests listed above
- Seed data script
- Basic frontend templates (functional, not polished)
- Project-level CLAUDE.md
- README with setup instructions

**Out of scope (do not build):**
- WebSocket or real-time features
- File upload handling (attendees add this as an exercise)
- Email sending infrastructure (attendees add this as an exercise)
- Deployment config (Docker, CI/CD)
- Admin panel
- Role-based access control beyond basic auth (attendees can add this as an exercise)

---

## Open Questions

- [ ] **Repo hosting:** Public GitHub repo under Busse's account? Anthropic org? Workshop-specific org?
- [ ] **License:** MIT for maximum simplicity?
- [ ] **Python version floor:** 3.11 or 3.12? (3.11 is safer for attendee compatibility)
- [ ] **Include `.claude/commands/`?** Could ship a sample slash command to demonstrate Block 4 stretch goal, but might be confusing pre-workshop

---

*Last updated: 2026-03-11*
