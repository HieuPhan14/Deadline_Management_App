# Deadline Management App

A full-stack deadline tracking system built for a Vietnamese hospital admin department (P.HCQT).

## Tech Stack

**Backend:** FastAPI, PostgreSQL, SQLAlchemy, APScheduler
**Frontend:** React, Vite, Tailwind CSS
**Infrastructure:** Docker, Docker Compose

## Features

- Excel import with fuzzy Vietnamese tab detection
- Automatic overdue detection via background scheduler
- Urgency tiers: overdue, red, yellow, green
- Staff drill-down view
- JWT authentication
- Full audit logging

## Running with Docker

1. Clone the repo
2. Create `.env` in root:
\```
POSTGRES_PASSWORD=yourpassword
SECRET_KEY=yoursecretkey
\```
3. Run:
\```bash
docker compose up --build
\```
4. Open http://localhost:5173
5. Login: admin@deadline-app.local / admin123

## Running locally

**Backend:**
\```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
\```

**Frontend:**
\```bash
cd frontend
npm install
npm run dev
\```

## Architecture

3-tier layered monolith designed for local network deployment, scalable to cloud without code changes.

- `backend/` — FastAPI REST API
- `frontend/` — React SPA
- `db/` — PostgreSQL schema
- `docs/` — Architecture docs, ERD, sequence diagrams