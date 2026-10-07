# B — execution, Git artifacts and local lookouts

Own services/tools/, journals/B.md and evidence/B/. Never repair this development repo as a runtime target. Use disposable fixture repositories. Follow EXECUTION.md's fixed component map and contracts; no new agent framework or platform-wide desktop controller.

## B1 — isolated Git and immutable artifacts

/goal Complete B1 only. Read AGENTS.md, EXECUTION.md sections 1–2, and contracts/PROTOCOL.md plus the artifact/progress sections of contracts/EXTENSIONS.md.

Implement protocol.py, git_ops.py and artifact_capture.py with repo.inspect, repo.prepare, artifacts.freeze and local-delivery support. Separate local clones per runtime task; candidate commit and frozen manifest/patch/diff with host-checked staging paths. Include untracked allowed files, removals, renames, modes and binary markers. Use Git's machine-readable formats; never ask a model to create a diff. Provide the complete shared envelope, progress log and error behavior.

- **B1-1**: Git tests prove independent clones, unchanged source, rejected dirty/unsafe source and no shared writable refs.
- **B1-2**: Fixture changes include add/edit/delete/rename/binary; captured manifest/diff bytes and hashes identify one immutable candidate and match the protocol.
- **B1-3**: Negative tests cover symlink/traversal/out-of-scope/oversize/secret-file input, stale delivery identity, repeated delivery ID and malformed stdout.

Run python3 -m unittest discover -s services/tools/tests -p 'test_*.py' -v. Keep the evidence concise and request independent review before B2.

## B2 — real Luna worker and approved delivery

/goal Complete B2 only. Read EXECUTION.md sections 1–3 and the model/approval/progress contracts. Do not reread all upstream agent frameworks.

Implement codex_bridge.py using the actual app-server, model catalog, explicit model/effort and bounded persistent goal. Stream safe activity to the assigned progress log and collect usage without exporting hidden reasoning. Use fake transport for most failures and one bounded real Luna repair on a disposable target. Implement GitHub read/PR operations with the configured gh CLI, disabled for writes until exact host approval. Provide preview.capture for the registered local origin only. No direct worker push or auto-merge.

- **B2-1**: Real configured Luna/max run produces a verified frozen patch on a disposable repository; record effective model/effort and bounded usage. Missing account access is BLOCKED.
- **B2-2**: Tests cover unsupported model/effort, provider error, unknown action request, cancellation, budget/time stop and secret/ANSI redaction, without successful fake fallback.
- **B2-3**: Mock-network PR/local-delivery tests require exact approval and reconcile an ambiguous retry. Preview cannot fetch arbitrary URLs or access unrelated origins.

A live GitHub write is not required for component PASS; no unapproved write is allowed. Full product smoke runs remain I1.

## B3 — structured and selected-screen monitoring

/goal Complete B3 only. Read EXECUTION.md sections 4–5, watcher extension contract and RESEARCH.md's Observer/portal rows only.

Implement lookouts.py, capture_portal.py and local_vision.py. Structured file/process/GitHub sources need no model. Selected-screen support uses the existing Linux portal/PipeWire/GStreamer stack, explicit OS consent, masks, frame-change gating, bounded local inference and persisted event identities/cooldowns. Do not vendor Observer or invent its API. Provide clear capability reporting and enable/disable controls; screen monitoring never grants desktop action permissions.

- **B3-1**: Structured source tests cover stable events/cursors, debounce, coalescing and restarts with zero inference on unchanged input.
- **B3-2**: Capture/model unit tests cover denial/revocation, masks, changed-frame threshold, local-only endpoint validation, bad model JSON, two-positive trigger and cooldown.
- **B3-3**: Run an actual selected-source capture and local-model condition test on the target Linux environment; record source scope/stop behavior without private desktop content. Missing portal/display/model is BLOCKED for this goal, never inferred from fake tests.

The rest of the app may remain usable while the optional capability is unavailable, but a completed B3 requires the actual monitoring evidence.
