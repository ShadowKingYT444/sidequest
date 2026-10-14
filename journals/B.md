# Lane B journal

## B1 — isolated Git and immutable artifacts

Implemented `services/tools/` with strict JSON-line protocol, allowlisted path configuration, sanitized shell-free Git subprocesses, independent `--no-hardlinks` preparation, frozen candidate commits, full mode-aware manifests, binary patch/diff artifacts and read-only snapshots. Local delivery requires matching host `delivery_id`/`action_id`, separately staged host approval, exact candidate/source/tree/patch/action/destination identity, clean destination checks and durable idempotency state. The approval and delivery paths were exercised only against temporary fixture repositories.

Validation: `python3 -m py_compile services/tools/*.py services/tools/tests/*.py` passed; `python3 -m services.tools.main --help` passed; `python3 -m unittest discover -s services/tools/tests -p 'test_*.py' -v` passed 15 tests. Evidence: `evidence/B/B1.json`.

Limits: credential detection is heuristic and can miss encoded or unrecognized secrets; this adapter does not provide OS isolation against code running as the same user. It rejects ignored and untracked source files conservatively. No provider/model job, B2 operation, real repository delivery or external write was run. Next: coordinator freeze and independent B1 review before any B2 work.
