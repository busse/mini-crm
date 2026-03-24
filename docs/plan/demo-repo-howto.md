# HOWTO: Build the `mini-crm` Demo Repo with Claude Code

## Why this document exists

The workshop teaches the Explore → Plan → Implement → Commit loop. Building the demo repo with Claude Code means you've done the loop yourself, end to end, and can speak to it honestly. This guide walks through each phase with the exact prompts, the gotchas, and the places where you'll need to steer the agent rather than let it run.

**Estimated time:** 2–3 hours across multiple sessions.
**Prerequisite:** Claude Code installed and authenticated, Python 3.11+ available.
**Reference:** [demo-repo-spec.md](demo-repo-spec.md) for the full spec. Keep it open — you'll paste sections of it into prompts.

---

## Phase 0 — Project bootstrap

### 0.1 Create the repo and initialize Claude Code

```bash
mkdir mini-crm && cd mini-crm
git init
claude
```

Once inside Claude Code, run `/init` to generate the starter CLAUDE.md. Then immediately replace its contents with the CLAUDE.md from the spec (the "Shipped with repo" section of `demo-repo-spec.md`). This gives Claude the project context before it writes a single line.

### 0.2 Scaffold the project structure

This is the one phase where you give Claude a big prompt. Paste the full project structure tree from the spec and ask it to create the skeleton:

```
Create the project scaffolding for a Python FastAPI + SQLite CRM app.
Use this exact directory structure:

[paste the project structure tree from demo-repo-spec.md]

For each file, create it with a minimal placeholder — a docstring or comment
explaining its purpose, but no implementation yet. For pyproject.toml, include
these dependencies:

  fastapi, uvicorn, sqlalchemy, alembic, pydantic-settings,
  python-jose[cryptography], passlib[bcrypt], jinja2, httpx

Dev dependencies: pytest, pytest-asyncio, httpx

Use the src-less layout (import as `app`). Python 3.11+.
```

**Why the skeleton first:** You want Claude to have the full file tree in its context before it starts implementing. This mirrors the "Explore first" principle from the workshop — and it means every subsequent prompt can reference files by path.

### 0.3 Git checkpoint

```
Commit this scaffolding with the message "chore: project skeleton with placeholder files"
```

**Do this after every major phase.** Git checkpoints are your rewind points. If Claude goes sideways in Phase 3, you can `git checkout` back to the end of Phase 2 and re-prompt.

---

## Phase 1 — Data model and database

### 1.1 Models

Start a new task (`/clear` from the scaffold session) and work on models:

```
Implement the SQLAlchemy models in app/models/. Here is the data model:

- companies: id, name, industry, website, created_at, updated_at
- contacts: id, first_name, last_name, email, phone, role, company_id (FK to companies), created_at, updated_at
- deals: id, title, value (Numeric), currency (default "USD"), expected_close (Date), contact_id (FK), stage_id (FK to deal_stages), created_at, updated_at
- deal_stages: id, name, display_order (Integer), is_closed (Boolean, default False)
- activities: id, type (string: call/email/meeting/note), subject, notes (Text), occurred_at (DateTime), deal_id (FK), contact_id (FK), created_at
- tags: id, name, color (string, hex)
- deal_tags: deal_id + tag_id (composite PK, join table)
- users: id, username, email, hashed_pw, is_active (default True), created_at

Use SQLAlchemy 2.0 declarative style with mapped_column. Import all models
in app/models/__init__.py so Alembic can see them. Use a shared Base from
app/database.py.

Relationships:
- Company has many Contacts (back_populates)
- Contact has many Deals, has many Activities
- Deal has many Activities, many Tags (via deal_tags), belongs to DealStage
- DealStage has many Deals

After implementing, verify the models import cleanly:
  python -c "from app.models import *; print('Models OK')"
```

### 1.2 Database setup and Alembic

```
Set up the database layer:

1. In app/database.py: create SQLAlchemy async engine and session factory
   pointing to sqlite:///data/crm.db (create data/ dir if needed).
   Also create a sync engine for Alembic.

2. In app/config.py: use pydantic-settings to load DATABASE_URL
   (default: sqlite:///data/crm.db) and SECRET_KEY (default: "dev-secret-key-change-me").

3. Initialize Alembic: run `alembic init alembic`, configure alembic.ini
   and alembic/env.py to import our Base and models.

4. Generate the initial migration: alembic revision --autogenerate -m "initial"

5. Run the migration: alembic upgrade head

6. Verify: python -c "import sqlite3; conn = sqlite3.connect('data/crm.db'); print(conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall())"
```

