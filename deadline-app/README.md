# Deadline Management App

A full-stack web application for tracking government document deadlines and staff assignments, built to replace a manual Excel-based workflow. Designed for a Vietnamese public administration office managing 50–100 deadline-sensitive tasks per month.

## What it does

The office tracks two types of tasks from Excel files updated monthly:
- **Documents** — incoming official documents with processing deadlines
- **Directives** — action items from leadership meetings with assigned staff

The app ingests those Excel files, surfaces upcoming deadlines on a live dashboard, and automatically marks overdue tasks every hour — replacing a process that previously required manual review of the spreadsheet.

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | React + Vite | Component model fits a card-based dashboard; Vite for fast hot reload |
| Backend | FastAPI (Python) | `openpyxl`, `rapidfuzz`, `dateutil` are best-in-class for this parsing problem |
| Database | PostgreSQL 16 | UUID support, JSONB audit log, handles concurrent writes |
| Auth | JWT (python-jose + bcrypt) | Stateless, works naturally with React SPA |
| Scheduler | APScheduler | In-process hourly job — no separate worker or message broker |
| Container | Docker + Docker Compose | One command to run the full stack |
| CI | GitHub Actions | Tests must pass before Docker images are built |

## Features

- **Fuzzy tab detection** — sheet names change every month (`"Tháng 4"` → `"Tháng 5"`). The parser uses `rapidfuzz` partial ratio matching to find the correct tab regardless of the month suffix, so no configuration is needed after each monthly update.
- **Free-text deadline extraction** — deadlines are embedded in Vietnamese prose (`"KS. Phú hoàn thành trước 15/5/2026"`). A regex + `dateutil` pipeline extracts the last date found, handling `d/m/yyyy` and `dd/mm/yyyy` formats with `dayfirst=True`.
- **Recurring task detection** — cells containing keywords like `"thường xuyên"`, `"hàng tuần"` are flagged as recurring and excluded from overdue logic permanently.
- **3-step import flow** — detect tabs → preview (with flagged rows) → confirm. No data is written until the admin explicitly confirms.
- **Urgency dashboard** — tasks grouped into 5 buckets: overdue, red urgent (≤1 day), red (≤3 days), yellow (≤7 days), green (>7 days). Computed at request time, not stored.
- **Staff drill-down** — click any staff card to see all their assigned tasks sorted by days remaining.
- **Automated overdue marking** — APScheduler runs `check_deadlines()` every hour, transitions `pending`/`in_progress` tasks past their deadline to `overdue`, and writes an audit log entry for each change.
- **Full audit trail** — every automated status change is recorded in `audit_log` with old/new values as JSONB.

## Excel file requirements

The app expects a `.xlsx` file with two sheets. Sheet names are detected by fuzzy matching — they do not need to match exactly.

### Tab 1 — Document tracking (`"Theo dõi CV Tháng X"`)

Data starts at **row 6**. Rows above row 6 are treated as headers and skipped.

| Column | Field | Notes |
|---|---|---|
| A | Row number | Integer |
| B | Received date | Date value or `dd/mm/yyyy` string |
| C | Document type | Free text |
| D | Content summary | Free text |
| E | Reference number | Free text |
| F | Requirement | **Deadline extracted from here** — can be free text like `"hoàn thành trước 15/5/2026"` |
| G | Assigned staff | Names separated by newline, comma, or semicolon — e.g. `"KS. Tiến\nKS. Bảo"` |
| H | Result | Free text |
| I | Notes | Free text |

### Tab 2 — Directives (`"Chỉ đạo LĐP giao ban"`)

Data starts at **row 9**.

| Column | Field | Notes |
|---|---|---|
| A | Row number | Integer |
| B | Meeting date | Date value or `dd/mm/yyyy` string |
| C | Directive content | Free text |
| D | Assigned staff | Names separated by newline, comma, or semicolon |
| E | Deadline | **Deadline extracted from here** — free text or date value |
| F | Result | Free text |
| G | Notes | Free text |

**Recurring tasks:** If column F (Tab 1) or column E (Tab 2) contains `"mỗi ngày"`, `"hàng ngày"`, `"hàng tuần"`, `"hàng tháng"`, or `"thường xuyên"`, the task is marked as recurring and excluded from overdue checks.

**Flagged rows:** Rows where no deadline can be extracted and the task is not recurring are imported but flagged for admin review in the preview step.

## Running locally

### With Docker (recommended)

```bash
# 1. Clone the repo
git clone <repo-url>
cd deadline-app

# 2. Create environment file
cp .env.example .env
# Edit .env and set POSTGRES_PASSWORD and SECRET_KEY

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
DATABASE_URL=postgresql://... SECRET_KEY=... uvicorn main:app --reload

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

Tests cover all `ExcelParser` parsing methods with 27 test cases across 4 test classes. No database required — the test fixture builds an in-memory workbook using `openpyxl`.

## Project structure

```
deadline-app/
├── backend/
│   ├── main.py                  # FastAPI app, scheduler lifecycle
│   ├── database.py              # SQLAlchemy engine + session
│   ├── models/                  # ORM models (User, Staff, Document, Directive, ...)
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── routers/                 # Route handlers (auth, import, dashboard)
│   ├── services/
│   │   ├── excel_parser.py      # Core parsing engine
│   │   └── scheduler.py         # Hourly deadline checker
│   └── tests/
│       └── test_excel_parser.py
├── frontend/
│   └── src/
│       ├── pages/               # Dashboard, Import, Login, StaffDetail
│       ├── components/          # TaskCard, StaffCard
│       ├── api/                 # Axios client + API call functions
│       └── context/             # JWT auth context
├── db/
│   └── schema.sql               # All 8 tables + indexes + seed user
├── docs/                        # Architecture, ERD, class diagram, ADRs, ...
└── .github/workflows/ci.yml     # GitHub Actions: test → build
```

## CI/CD

GitHub Actions runs on every push and PR to `dev` and `main`:

1. **test-backend** — installs dependencies, runs `pytest tests/ -v`
2. **build-docker** — builds backend and frontend Docker images (only runs if tests pass)

## Database schema

8 tables: `users`, `staff`, `documents`, `directives`, `document_assignees`, `directive_assignees`, `import_logs`, `audit_log`.

Key design decisions:
- All primary keys are UUIDs — safe for future data merging
- `document_assignees` and `directive_assignees` are explicit junction tables with a unique constraint on `(document_id, staff_id)` — prevents duplicate assignments
- `audit_log.old_values` and `new_values` are JSONB — stores arbitrary change history without schema changes
- `is_recurring = true` rows are permanently excluded from the overdue scheduler query
- `users` and `staff` are separate tables — a user is a system login; a staff member is a task assignee extracted from Excel (they may overlap but don't have to)

