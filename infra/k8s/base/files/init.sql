-- CleanRoom Harness schema. Demo/synthetic data only.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id            UUID PRIMARY KEY,
    tenant_id     TEXT NOT NULL,
    source        TEXT NOT NULL,
    content       TEXT NOT NULL,
    content_hash  TEXT NOT NULL,
    -- Populated when an embeddings pipeline is added; dimension matches
    -- common local embedding models and can be altered per deployment.
    embedding     VECTOR(768),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, content_hash)
);

CREATE INDEX IF NOT EXISTS idx_documents_tenant ON documents (tenant_id);

CREATE TABLE IF NOT EXISTS audit_events (
    id               UUID PRIMARY KEY,
    actor            TEXT NOT NULL,
    action           TEXT NOT NULL,
    resource_type    TEXT NOT NULL,
    resource_id      TEXT,
    tenant_id        TEXT,
    policy_decision  TEXT NOT NULL,
    reason           TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_events_tenant ON audit_events (tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_events_created ON audit_events (created_at);
