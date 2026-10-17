# Lane D journal

## D1 — trusted browser check and frozen candidate identity

Implemented the Python `check.run` adapter, trusted check definitions, candidate manifest/hash verification, bounded Chromium/Playwright journey, redacted reports and evidence under `services/workshops/`, with disposable bad and known-good club-site fixtures in `demo/club-site/`. The harness reads only its registered fixture routes, blocks external origins, checks candidate identity before and after the journey, and does not call a model or production service.

Validation: `python3 tests/e2e/run_d1.py` returned `bad_passed=false`, `known_good_passed=true`, `unittest_exit_code=0`. It ran `/usr/bin/chromium` 151.0.7922.173 with Playwright 1.62.0 and the required `python3 -m unittest discover -s services/workshops/tests -p 'test_*.py' -v`; all 13 tests passed. The bad signup popup produced `SIGNUP_DESTINATION_MISMATCH`; the frozen control reached `/members/welcome` and passed. Browser logs record one blocked external-origin request per case. All returned screenshot, log and report digests verified.

Evidence: `evidence/D/D1.json`, `evidence/D/unittest-20261014t015727796417z.log`, manifests in `evidence/D/inputs/`, and browser artifacts in `evidence/D/outputs/`. D2 recipes remain deferred.


## CI blocked-result diagnosis — October 17, 2026

PR-head 1375bf1 failed workshop test_candidate_authored_checks_and_destination_cannot_turn_bad_case_green: the browser check returned blocked rather than the required fail. CI discarded fixture artifacts and printed no check code. Launcher/runtime/provider tests passed; desktop tests/build were skipped by the failed workshop step. The workshop source predates the compact interface and is unchanged by that candidate.

Added trusted result codes/events to assertion failure messages so the next execution can distinguish browser startup, screenshot, timeout and candidate identity failures. Strengthened the shadow test to require SIGNUP_DESTINATION_MISMATCH explicitly. No timeout, skip, browser/security flag, expected outcome or production code change. This is an instrumented diagnostic candidate, not a claimed root-cause repair or blind retry. Independent VM compact interface/recovery checks report 5/5 passing separately. Next: inspect this candidate's CI result before deciding on a production repair.
