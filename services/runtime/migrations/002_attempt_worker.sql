ALTER TABLE attempts ADD COLUMN worker_id TEXT REFERENCES workers(id);
