# User stories

## Actors

| Actor | Description |
|-------|-------------|
| **Admin** | The sole user of the application. Imports Excel data, monitors all deadlines, manages staff assignments, and tracks task completion across the department. |
| **System** | The automated background scheduler. Runs hourly to check deadlines, update task statuses to `overdue`, and trigger dashboard alerts. |

---

## Epic 1 — Authentication

### US-01 · Login
> As an admin, I want to log in with my email and password so that the app is protected from unauthorised access.

**Acceptance criteria:**
- Admin can log in with valid email and password
- Invalid credentials show a clear error message
- A JWT token is issued on successful login
- Token expires after 8 hours of inactivity
- App redirects to the dashboard after login

---

## Epic 2 — Excel import

### US-02 · Upload Excel file
> As an admin, I want to upload the Excel file so that the latest tasks and directives are loaded into the system.

**Acceptance criteria:**
- Admin can upload a `.xlsx` file via a file picker
- The system reads all tab names from the uploaded file and displays them
- App auto-detects and pre-selects the most likely tab for each role using fuzzy matching
- Admin can override the selection via dropdown before confirming
- No tab names are hardcoded — app works regardless of tab name changes
- Vietnamese text (UTF-8) is parsed correctly
- A preview of parsed rows is shown before confirming the import
- Admin can cancel the import after seeing the preview

### US-03 · Handle import errors gracefully
> As an admin, I want to see which rows failed to import so that I can fix data issues without losing good rows.

**Acceptance criteria:**
- Rows with missing required fields are flagged with a reason
- Rows where no deadline could be extracted are flagged as "deadline not found"
- Valid rows are still imported even if some rows fail
- A summary shows: rows imported, rows skipped, rows flagged
- Flagged rows can be corrected manually after import

### US-04 · Avoid duplicate imports
> As an admin, I want the system to detect duplicate rows so that re-uploading the same file doesn't create duplicate tasks.

**Acceptance criteria:**
- Rows already in the database (matched by reference number + date) are skipped
- Admin is shown how many rows were skipped as duplicates
- Existing records are not overwritten unless admin explicitly chooses to update

### US-05 · View import history
> As an admin, I want to see a log of past imports so that I can track when data was last updated.

**Acceptance criteria:**
- Import log shows: filename, date/time, rows imported, rows skipped
- Logs are sorted newest first
- Each log entry shows which tab was imported

---

## Epic 3 — Dashboard

### US-06 · View deadline dashboard
> As an admin, I want to see all pending tasks on a dashboard so that I can get an immediate overview of the workload.

**Acceptance criteria:**
- Dashboard loads within 2 seconds
- Tasks are grouped by urgency tier (red / yellow / green)
- Each task card shows: content summary, assigned staff, deadline, days remaining
- Completed tasks are not shown by default but can be toggled on
- Dashboard refreshes automatically every 5 minutes

### US-07 · See red alerts for critical deadlines
> As an admin, I want tasks due within 3 days to be highlighted in red so that I can prioritise them immediately.

**Acceptance criteria:**
- Tasks with deadline ≤ 3 days display with a red background/border
- Red tasks are always sorted to the top of the dashboard
- Overdue tasks (past deadline, not done) also appear in red with an "OVERDUE" badge
- Count of red tasks is shown prominently at the top of the page

### US-08 · See yellow warnings for upcoming deadlines
> As an admin, I want tasks due within 7 days to be highlighted in yellow so that I can plan ahead.

**Acceptance criteria:**
- Tasks with deadline between 4–7 days display with a yellow indicator
- Yellow tasks appear below red tasks in the dashboard order

### US-09 · See green status for tasks on track
> As an admin, I want tasks with more than 7 days remaining to appear in green so that I can confirm they are under control.

**Acceptance criteria:**
- Tasks with deadline > 7 days display with a green indicator
- Green tasks appear below yellow tasks

### US-10 · View live countdown timers
> As an admin, I want to see exactly how much time remains for each task so that I have precise deadline awareness.

