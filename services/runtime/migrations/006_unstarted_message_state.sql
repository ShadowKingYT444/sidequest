ALTER TABLE session_messages ADD COLUMN previous_job_state TEXT NOT NULL DEFAULT 'verifying'
    CHECK (previous_job_state IN ('verifying', 'accepted'));
