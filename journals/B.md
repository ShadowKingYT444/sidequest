# Lane B journal

## B1 — isolated Git and immutable artifacts

Implemented `services/tools/` with strict JSON-line protocol, allowlisted path configuration, sanitized shell-free Git subprocesses, independent `--no-hardlinks` preparation, frozen candidate commits, full mode-aware manifests, binary patch/diff artifacts and read-only snapshots. Local delivery requires matching host `delivery_id`/`action_id`, separately staged host approval, exact candidate/source/tree/patch/action/destination identity, clean destination checks and durable idempotency state. The approval and delivery paths were exercised only against temporary fixture repositories.

An independent B1 review found that a worker-editable `.git/config` hard link could make freeze truncate a file outside configured roots. Repair attempt 2 rejects hard-linked regular files throughout `.git`, walks metadata with no-follow directory descriptors, and replaces sanitized config via a new single-link inode and descriptor-relative atomic rename. It never opens the original config with `O_TRUNC`. Artifact, snapshot, state, progress, destination-file and destination-index writes were audited and changed to rooted directory descriptors, no-follow opens, and atomic replacement where applicable. Regression tests verify typed `POLICY_DENIED` and unchanged external sentinel bytes for hard-linked config, refs and progress logs.

Validation after repair: `python3 -m py_compile services/tools/*.py services/tools/tests/*.py` passed; `python3 -m services.tools.main --help` passed; `python3 -m unittest discover -s services/tools/tests -p 'test_*.py' -v` passed 19 tests. Evidence: `evidence/B/B1.json`.

Limits: credential detection is heuristic and can miss encoded or unrecognized secrets. The adapter is not an OS/container boundary against a malicious process running as the same user concurrently; worker access must be quiesced during freeze and delivery, and configured roots must be protected. It rejects ignored and untracked source files conservatively. No provider/model job, B2 operation, real repository delivery or external write was run. Next: coordinator freeze and fresh independent B1 review before any B2 work.