**Steering note:** Claude sometimes makes Alembic async-compatible in an over-engineered way. If it starts pulling in `sqlalchemy.ext.asyncio` for the migration env, steer it back: "Use a simple synchronous engine in env.py. We don't need async migrations."

- As-built, this was needed

### 1.3 Git checkpoint

```
Commit with the message "feat: SQLAlchemy models and Alembic migration for 7-table CRM schema"
```

---

## Phase 2 — Auth layer

`/clear` and start fresh.

```
Implement JWT authentication in app/auth/:

1. app/auth/utils.py:
   - create_access_token(data: dict) → JWT string, 60-min expiry
   - verify_password(plain, hashed) → bool using passlib bcrypt
   - hash_password(plain) → hashed string

2. app/auth/dependencies.py:
   - get_db() → yields async SQLAlchemy session
   - get_current_user(token from Authorization: Bearer header) → User
     Raises 401 if token invalid or user not found

3. app/auth/router.py:
   - POST /auth/login: accepts username + password (form or JSON),
     returns {"access_token": "...", "token_type": "bearer"}
   - GET /auth/me: returns current user info (requires auth)

Use the SECRET_KEY from app/config.py.
After implementing, write tests in tests/test_auth.py covering:
  - Successful login
  - Login with wrong password (401)
  - /auth/me with valid token
  - /auth/me with no token (401)

Run the tests and fix any failures.
```

**Steering note:** Make sure `get_db` is set up as a FastAPI dependency that yields a session. Claude sometimes creates it as a raw function. Check the test fixtures in `conftest.py` — they should use an in-memory SQLite database, not the file-based one.

### Git checkpoint

```
Commit: "feat: JWT auth with login, token verification, and tests"
```

---

## Phase 3 — API routers (the bulk of the build)

This is the largest phase. Break it into sub-sessions to keep context clean. Use `/clear` between each router group.

### 3.1 Contacts CRUD

```
Implement the contacts API in app/routers/contacts.py and app/schemas/contact.py:

Schemas (Pydantic v2):
  - ContactCreate: first_name, last_name, email, phone (optional), role (optional), company_id (optional)
  - ContactUpdate: all fields optional
  - ContactResponse: all fields + id, company name (if present), created_at, updated_at

Endpoints:
  - GET /api/contacts — paginated list (?page=1&per_page=20), returns items + total count
  - GET /api/contacts/{id} — single contact with company and deals eager-loaded
  - POST /api/contacts — create (requires auth)
  - PUT /api/contacts/{id} — update (requires auth)
  - DELETE /api/contacts/{id} — delete (requires auth)

Register the router in app/main.py.

Write tests in tests/test_contacts.py:
  - List contacts (empty, then with data)
  - Create, read, update, delete cycle
  - 404 on nonexistent contact

Run pytest and fix failures.
```

**IMPORTANT — Intentional imperfection #1:** After Claude finishes and tests pass, go back and deliberately REMOVE any email validation on ContactCreate. If Claude added `EmailStr` or a regex validator, strip it out. The spec requires missing input validation on `POST /api/contacts` so Block 2's "find bugs" exercise works. You can do this manually or prompt:

```
Remove the email validation from ContactCreate — just make it a plain str
with no format checking. Also remove any length constraints on first_name
and last_name. Don't add them back. This is intentional.
```

### 3.2 Companies CRUD

```
Implement app/routers/companies.py and app/schemas/company.py:

Schemas:
  - CompanyCreate: name, industry (optional), website (optional)
  - CompanyUpdate: all optional
  - CompanyResponse: all fields + id, contact_count, created_at, updated_at

Endpoints:
  - GET /api/companies — paginated list
  - GET /api/companies/{id} — company with list of contacts
  - POST /api/companies — create (requires auth)
  - PUT /api/companies/{id} — update (requires auth)

Register in main.py. Tests in tests/test_companies.py. Run pytest.
```

### 3.3 Deals CRUD + stage transitions

