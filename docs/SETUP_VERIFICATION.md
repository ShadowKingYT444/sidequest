# Launch-kit verification — October 4, 2026

This record covers development tooling only. No Sidequest product feature, real Codex model run, Unity scene, or live GitHub delivery was tested here.

Environment: Python 3.13.5, Git 2.47.3, Linux container. The checked-in CI workflow targets Python 3.11; its remote result must be checked separately.

Executed:

```bash
python3 -m unittest discover -s dev -p 'test_*.py' -v
python3 dev/check.py --setup
```

Result: **15 tests passed**. They exercise local Git worktree preparation, same-base branches, refusal to overwrite existing setup, out-of-lane edits, rename and symlink escapes, exact-SHA verdicts, missing/duplicate checks, locks, bounded failed-review retries, blocked-review recovery, four-lane assembly and preservation of main. JSON-lines transport tests launch a fake local server and verify fresh thread IDs and blocked/budget-limited stops. These prove controller behavior under the test doubles, not compatibility with a particular installed Codex build.

The static check verifies disjoint ownership, goal/check IDs, internal documentation links, Python parsing, SVG XML and fixture labeling. The two original SVG design boards were rendered locally and inspected. They are diagrams, not Unity screenshots. External game images are linked with provenance; the local reference downloader could not be tested against the image hosts in this network-restricted environment.

Remaining validation: run the installed Codex app-server against one goal, provide Unity editor/build-module access for C, configure a bounded coding provider for B, install D's browser dependencies, and execute I1 on the merged product. Missing tools or unobserved results must stay BLOCKED.
