# Deadline Management App

A full-stack web application for tracking document deadlines and staff assignments, built to replace a manual Excel-based workflow. Supports any Excel structure via a visual column mapping UI — not tied to a specific spreadsheet format.

## What it does

The app ingests Excel files, surfaces upcoming deadlines on a live dashboard, and automatically marks overdue tasks every hour. Users can also create and edit tasks directly without importing from Excel.

Two task types:
- **Documents** — tasks where the deadline is embedded in the same cell as the content (free text like `"hoàn thành trước 15/5/2026"`)
- **Directives** — tasks where content and deadline are in separate columns

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | React + Vite | Component model fits a card-based dashboard; Vite for fast hot reload |
| Backend | FastAPI + async SQLAlchemy | Non-blocking I/O; `openpyxl`, `rapidfuzz`, `dateutil` for parsing |
| Database | PostgreSQL 16 + asyncpg | UUID support, JSONB audit log, async driver |
| Auth | PyJWT + pwdlib (bcrypt) | Stateless JWT; pwdlib is the modern passlib replacement |
| Config | pydantic-settings | Validates env vars at startup, fails fast on missing config |
| Scheduler | APScheduler (AsyncIOScheduler) | In-process hourly job running inside the async event loop |
| Container | Docker + Docker Compose | One command to run the full stack |
| CI | GitHub Actions | Tests must pass before Docker images are built |

## Features

- **Universal Excel import** — visual 4-step wizard: upload → map columns → preview → confirm. Works with any `.xlsx` structure regardless of column order or number of tabs. Users point and click to assign which column is content, deadline, and staff.
- **Flexible tab support** — import from 1 or 2 tabs in a single file. Each tab is configured independently with its own column mapping and type.
- **Fuzzy tab detection** — sheet names are auto-suggested using `rapidfuzz` partial ratio matching, so monthly name changes (`"Tháng 4"` → `"Tháng 5"`) require no manual adjustment.
- **Free-text deadline extraction** — deadlines embedded in prose (`"hoàn thành trước 15/5/2026"`) are extracted via regex + `dateutil`, supporting `dd/mm/yyyy`, `d/m/yyyy`, and ISO `yyyy-mm-dd` formats.
- **Bilingual recurring detection** — keywords in both Vietnamese (`"thường xuyên"`, `"hàng tuần"`) and English (`"weekly"`, `"recurring"`, `"ongoing"`) mark tasks as recurring, permanently excluding them from overdue logic.
- **Urgency dashboard** — tasks grouped into 5 buckets: overdue, red urgent (≤1 day), red (≤3 days), yellow (≤7 days), green (>7 days). Computed at request time, not stored.
- **Task CRUD** — create custom jobs directly from the dashboard without importing. Edit content, deadline, and staff assignments inline via a modal. Delete (cancel) tasks from the dashboard or staff detail view.
- **Custom staff creation** — when assigning staff to a task, type any name not in the existing list to create a new staff member on the fly.
- **Staff sidebar** — shows only staff with active tasks (pending/overdue count > 0). Click any staff card to see their tasks sorted by days remaining.
- **Duplicate prevention** — re-importing the same Excel skips rows whose content already exists in the database and is not cancelled.
- **Automated overdue marking** — APScheduler runs `check_deadlines()` every hour, transitions `pending`/`in_progress` tasks past their deadline to `overdue`, and writes an audit log entry per change.
- **Full audit trail** — every automated status change recorded in `audit_log` with old/new values as JSONB.

## Import flow

```
1. Upload .xlsx file
        ↓ auto-suggests sheet names via fuzzy match
2. Configure each tab:
   - Select sheet name
   - Set data start row
   - Choose type: "Content & Deadline in same column" or "Separate content & deadline columns"
   - Click "Load Columns" → see live preview table with sample values
   - Map: content column (required), deadline column, staff column
        ↓
3. Preview — summary of parsed rows + flagged rows (no deadline found)
        ↓ confirm
4. Done — import log saved, staff auto-created if new names found
```

## Running locally

### With Docker (recommended)

```bash
# 1. Clone the repo
git clone <repo-url>
cd deadline-app

# 2. Create environment file
cp .env.example .env
# Edit .env — set DATABASE_URL (must use postgresql+asyncpg:// scheme), SECRET_KEY, POSTGRES_PASSWORD

# 3. Start all services
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs (Swagger): http://localhost:8000/docs

Default login (seeded by `schema.sql`):
```
Email:    admin@deadline-app.local
Password: admin123
```

### Without Docker

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# Requires .env with DATABASE_URL=postgresql+asyncpg://...

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Running tests

```bash
cd backend
pytest tests/ -v
```

27 test cases across 4 classes covering `extract_deadline`, `detect_recurring`, `extract_staff_names`, and `_suggest_tab`. No database required — tests use an in-memory workbook built with `openpyxl`.

## Project structure

```
deadline-app/
├── backend/
│   ├── main.py                  # FastAPI app, lifespan, CORS, scheduler start/stop
│   ├── auth.py                  # JWT + bcrypt, get_current_user, CurrentUser alias
│   ├── config.py                # pydantic-settings, loads .env
│   ├── database.py              # Async SQLAlchemy engine, AsyncSessionLocal, Base
│   ├── models/                  # ORM models — User, Staff, Document, Directive, AuditLog, ImportLog
│   ├── schemas/                 # Pydantic schemas — dashboard, import, user
│   ├── routers/
│   │   ├── auth.py              # POST /auth/login
│   │   ├── dashboard.py         # GET /dashboard/, /staff, /staff/{id}
│   │   ├── tasks.py             # POST/PATCH/DELETE /tasks/documents|directives
│   │   ├── import_.py           # POST /import/detect-tabs, /tab-preview, /preview, /confirm
│   │   └── deps.py              # Re-exports from auth.py (backward compat)
│   ├── services/
│   │   ├── excel_parser.py      # Universal parser — column mapping, deadline extraction
│   │   └── scheduler.py         # Async hourly deadline checker
│   └── tests/
│       └── test_excel_parser.py
├── frontend/
│   └── src/
│       ├── pages/               # Dashboard, Import, Login, StaffDetail
│       ├── components/          # TaskCard, StaffCard, StaffPicker
│       ├── api/                 # Axios client + typed API functions
│       └── context/             # JWT auth context + useAuth hook
├── db/
│   └── schema.sql               # All 8 tables + indexes + seed user
└── .github/workflows/ci.yml     # GitHub Actions: test → build
```

## CI/CD

GitHub Actions runs on every push and PR to `dev` and `main`:

1. **test-backend** — installs dependencies, runs `pytest tests/ -v`
2. **build-docker** — builds backend and frontend Docker images (only if tests pass)

## Database schema

8 tables: `users`, `staff`, `documents`, `directives`, `document_assignees`, `directive_assignees`, `import_logs`, `audit_log`.

Key design decisions:
- All primary keys are UUIDs — safe for future data merging
- `document_assignees` and `directive_assignees` are junction tables with a unique constraint on `(document_id, staff_id)` — prevents duplicate assignments
- `audit_log.old_values` / `new_values` are JSONB — stores arbitrary change history without schema changes
- `is_recurring = true` rows are permanently excluded from the overdue scheduler query
- `users` and `staff` are separate — a user is a system login; a staff member is a task assignee (they may overlap but don't have to)
- Tasks with empty `content_summary` / `directive_content` are filtered out of all dashboard and staff views