```
Implement app/routers/deals.py, app/schemas/deal.py, and app/services/deal_service.py:

Schemas:
  - DealCreate: title, value, currency (default "USD"), expected_close (optional), contact_id, stage_id
  - DealUpdate: all optional
  - DealResponse: all fields + contact name, stage name, tags, activity count

Endpoints:
  - GET /api/deals — paginated, filterable by stage_id (?stage_id=X)
  - GET /api/deals/{id} — full deal with contact, activities, tags
  - POST /api/deals — create (requires auth)
  - PUT /api/deals/{id} — update (requires auth)
  - PATCH /api/deals/{id}/stage — move deal to new stage (requires auth)

deal_service.py:
  - move_to_stage(deal_id, new_stage_id) — validates stage exists, updates deal,
    returns updated deal.
  - Add a TODO comment on a blank line after the stage update:
    # TODO: send notification when deal moves to Closed Won
    (This is intentional — it's a breadcrumb for the Block 4 exercise.)

Tests in tests/test_deals.py:
  - CRUD cycle
  - Filter by stage
  - 404 on nonexistent deal

DO NOT write tests for stage transitions. Leave that gap intentionally.
The test file should have a comment: # TODO: add tests for PATCH stage endpoint

Run pytest.
```

**IMPORTANT — Intentional imperfection #2:** After Claude finishes, check `GET /api/deals`. The spec requires an N+1 query here. If Claude used `joinedload` or `selectinload`, replace it with lazy loading:

```
In the deals list endpoint, change the query to NOT use eager loading
for the contact and company relationships. Use plain lazy loading so
each deal triggers separate queries for contact and company. I know this
is an N+1 — it's intentional for the workshop.
```

**IMPORTANT — Intentional imperfection #4:** Check error handling across the routers you've built so far. Make it inconsistent on purpose:

```
I want inconsistent error handling across the routers:
- In contacts.py: return HTTPException(status_code=404, detail="Contact not found")
- In companies.py: return HTTPException(status_code=404, detail="Company not found")
- In deals.py: return HTTPException(status_code=404) with NO detail message
This inconsistency is intentional — workshop attendees should discover it.
```

### 3.4 Activities and Tags

```
Implement the remaining routers:

app/routers/activities.py + app/schemas/activity.py:
  - GET /api/deals/{deal_id}/activities — list activities for a deal
  - POST /api/deals/{deal_id}/activities — log activity (requires auth)
    Activity types: "call", "email", "meeting", "note"

app/routers/tags.py + app/schemas/tag.py:
  - GET /api/tags — list all tags
  - POST /api/deals/{deal_id}/tags — add tag to deal (requires auth)
  - DELETE /api/deals/{deal_id}/tags/{tag_id} — remove tag (requires auth)

Tests in test_activities.py and (add tag tests to test_deals.py or a new file).
Register both routers in main.py. Run pytest.
```

### 3.5 Pipeline summary

```
Implement app/routers/pipeline.py:

  - GET /api/pipeline/summary — returns JSON array of objects:
    { stage_name, stage_id, display_order, deal_count, total_value }
    Ordered by display_order. Include stages with 0 deals.

No schema file needed — just inline the response model.
Add a basic test in tests/test_pipeline.py. Run pytest.
```

### Git checkpoint

```
Commit: "feat: full API — contacts, companies, deals, activities, tags, pipeline"
```

---

## Phase 4 — Seed data

`/clear` and start fresh.

```
Implement scripts/seed.py that populates the database with realistic demo data.
Use deterministic values (no random) so every attendee sees the same state.

Data to create:

Users (2):
  - admin / password123
  - demo / demo123

Companies (3):
  - "Acme Corp", technology, https://acme.example.com
  - "Greenfield Solar", energy, https://greenfieldsolar.example.com
  - "Meridian Health", healthcare, https://meridianhealth.example.com

Deal stages (6):
  Lead (order 1) → Qualified (2) → Proposal (3) → Negotiation (4) → Closed Won (5, is_closed=True) → Closed Lost (6, is_closed=True)

Contacts (9):
  Distribute across companies. Use realistic names and roles:
    Acme: "Jordan Lee" (CTO), "Casey Morgan" (VP Engineering), "Alex Rivera" (Dev Lead)
    Greenfield: "Sam Patel" (CEO), "Taylor Kim" (VP Sales), "Jamie Chen" (Operations)
    Meridian: "Morgan Wells" (CFO), "Riley Brooks" (Product Manager), "Drew Simmons" (Data Analyst)

Deals (7):
  Spread across stages, mix of values. At least one overdue (expected_close in the past).
    "Acme Platform Upgrade" — $120,000, Negotiation, contact: Jordan Lee
    "Greenfield CRM Migration" — $45,000, Proposal, contact: Sam Patel
    "Meridian Data Pipeline" — $250,000, Qualified, contact: Morgan Wells
    "Acme DevOps Retainer" — $8,000/mo → $96,000, Lead, contact: Casey Morgan
    "Greenfield IoT Dashboard" — $35,000, Closed Won, contact: Taylor Kim
    "Meridian Compliance Audit" — $15,000, Closed Lost, contact: Riley Brooks
    "Acme Mobile App" — $180,000, Proposal, contact: Alex Rivera, expected_close 2 weeks ago (overdue)

Tags (6):
  enterprise (#2563eb), startup (#16a34a), referral (#ca8a04),
  hot-lead (#dc2626), renewal (#7c3aed), at-risk (#ea580c)

Tag some deals: "Acme Platform Upgrade" → enterprise, hot-lead;
  "Greenfield CRM Migration" → referral; "Acme Mobile App" → enterprise, at-risk

Activities (18):
  Mix of types across deals, timestamps spread over past 60 days.
  Include a variety: initial call, follow-up email, proposal meeting, etc.
  Make them feel like a real sales process narrative.

Also implement scripts/reset_db.py:
  - Drops all tables, re-runs alembic upgrade head, then runs seed.py

Test both scripts:
  python scripts/reset_db.py
  python scripts/seed.py
  python -c "import sqlite3; c=sqlite3.connect('data/crm.db'); print('Contacts:', c.execute('SELECT COUNT(*) FROM contacts').fetchone()[0])"
```

