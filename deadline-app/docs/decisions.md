# Architecture decision records (ADR)

Why we chose each technology over the alternatives.

---

## ADR-01 — Python for the backend

**Decision:** Python (FastAPI) over Node.js (Express)

**Reasons:**
- `pandas` and `openpyxl` are the best Excel parsing libraries in any language — handling Vietnamese UTF-8 text, merged cells, and free-text date extraction is significantly easier in Python
- `rapidfuzz` for fuzzy tab name matching is a mature Python library with no equivalent in Node.js
- `APScheduler` for background jobs is simpler to integrate than Node.js alternatives (`node-cron` requires a separate process)
- `SQLAlchemy` ORM is more powerful and better documented than Node.js ORMs (Sequelize, Prisma)
- Python practice was an explicit project goal

**Tradeoff:** Node.js would have been slightly faster for API response times, but at <20 users this difference is irrelevant.

---

## ADR-02 — FastAPI over Flask or Django

**Decision:** FastAPI

**Reasons:**
- Auto-generates interactive API documentation at `/docs` (Swagger UI) — useful during development and for the client
- Native async support — handles concurrent requests without blocking
- Built-in request validation via Pydantic — catches bad data before it hits the database
- Modern, actively maintained, widely used in industry

**Alternatives rejected:**
- Flask — too minimal, requires too many separate libraries for auth, validation, async
- Django — too heavy for this scope, brings ORM, templating, admin panel we don't need

---

## ADR-03 — PostgreSQL over SQLite or MySQL

**Decision:** PostgreSQL

**Reasons:**
- Native `UUID` type — no workarounds needed
- Native `JSONB` type — used in `audit_log` for storing old/new values efficiently with indexing
- Handles concurrent writes safely — important when multiple admins are added in the future
- Scales from local PC to cloud server with zero code changes
- Better support for complex queries than MySQL

**Alternatives rejected:**
- SQLite — no concurrent write support, not suitable for multi-user future
- MySQL — no native UUID type, weaker JSON support, owned by Oracle

---

## ADR-04 — React over Vue or plain HTML

**Decision:** React (with Vite)

**Reasons:**
- Component model is ideal for the dashboard — each task card, staff card, and countdown timer is a reusable component
- Large ecosystem — date libraries, chart libraries, UI component libraries all available
- Industry standard — most recognisable on a resume
- Vite provides fast development server with hot reload

**Alternatives rejected:**
- Vue — good alternative but smaller ecosystem and less resume value
- Plain HTML/JS — unmanageable for a dynamic dashboard with live countdowns and real-time updates

---

## ADR-05 — JWT for authentication over sessions

**Decision:** JWT (JSON Web Tokens) stored in memory

**Reasons:**
- Stateless — server does not need to store session data in the database
- Works naturally with a React SPA + FastAPI backend architecture
- Token stored in memory (not localStorage) — protected against XSS attacks
- Easy to add role-based access control via token claims

**Tradeoff:** Tokens cannot be invalidated server-side before expiry. Mitigated by short expiry (8 hours) matching a working day.

---

## ADR-06 — APScheduler over Celery or cron

**Decision:** APScheduler (in-process background scheduler)

**Reasons:**
- Runs inside the FastAPI process — no separate worker process or message broker needed
- Simple setup — `scheduler.add_job(check_deadlines, 'interval', hours=1)`
- Sufficient for hourly deadline checks at this scale
- Easy to monitor — scheduler logs every run to the database

**Alternatives rejected:**
- Celery — requires Redis or RabbitMQ as a message broker, massive overkill for one hourly job
- System cron — runs outside the app, cannot access SQLAlchemy models or app configuration directly

---

## ADR-07 — Fuzzy tab matching with rapidfuzz

**Decision:** `rapidfuzz` library for Excel tab name detection

**Reasons:**
- Tab 1 name changes every month ("Tháng 4" → "Tháng 5") — hardcoding breaks monthly
- Fuzzy matching detects the correct tab even when the name changes
- `rapidfuzz` is faster and more accurate than the older `fuzzywuzzy` library
- Admin always sees a dropdown to confirm or override — fuzzy match is a suggestion, not automatic

---

## ADR-08 — Monorepo structure

**Decision:** Single repository with `/backend` and `/frontend` folders

**Reasons:**
- Simpler for a solo developer — one repo to clone, one README to follow
- Easier to keep docs, schema, and code in sync
- Single GitHub Actions CI pipeline covers both backend tests and Docker builds from one workflow file

**Future consideration:** If the frontend and backend teams grow separately, splitting into two repos is straightforward.