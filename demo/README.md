# D1 disposable browser fixture

`club-site/bad` contains one seeded defect: its “Join the club” link opens a
plausible confirmation page at the wrong path. `club-site/known-good` opens the
trusted `/members/welcome` destination in a popup and shows the confirmation
there. Both are inert static fixtures; they contain no credentials, account
integration, or production destination. The D1 checker serves each fixture on a
temporary loopback origin and blocks browser requests to every other origin.

The trusted destination and check IDs are installed under
`services/workshops/trusted_checks.json`, outside these candidate snapshots.
Candidate files named like the checker or its definitions are treated as data
and never imported.

Run the D1 browser and protocol evidence with:

```sh
python3 tests/e2e/run_d1.py
```

The script uses the configured `CHROMIUM_PATH`, defaulting to the already
installed `/usr/bin/chromium`. It does not download a browser.
