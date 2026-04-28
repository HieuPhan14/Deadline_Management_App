# Sequence diagrams
 
Three core flows that define how the system behaves.
 
---
 
## Flow 1 — Admin login
 
```mermaid
sequenceDiagram
  actor Admin
  participant React as React frontend
  participant API as FastAPI
  participant DB as PostgreSQL
 
  Admin->>React: enters email + password
  React->>API: POST /auth/login
  API->>DB: SELECT user WHERE email=?
  DB-->>API: user record
  API->>API: verify password hash (bcrypt)
  alt invalid credentials
    API-->>React: 401 Unauthorised
    React-->>Admin: shows error message
  else valid credentials
    API->>API: generate JWT token (8hr expiry)
    API-->>React: 200 OK + JWT token
    React->>React: store token in memory
    React-->>Admin: redirect to dashboard
  end
```
 
**Key decisions:**
- Password hashed with bcrypt — never stored in plain text
- JWT stored in memory (not localStorage) — safer against XSS attacks
- Token expires after 8 hours — admin must re-login each working day
---
 
## Flow 2 — Excel import
 
```mermaid
sequenceDiagram
  actor Admin
  participant React as React frontend
  participant API as FastAPI
  participant Parser as Excel parser (Python)
  participant DB as PostgreSQL
 
  Admin->>React: selects .xlsx file
  React->>API: POST /import/detect-tabs (multipart)
  API->>Parser: load_workbook(file)
  Parser->>Parser: read all sheet names
  Parser->>Parser: fuzzy match best tab for each role
  API-->>React: sheet names + suggested selections
  React-->>Admin: shows tab dropdowns with pre-selected tabs
  Admin->>React: confirms or overrides tab selection
  React->>API: POST /import/preview + selected tab names
  API->>Parser: parse tab 1 with selected name
  API->>Parser: parse tab 2 with selected name
  Parser->>Parser: extract staff names
  Parser->>Parser: extract deadlines from free text
  Parser->>Parser: flag rows with no deadline found
  Parser-->>API: parsed rows + flagged rows
  API-->>React: preview payload (rows + warnings)
  React-->>Admin: shows preview table + warnings
 
  alt admin cancels
    Admin->>React: clicks cancel
    React-->>Admin: import discarded
  else admin confirms
    Admin->>React: clicks confirm import
    React->>API: POST /import/confirm
    API->>DB: upsert staff names
    loop for each valid row
      API->>DB: check duplicate (ref number + date)
      alt not duplicate
        API->>DB: INSERT document or directive
        API->>DB: INSERT assignees (junction table)
      else duplicate
        API->>DB: skip row
      end
    end
    API->>DB: INSERT import_log record
    API->>DB: INSERT audit_log entries
    API-->>React: 200 OK + import summary
    React-->>Admin: shows result (imported / skipped / flagged)
  end
```
 
**Key decisions:**
- Two-step flow (preview → confirm) prevents accidental data overwrites
- Duplicate detection uses reference number + date as a composite key
- Flagged rows (no deadline found) are still shown — admin fixes manually
- Both tabs are parsed in a single upload request
- Every import is recorded in `import_log` and `audit_log`
---
 
## Flow 3 — Automated deadline notification
 
```mermaid
sequenceDiagram
  participant Scheduler as APScheduler (hourly)
  participant API as FastAPI
  participant DB as PostgreSQL
  participant React as React dashboard
  actor Admin
 
  loop every hour
    Scheduler->>API: trigger check_deadlines()
    API->>DB: SELECT all pending + in_progress tasks
    DB-->>API: task list with deadlines
 
    loop for each task
      API->>API: calculate days_remaining = deadline - today
      alt days_remaining < 0
        API->>DB: UPDATE status = overdue
        API->>DB: INSERT audit_log (auto-overdue)
      else days_remaining <= 1
        API->>API: tag urgency = red (urgent)
      else days_remaining <= 3
        API->>API: tag urgency = red
      else days_remaining <= 7
        API->>API: tag urgency = yellow
      else
        API->>API: tag urgency = green
      end
    end
 
    API->>DB: INSERT scheduler_log (run timestamp)
    Scheduler-->>API: job complete
  end
 
  Admin->>React: opens dashboard
  React->>API: GET /dashboard
  API->>DB: SELECT tasks ordered by urgency
  DB-->>API: tasks with urgency tags
  API-->>React: dashboard payload
  React-->>Admin: renders red alerts at top
```
 
**Key decisions:**
- Scheduler runs independently every hour — no user action required
- Urgency tiers: red urgent (≤1 day), red (≤3 days), yellow (≤7 days), green (>7 days)
- Overdue status is set automatically and logged in audit_log
- Dashboard fetches pre-computed urgency — fast load, no recalculation on request
- Recurring tasks (`is_recurring = true`) are excluded from overdue logic