### Git checkpoint

```
Commit: "feat: seed data script with 3 companies, 9 contacts, 7 deals, 18 activities"
```

---

## Phase 5 — Frontend templates

`/clear` and start fresh. The frontend is intentionally thin.

```
Create minimal frontend templates using Jinja2 and Pico CSS (load from CDN).

app/templates/base.html:
  - HTML5 boilerplate, loads Pico CSS from CDN
  - Simple nav: Dashboard | Contacts | Deals
  - Content block

app/templates/dashboard.html:
  - Page title "Pipeline Dashboard"
  - Show a PLACEHOLDER message: "Dashboard visualizations coming soon."
  - Do NOT build a real chart or table. The placeholder is intentional —
    it's an exercise for workshop attendees to build in Block 5.

app/templates/contacts.html:
  - Table listing contacts: name, email, company, role
  - Links to deal count
  - Basic pagination

app/templates/deal_detail.html:
  - Deal title, value, stage, contact
  - Activity timeline (simple list)
  - Tags shown as colored badges

static/style.css:
  - Minimal overrides on top of Pico (if needed)

static/app.js:
  - Minimal: fetch helpers for API calls, nothing complex

Add template-serving routes in app/main.py:
  - GET / → redirect to /dashboard
  - GET /dashboard → renders dashboard.html
  - GET /contacts → renders contacts.html (fetches from API)
  - GET /deals/{id} → renders deal_detail.html

Run the server (uvicorn app.main:app --reload), visit http://localhost:8000,
verify the pages render. Take note of anything that looks broken.
```

### Git checkpoint

```
Commit: "feat: minimal Jinja2 frontend — dashboard placeholder, contacts list, deal detail"
```

---

## Phase 6 — Test suite tuning

`/clear` and start fresh. This is a polish pass.

```
Review the test suite and adjust coverage:

1. Run pytest --tb=short and show me the results.
2. Ensure we have tests for:
   - Auth (login, token, unauthorized)
   - Contacts (CRUD, pagination, 404)
   - Companies (CRUD, 404)
   - Deals (CRUD, filter by stage, 404)
   - Activities (create, list by deal)
   - Pipeline summary (returns all stages with counts)
   - Tags (add to deal, remove from deal, list)

3. Ensure we do NOT have tests for:
   - Deal stage transitions (PATCH endpoint) — this gap is intentional
   - Email validation on contacts — no validation exists, so no test
   - Dashboard rendering — it's a placeholder

4. Make sure conftest.py:
   - Uses in-memory SQLite (not file-based)
   - Creates a fresh DB per test session
   - Provides authenticated client fixture
   - Seeds deal_stages before tests that need them

Run pytest. Target: all tests pass, ~70% overall coverage.
We WANT some untested paths — that's by design.
```

### Git checkpoint

```
Commit: "test: tune test suite — ~70% coverage with intentional gaps"
```

---

## Phase 7 — Final polish and verification

### 7.1 README

```
Write a README.md for the mini-crm repo. Keep it short and practical:

  - One-line description
  - Quick start (clone, venv, install, seed, run)
  - How to run tests
  - Project structure overview (brief, not file-by-file)
  - API endpoint summary table
  - Link to the workshop if applicable

No badges, no lengthy explanations. Just enough that someone can clone
and be running in 2 minutes.
```