**Acceptance criteria:**
- Each task shows a countdown in the format: `X days Y hours`
- Countdown updates in real time without page refresh
- Overdue tasks show how long ago they were due: `Overdue by X days`
- Recurring tasks (e.g. "Mỗi ngày") show "Recurring — daily" instead of a countdown

---

## Epic 4 — Staff management

### US-11 · View all staff
> As an admin, I want to see a list of all staff members so that I can manage who is assigned to what.

**Acceptance criteria:**
- Staff list shows full name and short name (as used in Excel)
- Each staff member shows a count of their pending tasks
- Staff with overdue tasks are highlighted

### US-12 · Drill down into a staff member's tasks
> As an admin, I want to click on a staff member and see all their assigned tasks so that I can assess their workload at a glance.

**Acceptance criteria:**
- Clicking a staff member opens a detail view
- Detail view shows all tasks assigned to that person grouped by status
- Each task shows deadline, urgency colour, and current status
- Admin can mark a task as done from this view

### US-13 · Manually assign staff to a task
> As an admin, I want to assign or reassign a staff member to a task so that I can correct import errors or update responsibilities.

**Acceptance criteria:**
- Admin can edit the assigned staff on any task
- Changes are saved immediately
- Change is recorded in the audit log

---

## Epic 5 — Task management

### US-14 · Mark a task as done
> As an admin, I want to mark a task as done so that it no longer appears as a pending deadline.

**Acceptance criteria:**
- Admin can mark any task as done from the dashboard or staff detail view
- Done tasks move out of the active dashboard view
- Completion timestamp is recorded
- Action is logged in the audit log

### US-15 · Mark a task as in progress
> As an admin, I want to mark a task as in progress so that I can communicate that work has started.

**Acceptance criteria:**
- Task status can be set to `in_progress`
- In-progress tasks still show their deadline and urgency colour
- Status badge changes to "In progress"

### US-16 · Edit task details manually
> As an admin, I want to edit a task's deadline or notes so that I can correct data that was not parsed correctly from the Excel file.

**Acceptance criteria:**
- Admin can edit: deadline, notes, assigned staff, status
- Original imported values are preserved in the audit log
- Edited fields are visually marked as "manually edited"

### US-17 · View recurring tasks
> As an admin, I want recurring tasks (e.g. daily tasks) to be clearly labelled so that I don't confuse them with one-time deadlines.

**Acceptance criteria:**
- Tasks with `is_recurring = true` show a "Recurring" badge
- Recurring label (e.g. "Mỗi ngày") is displayed
- These tasks are never marked as overdue automatically

---

## Epic 6 — Notifications and alerts

### US-18 · See urgent tasks highlighted on login
> As an admin, I want the dashboard to immediately show red alerts when I log in so that I never miss a critical deadline.

**Acceptance criteria:**
- Red tasks are the first thing visible on the dashboard
- A count badge shows total red + overdue tasks in the page title or header
- No additional steps needed — alerts are visible on the main screen

### US-19 · System auto-marks overdue tasks
> As an admin, I want the system to automatically flag tasks as overdue so that I don't have to check manually every day.

**Acceptance criteria:**
- Scheduler runs every hour
- Any task past its deadline with status `pending` or `in_progress` is set to `overdue`
- Overdue tasks appear with a red "OVERDUE" badge on the dashboard
- Scheduler activity is logged

---

## Epic 7 — Audit and history

### US-20 · View audit log
> As an admin, I want to see a history of all changes so that I can track what was modified and when.

**Acceptance criteria:**
- Audit log shows: table, record, action (create/update/delete), old value, new value, timestamp
- Log is sortable by date
- Admin can filter by record type (document or directive)

---

## Story point summary

| Epic | Stories | Priority |
|------|---------|----------|
| Authentication | US-01 | High |
| Excel import | US-02, US-03, US-04, US-05 | High |
| Dashboard | US-06, US-07, US-08, US-09, US-10 | High |
| Staff management | US-11, US-12, US-13 | High |
| Task management | US-14, US-15, US-16, US-17 | Medium |
| Notifications | US-18, US-19 | High |
| Audit and history | US-20 | Medium |
