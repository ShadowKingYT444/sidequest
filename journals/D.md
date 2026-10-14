# Lane D journal

## D1 — trusted browser check and frozen candidate identity

Implemented the Python `check.run` adapter, trusted check definitions, candidate manifest/hash verification, bounded Chromium/Playwright journey, redacted reports and evidence under `services/workshops/`, with disposable bad and known-good club-site fixtures in `demo/club-site/`. The harness reads only its registered fixture routes, blocks external origins, checks candidate identity before and after the journey, and does not call a model or production service.

Validation: `python3 tests/e2e/run_d1.py` returned `bad_passed=false`, `known_good_passed=true`, `unittest_exit_code=0`. It ran `/usr/bin/chromium` 151.0.7922.173 with Playwright 1.62.0 and the required `python3 -m unittest discover -s services/workshops/tests -p 'test_*.py' -v`; all 13 tests passed. The bad signup popup produced `SIGNUP_DESTINATION_MISMATCH`; the frozen control reached `/members/welcome` and passed. Browser logs record one blocked external-origin request per case. All returned screenshot, log and report digests verified.

Evidence: `evidence/D/D1.json`, `evidence/D/unittest-20261014t015727796417z.log`, manifests in `evidence/D/inputs/`, and browser artifacts in `evidence/D/outputs/`. D2 recipes remain deferred.
