-- Deadline Management App
-- Run this once to set up the database:
--   psql -U postgres -d deadline_app -f db/schema.sql

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- GROUP 1: Auth

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       VARCHAR(255) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role            VARCHAR(255) NOT NULL DEFAULT 'admin'
                    CHECK (role IN ('super_admin', 'admin')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- GROUP 2: Core data

CREATE TABLE staff (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name   VARCHAR(255) NOT NULL,
    short_name  VARCHAR(100) NOT NULL UNIQUE,
    department  VARCHAR(255),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE documents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    row_number          INTEGER,
    received_date       DATE,
    document_type       VARCHAR(255),
    content_summary     TEXT,
    reference_number    VARCHAR(255),
    requirement         TEXT,
    deadline            DATE,
    is_recurring        BOOLEAN NOT NULL DEFAULT FALSE,
    recurrence_label    VARCHAR(100),
    status              VARCHAR(50) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'in_progress', 'overdue', 'done', 'cancelled')),
    result              TEXT,
    notes               TEXT,
    imported_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    imported_by         UUID REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE directives (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    row_number          INTEGER,
    meeting_date        DATE,
    directive_content   TEXT,
    deadline            DATE,
    is_recurring        BOOLEAN NOT NULL DEFAULT FALSE,
    recurrence_label    VARCHAR(100),
    status              VARCHAR(50) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'in_progress', 'overdue', 'done', 'cancelled')),
    result              TEXT,
    notes               TEXT,
    imported_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    imported_by         UUID REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE document_assignees (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    staff_id        UUID NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    UNIQUE (document_id, staff_id)   
);

CREATE TABLE directive_assignees (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    directive_id UUID NOT NULL REFERENCES directives(id) ON DELETE CASCADE,
    staff_id     UUID NOT NULL REFERENCES staff(id)      ON DELETE CASCADE,
    UNIQUE (directive_id, staff_id)
);

-- GROUP 3: System records

CREATE TABLE import_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_tab      VARCHAR(255) NOT NULL,
    filename        VARCHAR(255) NOT NULL,
    rows_imported   INTEGER NOT NULL DEFAULT 0,
    rows_skipped    INTEGER NOT NULL DEFAULT 0,
    rows_flagged    INTEGER NOT NULL DEFAULT 0,
    imported_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    imported_by     UUID REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name      VARCHAR(255) NOT NULL,
    record_id       UUID NOT NULL,
    action          VARCHAR(50)  NOT NULL CHECK (action IN ('create','update','delete')),
    old_values      JSONB,
    new_values      JSONB,
    changed_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    changed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- INDEXES

CREATE INDEX idx_documents_status    ON documents(status);
CREATE INDEX idx_documents_deadline  ON documents(deadline);
CREATE INDEX idx_directives_status   ON directives(status);
CREATE INDEX idx_directives_deadline ON directives(deadline);
CREATE INDEX idx_doc_assignees_staff ON document_assignees(staff_id);
CREATE INDEX idx_dir_assignees_staff ON directive_assignees(staff_id);
CREATE INDEX idx_audit_table_record  ON audit_log(table_name, record_id);

-- SEED: default super admin

-- Replace hashed_password with a real bcrypt hash before using
-- Generate with: python -c "import bcrypt; print(bcrypt.hashpw(b'yourpassword', bcrypt.gensalt()).decode())"
-- password: admin123 in this case

INSERT INTO users (full_name, email, hashed_password, role)
VALUES (
    'Super Admin',
    'admin@deadline-app.local',
    '$2b$12$PByzIDDj.eM2HySpETFWluMN4fIzzxfGArotelBzE/JfYZIiyEsnG',
    'super_admin'
);