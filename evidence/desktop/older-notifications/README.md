# Older office-run notification repair

Base: `1a5d1be12314b0e314740cec7a9083e1ae470387`.

The recent snapshot list is limited to twenty jobs. Notification projection used
only that list, so an older assigned run silently lost its completion/attention
notification and station badge. An older active run's warning also disappeared.

The renderer now accepts optional `office_jobs`, bounded at 124 records: up to
24 distinct assigned jobs plus 100 active jobs. Runtime integration is owned by
the coordinator. Both lists are validated before projection; equivalent
notification records deduplicate by job ID, while conflicting state or ownership
fails closed. Supplemental snapshots must resolve every persisted office owner
to the exact project, run, task and worker. Explicitly released null workers keep
the retained attempt identity. Older runtimes without the field retain their
existing recent-list behavior.

`requireOfficeSessions` independently validates the 124-record supplemental bound,
while retaining the twenty-record recent-job bound. The optional
`office_jobs_truncated` coverage marker must be boolean and requires the
supplemental list. The coordinator's runtime contract retains every assigned job
across project selection and marks overflow above 100 active jobs. The desktop
transport owner is responsible for displaying partial active coverage honestly.

Validation uses deterministic snapshot fixtures. It makes no live provider calls
and does not establish native Electron or live orchestration readiness.

- `node --test desktop/tests/notifications.test.mjs`: baseline 8 passed;
  regression red 8 passed / 5 failed; repaired 13 passed / 0 failed.
- `node --test desktop/tests/runtime-identity.test.mjs`: regression red 3 passed /
  2 failed; repaired 5 passed / 0 failed.
- `node --test desktop/tests/*.test.mjs`: initial repair 55 passed / 0 failed;
  final repair 57 passed / 0 failed.
- `desktop/node_modules/.bin/tsc --noEmit -p desktop/tsconfig.json`: passed.
- `git diff --check`: passed.

The first isolated-worktree typecheck could not find dependency typings
(`typecheck.log`). A symlink to the existing installed desktop dependencies fixed
module resolution; the successful check is `typecheck-green.log`. No dependency
versions or assets changed. Baseline and red failures are retained separately.
The temporary dependency symlink was removed before handoff.
