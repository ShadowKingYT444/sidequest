CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 200),
    canonical_root TEXT NOT NULL UNIQUE,
    base_ref TEXT NOT NULL,
    base_revision TEXT NOT NULL,
    policy_json TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'paused', 'blocked')),
    created_at TEXT NOT NULL
);

CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    title TEXT NOT NULL CHECK (length(title) BETWEEN 1 AND 200),
    source_json TEXT NOT NULL,
    outcome TEXT,
    state TEXT NOT NULL CHECK (state IN ('queued', 'running', 'verifying', 'needs_approval', 'accepted', 'blocked', 'failed', 'paused', 'cancelled')),
    checks_json TEXT NOT NULL,
    allowed_actions_json TEXT NOT NULL,
    budget_micro INTEGER NOT NULL CHECK (budget_micro >= 0),
    spent_micro INTEGER CHECK (spent_micro IS NULL OR spent_micro >= 0),
    workflow_version INTEGER NOT NULL CHECK (workflow_version >= 1),
    candidate_id TEXT,
    blocked_reason TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

CREATE TABLE workers (
    id TEXT PRIMARY KEY,
    role TEXT NOT NULL CHECK (role IN ('builder', 'researcher', 'verifier')),
    state TEXT NOT NULL CHECK (state IN ('idle', 'working', 'blocked', 'paused')),
    current_task_id TEXT,
    configuration_json TEXT NOT NULL,
    FOREIGN KEY (current_task_id) REFERENCES tasks(id)
);

CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(id),
    kind TEXT NOT NULL CHECK (kind IN ('build', 'research', 'integration', 'verify')),
    objective TEXT NOT NULL CHECK (length(objective) BETWEEN 1 AND 4000),
    depends_on_json TEXT NOT NULL,
    write_paths_json TEXT NOT NULL,
    check_ids_json TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('queued', 'running', 'verifying', 'needs_approval', 'completed', 'blocked', 'failed', 'paused', 'cancelled')),
    worker_id TEXT REFERENCES workers(id),
    current_attempt_id TEXT,
    sort_order INTEGER NOT NULL CHECK (sort_order >= 0),
    FOREIGN KEY (current_attempt_id) REFERENCES attempts(id)
);

CREATE TABLE attempts (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    number INTEGER NOT NULL CHECK (number > 0),
    state TEXT NOT NULL CHECK (state IN ('running', 'completed', 'failed', 'cancelled', 'ambiguous')),
    base_revision TEXT NOT NULL,
    provider_thread_id TEXT,
    provider_turn_id TEXT,
    model TEXT,
    effort TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    input_tokens INTEGER CHECK (input_tokens IS NULL OR input_tokens >= 0),
    cached_input_tokens INTEGER CHECK (cached_input_tokens IS NULL OR cached_input_tokens >= 0),
    output_tokens INTEGER CHECK (output_tokens IS NULL OR output_tokens >= 0),
    total_tokens INTEGER CHECK (total_tokens IS NULL OR total_tokens >= 0),
    cost_micro INTEGER CHECK (cost_micro IS NULL OR cost_micro >= 0),
    usage_uncertain INTEGER NOT NULL CHECK (usage_uncertain IN (0, 1)),
    UNIQUE (task_id, number)
);

CREATE TABLE artifacts (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(id),
    run_id TEXT REFERENCES attempts(id),
    candidate_id TEXT REFERENCES candidates(id),
    kind TEXT NOT NULL,
    media_type TEXT NOT NULL,
    display_name TEXT NOT NULL,
    sha256 TEXT NOT NULL CHECK (length(sha256) = 64),
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    storage_key TEXT NOT NULL,
    immutable INTEGER NOT NULL CHECK (immutable IN (0, 1)),
    created_at TEXT NOT NULL
);

CREATE TABLE candidates (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(id),
    run_id TEXT NOT NULL REFERENCES attempts(id),
    base_revision TEXT NOT NULL,
    candidate_revision TEXT NOT NULL,
    tree_sha256 TEXT NOT NULL CHECK (length(tree_sha256) = 64),
    patch_sha256 TEXT NOT NULL CHECK (length(patch_sha256) = 64),
    manifest_artifact_id TEXT NOT NULL REFERENCES artifacts(id),
    created_at TEXT NOT NULL
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL REFERENCES jobs(id),
    run_id TEXT REFERENCES attempts(id),
    run_seq INTEGER,
    at TEXT NOT NULL,
    type TEXT NOT NULL,
    message TEXT NOT NULL CHECK (length(message) <= 4096),
    artifact_id TEXT REFERENCES artifacts(id),
    UNIQUE (run_id, run_seq)
);

