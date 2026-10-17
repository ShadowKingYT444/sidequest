CREATE TABLE office_sessions (
    station_id TEXT PRIMARY KEY CHECK (
        station_id GLOB 'parent_0[0-2][0-9]'
        AND station_id BETWEEN 'parent_001' AND 'parent_024'
    ),
    job_id TEXT NOT NULL REFERENCES jobs(id),
    run_id TEXT NOT NULL UNIQUE REFERENCES attempts(id),
    worker_id TEXT NOT NULL UNIQUE REFERENCES workers(id),
    project_id TEXT NOT NULL REFERENCES projects(id),
    assigned_at TEXT NOT NULL
);

CREATE TRIGGER office_session_requires_recorded_identity
BEFORE INSERT ON office_sessions
WHEN NOT EXISTS (
    SELECT 1 FROM attempts a
    JOIN tasks t ON t.id = a.task_id
    JOIN jobs j ON j.id = t.job_id
    WHERE a.id = NEW.run_id AND a.worker_id = NEW.worker_id
      AND t.job_id = NEW.job_id AND j.project_id = NEW.project_id
)
BEGIN
    SELECT RAISE(ABORT, 'office session must match recorded run, worker, job and project');
END;

CREATE TRIGGER office_session_identity_is_immutable
BEFORE UPDATE ON office_sessions
BEGIN
    SELECT RAISE(ABORT, 'office session identity is immutable; clear explicitly before assigning');
END;
