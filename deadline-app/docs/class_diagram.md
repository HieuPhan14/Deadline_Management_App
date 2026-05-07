# Class diagram

Python SQLAlchemy models and service classes for the deadline management backend.

```mermaid
classDiagram
  class User {
    +UUID id
    +String full_name
    +String email
    +String hashed_password
    +String role
    +Boolean is_active
    +DateTime created_at
    +verify_password(plain) bool
    +is_admin() bool
    +is_super_admin() bool
  }

  class Staff {
    +UUID id
    +String full_name
    +String short_name
    +String department
    +Boolean is_active
    +DateTime created_at
    +get_pending_tasks() list
    +get_overdue_tasks() list
    +get_task_count() int
  }

  class Document {
    +UUID id
    +Int row_number
    +Date received_date
    +String document_type
    +String content_summary
    +String reference_number
    +String requirement
    +Date deadline
    +Boolean is_recurring
    +String recurrence_label
    +String status
    +String notes
    +DateTime imported_at
    +UUID imported_by
    +is_overdue() bool
    +days_remaining() int
    +urgency_tier() str
    +mark_done() None
    +mark_in_progress() None
  }

  class Directive {
    +UUID id
    +Int row_number
    +Date meeting_date
    +String directive_content
    +Date deadline
    +Boolean is_recurring
    +String recurrence_label
    +String status
    +String result
    +String notes
    +DateTime imported_at
    +UUID imported_by
    +is_overdue() bool
    +days_remaining() int
    +urgency_tier() str
    +mark_done() None
    +mark_in_progress() None
  }

  class DocumentAssignee {
    +UUID id
    +UUID document_id
    +UUID staff_id
  }

  class DirectiveAssignee {
    +UUID id
    +UUID directive_id
    +UUID staff_id
  }

  class ImportLog {
    +UUID id
    +String source_tab
    +String filename
    +Int rows_imported
    +Int rows_skipped
    +Int rows_flagged
    +DateTime imported_at
    +UUID imported_by
  }

  class AuditLog {
    +UUID id
    +String table_name
    +UUID record_id
    +String action
    +JSON old_values
    +JSON new_values
    +UUID changed_by
    +DateTime changed_at
  }

  class ExcelParser {
    +Workbook wb
    +detect_tabs() dict
    +parse(tab1_name, tab2_name) dict
    +parse_tab1(sheet) tuple
    +parse_tab2(sheet) tuple
    +extract_deadline(text) Date
    +extract_staff_names(text) list~str~
    +detect_recurring(text) tuple
    -_suggest_tab(keywords) str
    -_parse_date(value) Date
  }

  class DeadlineScheduler {
    +APScheduler scheduler
    +start_scheduler() None
    +stop_scheduler() None
    +check_deadlines() None
  }

  User "1" --> "many" Document : imports
  User "1" --> "many" Directive : imports
  User "1" --> "many" ImportLog : creates
  User "1" --> "many" AuditLog : performs

  Document "1" --> "many" DocumentAssignee : has
  Staff "1" --> "many" DocumentAssignee : assigned via

  Directive "1" --> "many" DirectiveAssignee : has
  Staff "1" --> "many" DirectiveAssignee : assigned via

  ExcelParser ..> Document : creates
  ExcelParser ..> Directive : creates
  ExcelParser ..> Staff : creates
  ExcelParser ..> ImportLog : creates

  DeadlineScheduler ..> Document : updates
  DeadlineScheduler ..> Directive : updates
  DeadlineScheduler ..> AuditLog : writes
```

---

## Notes

**Solid arrows (`-->`)** — persistent database relationships (foreign keys in the ERD).

**Dashed arrows (`..>`)** — service dependencies. `ExcelParser` and `DeadlineScheduler` are not database models — they are Python service classes that create or update the model instances.

**`Document` and `Directive` share the same methods** (`is_overdue`, `days_remaining`, `urgency_tier`, `mark_done`, `mark_in_progress`) — currently stubbed as `...` on each model; urgency computation lives in the dashboard router.

**`ExcelParser`** is the most critical service class. Its `extract_deadline()` method uses Python regex + `dateutil` to parse Vietnamese date strings embedded in free text (e.g. `"KS. Phú hoàn thành trước 15/5/2026"`).

**`DeadlineScheduler`** wraps APScheduler and runs `check_deadlines()` every hour independently of any user request.