CREATE TABLE approvals (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(id),
    candidate_id TEXT NOT NULL REFERENCES candidates(id),
    source_revision TEXT NOT NULL,
    tree_sha256 TEXT NOT NULL CHECK (length(tree_sha256) = 64),
    patch_sha256 TEXT NOT NULL CHECK (length(patch_sha256) = 64),
    action TEXT NOT NULL,
    destination TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('pending', 'approved', 'denied', 'stale')),
    decision_at TEXT
);

CREATE TABLE deliveries (
    id TEXT PRIMARY KEY,
    approval_id TEXT NOT NULL REFERENCES approvals(id),
    request_sha256 TEXT NOT NULL CHECK (length(request_sha256) = 64),
    state TEXT NOT NULL CHECK (state IN ('pending', 'applied', 'not_applied', 'ambiguous')),
    external_receipt TEXT,
    started_at TEXT NOT NULL,
    reconciled_at TEXT
);

CREATE TABLE workshops (
    id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    name TEXT NOT NULL,
    package_artifact_id TEXT NOT NULL REFERENCES artifacts(id),
    package_sha256 TEXT NOT NULL CHECK (length(package_sha256) = 64),
    state TEXT NOT NULL CHECK (state IN ('draft', 'testing', 'ready', 'active', 'paused', 'blocked')),
    validation_json TEXT NOT NULL,
    activation_json TEXT,
    PRIMARY KEY (id, version)
);

CREATE TABLE watcher_cursors (
    watcher_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    config_json TEXT NOT NULL,
    cursor_json TEXT NOT NULL,
    state TEXT NOT NULL,
    last_event_at TEXT
);

CREATE TABLE watcher_events (
    watcher_id TEXT NOT NULL REFERENCES watcher_cursors(watcher_id),
    event_id TEXT NOT NULL,
    job_id TEXT REFERENCES jobs(id),
    payload_sha256 TEXT NOT NULL CHECK (length(payload_sha256) = 64),
    observed_at TEXT NOT NULL,
    PRIMARY KEY (watcher_id, event_id)
);

CREATE TABLE budget_reservations (
    id TEXT PRIMARY KEY,
    attempt_id TEXT NOT NULL UNIQUE REFERENCES attempts(id),
    reserved_micro INTEGER NOT NULL CHECK (reserved_micro >= 0),
    settled_micro INTEGER CHECK (settled_micro IS NULL OR settled_micro >= 0),
    state TEXT NOT NULL CHECK (state IN ('active', 'settled', 'uncertain', 'released')),
    created_at TEXT NOT NULL
);

CREATE TABLE command_results (
    command_id TEXT PRIMARY KEY,
    request_sha256 TEXT NOT NULL CHECK (length(request_sha256) = 64),
    type TEXT NOT NULL,
    accepted_revision INTEGER NOT NULL CHECK (accepted_revision >= 0),
    response_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE INDEX idx_jobs_project_state_created ON jobs(project_id, state, created_at);
CREATE INDEX idx_tasks_job_state_sort ON tasks(job_id, state, sort_order);
CREATE INDEX idx_attempts_task_state ON attempts(task_id, state);
CREATE INDEX idx_events_run_sequence ON events(run_id, run_seq);
CREATE INDEX idx_artifacts_job_candidate ON artifacts(job_id, candidate_id);
CREATE INDEX idx_approvals_job_state ON approvals(job_id, state);
CREATE INDEX idx_workshops_state ON workshops(state);

CREATE TRIGGER candidates_identity_is_immutable
BEFORE UPDATE ON candidates
BEGIN
    SELECT RAISE(ABORT, 'candidate identity is immutable');
END;

CREATE TRIGGER candidates_cannot_be_deleted
BEFORE DELETE ON candidates
BEGIN
    SELECT RAISE(ABORT, 'candidate identity is immutable');
END;

CREATE TRIGGER approvals_identity_is_immutable
BEFORE UPDATE OF id, job_id, candidate_id, source_revision, tree_sha256, patch_sha256, action, destination ON approvals
BEGIN
    SELECT RAISE(ABORT, 'approval identity is immutable');
END;

CREATE TRIGGER artifact_candidate_link_is_immutable
BEFORE UPDATE OF candidate_id ON artifacts
WHEN OLD.candidate_id IS NOT NULL AND NEW.candidate_id != OLD.candidate_id
BEGIN
    SELECT RAISE(ABORT, 'artifact candidate link is immutable');
END;
