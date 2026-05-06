# Architecture

## Overview

A single-server web application for deadline management. One admin uses the app to import Vietnamese Excel data, monitor task deadlines, and track staff assignments. Built to run on a local network PC today, deployable to cloud with zero code changes in the future.

---

## System diagram

```
┌─────────────────────────────────────────────────┐
│                  Admin's PC                      │
│                                                  │
│  ┌──────────────┐      ┌──────────────────────┐  │
│  │    React     │◄────►│  FastAPI (Python)    │  │
│  │  (frontend)  │ HTTP │  + APScheduler       │  │
│  └──────────────┘      └──────────┬───────────┘  │
│                                   │               │
│                         ┌─────────▼──────────┐   │
│                         │    PostgreSQL       │   │
│                         └────────────────────┘   │
│                                                  │
│  Runs on port 5173 — no internet required        │
└─────────────────────────────────────────────────┘
         ▲
         │ local network (192.168.x.x)
         │ future: cloud URL
```

---

## Layers

### Frontend — React + Vite
- Single page application running in the browser
- Communicates with the backend via REST API calls
- Displays dashboard, staff drill-down, import UI
- JWT token stored in sessionStorage for authenticated requests (survives tab refresh, cleared on browser close)

### Backend — FastAPI (Python)
- Handles all business logic and database operations
- Validates all incoming requests via Pydantic schemas
- Issues and verifies JWT tokens for authentication
- Runs APScheduler in-process for hourly deadline checks
- Auto-generates API docs at `/api/docs` (Swagger UI)

### Scheduler — APScheduler
- Runs inside the FastAPI process — no separate service needed
- Executes `check_deadlines()` every hour automatically
- Marks overdue tasks and writes an audit_log entry for each change
- Recurring tasks (`is_recurring = true`) excluded from overdue logic

### Database — PostgreSQL
- Single PostgreSQL instance on the same machine
- 8 tables: users, staff, documents, directives, document_assignees, directive_assignees, import_logs, audit_log
- All IDs are UUIDs — safe for future merging or scaling
- JSONB columns in audit_log for flexible change history

### Excel parser — Python service class
- Reads `.xlsx` file using `openpyxl`
- Detects tab names dynamically using `rapidfuzz` fuzzy matching
- Extracts deadlines from Vietnamese free text using regex + `dateutil`
- Splits multi-person staff fields (e.g. `"KS. Tiến\nKS. Bảo"`)
- Flags rows where no deadline could be extracted

---

## Request flow

```
Admin browser
    │
    │ HTTPS + JWT token
    ▼
FastAPI router
    │
    ├── Auth middleware (verify JWT)
    │
    ├── Route handler (business logic)
    │       │
    │       ├── SQLAlchemy ORM
    │       │       │
    │       │       └── PostgreSQL
    │       │
    │       └── ExcelParser (on import requests)
    │
    └── JSON response → React frontend
```

---

## Folder structure

```
deadline-app/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # SQLAlchemy engine + session
│   ├── models/
│   │   ├── user.py
│   │   ├── staff.py
│   │   ├── document.py
│   │   ├── directive.py
│   │   ├── import_log.py
│   │   └── audit_log.py
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── import_.py
│   │   └── dashboard.py
│   ├── routers/                 # FastAPI route handlers
│   │   ├── auth.py
│   │   ├── import_.py
│   │   ├── dashboard.py
│   │   └── deps.py
│   ├── services/                # Business logic
│   │   ├── excel_parser.py
│   │   └── scheduler.py
│   ├── tests/
│   │   └── test_excel_parser.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── StaffDetail.jsx
│   │   │   ├── Import.jsx
│   │   │   └── Login.jsx
│   │   ├── components/
│   │   │   ├── TaskCard.jsx
│   │   │   └── StaffCard.jsx
│   │   ├── api/
│   │   │   ├── auth.js
│   │   │   ├── dashboard.js
│   │   │   ├── staff.js
│   │   │   └── client.js
│   │   ├── context/
│   │   │   ├── AuthContext.jsx
│   │   │   └── useAuth.js
│   │   └── App.jsx
│   └── package.json
├── docs/
│   ├── architecture.md          ← this file
│   ├── ERD.md
│   ├── user_stories.md
│   ├── sequence_diagrams.md
│   ├── class_diagram.md
│   ├── state_diagram.md
│   └── decisions.md
├── db/
│   └── schema.sql               # raw SQL to create all tables
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI pipeline
└── README.md
```

---

## Scalability path

| Phase | Setup | What changes |
|-------|-------|-------------|
| Now | Local PC, 1 admin | Nothing — this is the starting point |
| More admins | Same local PC | Add user accounts via admin UI — no code change |
| Remote access | VPS ($10/month) | Point same codebase at cloud server — no code change |
| High traffic | Scale PostgreSQL | Upgrade DB server or add read replicas |

The architecture is designed so each scaling step requires infrastructure changes only — never a code rewrite.

---

## Key constraints

- **No internet required** — runs entirely on local network
- **No mobile app** — browser only, responsive design for tablet access
- **Single admin initially** — auth layer supports multiple users when needed
- **Vietnamese text** — all parsing handles UTF-8 Vietnamese characters natively
- **Excel dependency** — source of truth remains the Excel file, app is the tracking layer