### 7.2 .gitignore

```
Create a .gitignore for a Python FastAPI project:
  __pycache__, *.pyc, .venv, data/*.db, .env, *.egg-info, dist, build, .pytest_cache
```

### 7.3 Verification pass

Run this yourself — don't delegate it to Claude:

```bash
# Clean slate
rm -rf data/ .venv
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Database
alembic upgrade head
python scripts/seed.py

# Tests
pytest -v

# Server
uvicorn app.main:app --reload
# Visit: http://localhost:8000
# Hit: http://localhost:8000/docs (FastAPI auto-docs)
# Verify: login works, contacts list loads, deal detail shows activities
```

### 7.4 Imperfection checklist

Walk through this list manually. If Claude "fixed" any of these during the build, re-introduce them:

| # | Imperfection | Where | How to verify |
|---|-------------|-------|---------------|
| 1 | No email validation on contact create | `app/schemas/contact.py` | POST a contact with `email: "not-an-email"` — should succeed |
| 2 | N+1 on deals list | `app/routers/deals.py` | Enable SQLAlchemy echo, GET `/api/deals`, count queries |
| 3 | TODO comment for notifications | `app/services/deal_service.py` | grep for "TODO: send notification" |
| 4 | Inconsistent 404s | `deals.py` vs `contacts.py` | GET nonexistent IDs, compare error responses |
| 5 | No search endpoint | all routers | Confirm no `/search` or `?q=` parameter exists |
| 6 | No favorites | contacts schema/router | Confirm no `is_favorite` field |
| 7 | No email notifications | whole repo | grep for `notification` — only the TODO comment |
| 8 | No stage transition tests | `tests/test_deals.py` | grep for "TODO: add tests for PATCH" |
| 9 | No CSV import/export | whole repo | grep for `csv` — nothing |
| 10 | Dashboard is placeholder | `app/templates/dashboard.html` | Visit `/dashboard` — sees "coming soon" |

### 7.5 Final commit and tag

```bash
git add -A
git commit -m "chore: README, gitignore, final polish"
git tag v1.0-workshop
```

---

## Session management tips

These are specific to building this repo with Claude Code, based on the patterns from the workshop itself:

**Use `/clear` between phases.** Each phase above is a natural session boundary. Don't try to build the whole thing in one conversation — context rot will degrade quality by Phase 4.

**Paste the spec, not instructions about the spec.** When starting a phase, paste the relevant section from `demo-repo-spec.md` directly into the prompt rather than describing what you want. Claude Code works better with concrete reference material.

**Don't fight Claude on style choices.** If it uses slightly different import ordering or names a variable differently than the spec, let it go — unless the difference affects a workshop exercise. Save your steering for the intentional imperfections.

**Use Plan Mode for Phase 3.** The routers phase is the most complex. For each router, start in Plan Mode, review the plan, then switch to normal mode for implementation. This mirrors what you'll demo in Block 4.

**Verify after every phase, not just at the end.** Run `pytest` and `uvicorn` after each git checkpoint. Fixing a broken test in Phase 3 is easy; finding it in Phase 7 means debugging through 20 files.

**Keep a scratch notes file.** As you build, jot down any moments where you had to steer Claude, where it surprised you, or where it made a mistake you had to correct. These are gold for your speaker notes — real anecdotes from the exact workflow you're teaching.

---

## Common pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Alembic can't find models | Models not imported in `__init__.py` | Ensure `app/models/__init__.py` imports all model classes |
| Tests hit file-based DB | `conftest.py` not overriding DB URL | Force `sqlite://` (in-memory) in test fixtures |
| Auth tests fail with 422 | Login endpoint expects form data, tests send JSON (or vice versa) | Check whether you're using `OAuth2PasswordRequestForm` or a Pydantic model |
| Claude adds email validation back | It "fixes" the intentional gap | Re-prompt to remove it, or manually delete the validator |
| N+1 gets fixed automatically | Claude adds eager loading by default | Replace `joinedload`/`selectinload` with lazy loading on the deals list query |
| Frontend templates 500 | Jinja2 not configured in FastAPI | Check `app/main.py` has `Jinja2Templates(directory="app/templates")` |
| Seed script fails | Foreign key order wrong | Seed in order: users → companies → deal_stages → contacts → deals → tags → deal_tags → activities |

---

*Last updated: 2026-03-11*
