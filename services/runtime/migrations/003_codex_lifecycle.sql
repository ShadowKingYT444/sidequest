ALTER TABLE attempts ADD COLUMN resume_count INTEGER NOT NULL DEFAULT 0 CHECK (resume_count >= 0);
ALTER TABLE tasks ADD COLUMN resume_requested INTEGER NOT NULL DEFAULT 0 CHECK (resume_requested IN (0, 1));

CREATE INDEX idx_attempts_provider_thread ON attempts(provider_thread_id) WHERE provider_thread_id IS NOT NULL;
