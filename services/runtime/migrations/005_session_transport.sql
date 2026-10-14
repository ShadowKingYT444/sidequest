CREATE TABLE session_attachments (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES attempts(id),
    attachment_key TEXT NOT NULL,
    name TEXT NOT NULL,
    media_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL CHECK (size_bytes BETWEEN 0 AND 10485760),
    sha256 TEXT NOT NULL CHECK (length(sha256) = 64),
    storage_key TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    UNIQUE(run_id, attachment_key)
);
CREATE TABLE session_messages (
    id TEXT PRIMARY KEY REFERENCES command_results(command_id) DEFERRABLE INITIALLY DEFERRED,
    job_id TEXT NOT NULL REFERENCES jobs(id),
    task_id TEXT NOT NULL REFERENCES tasks(id),
    parent_run_id TEXT NOT NULL REFERENCES attempts(id),
    run_id TEXT REFERENCES attempts(id),
    prompt TEXT NOT NULL CHECK (length(prompt) BETWEEN 1 AND 2000),
    attachment_ids_json TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('queued','dispatching','completed','uncertain','rejected')),
    created_at TEXT NOT NULL
);
CREATE UNIQUE INDEX idx_one_pending_session_message ON session_messages(task_id)
    WHERE state IN ('queued','dispatching','uncertain');
