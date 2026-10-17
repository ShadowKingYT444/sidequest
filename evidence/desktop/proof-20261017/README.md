# Sidequest visual proof — 17 October 2026

[Watch the 39.5-second MP4](walkthrough-browser.mp4) · [Original 55.75-second WebM](walkthrough-raw.webm) · [Verification](verification.json)

**Passed on the first attempt.** This is the actual browser UI running through `sidequest.py run --browser`, with the original office assets, installed Chromium/SwiftShader, and a fresh trusted local Git project. The local inspection passed its frozen-identity check with **zero model calls, $0 spent, no mocked responses, and no page errors**. It is browser proof, not native Electron or live coding proof.

The MP4 removes only the first 16.25 seconds of initial loading and adds a scope caption below the uncropped app. All interactions remain in their original order at normal speed; there are no later cuts. The untouched recording is retained once. Screenshots are unedited.

| Approximate MP4 position | Demonstrated behavior | Screenshot |
| --- | --- | --- |
| 00:00 | Original office loaded; 26 staged figures | [Office](01-office.png) |
| 00:06.5 | Physical monitor click; unsent text, local file and image inputs; Send disabled | [Monitor draft](02-monitor-draft.png) |
| 00:13.5 | Actual committed Git changes in the expanded read-only viewer | [Git diff](03-git-diff.png) |
| 00:21.5 | Fresh repository registered; zero-budget inspection queued | [Queued inspection](04-inspection-queued.png) |
| 00:24 | Real inspection passed; immutable README content displayed | [Inspection result](05-inspection-result.png) |
| 00:26.5 | Frozen check report displays `inference_calls: 0` | [Check report](06-check-report.png) |
| 00:27 | Recorded run completed; activity says “No model call” | [Run activity](07-run-activity.png) |
| 00:33 | Coding remains unavailable; spending enforcement is absent | [Coding status](08-coding-unavailable.png) |
| 00:36.5 | Actual CLI discovery; authentication and reachability unknown | [Provider settings](09-provider-settings.png) |
| 00:37 | Usage totals and telemetry honestly unavailable | [Usage](10-usage-unavailable.png) |

Timestamps identify representative frames matched against screenshots at 4 Hz; see [frame matches](video-step-matches.json). [Steps](steps.json) preserve the separate automation-clock timings.

Application checkpoint: `bdf2fdd51196634293588ac38a9845e02894dab0`. All **253** recorded source, test, asset and launcher hashes were unchanged before/after capture. [Run context](run-context.json) includes exact fixture commits, launcher command and hashes. The launcher used an ephemeral in-process API token and coding-disabled state outside Git. Both services stopped cleanly; ports were released and no token files or credential markers were found in state. [Launcher log](launcher.log) and [browser result](browser-verification.json) retain the evidence.

The fixture contains two ordinary commits and no credentials. The inspection checks immutable bytes; it does not run arbitrary project tests or change/deliver source. Its backend job remains `verifying` after results are ready because delivery is disabled, as explained in the visible UI. Text/files/images stayed local and unsent. The screen does not establish provider login, live coding, usage integration or native desktop support. Wider feature coverage is documented in the [25-case browser validation](../startup-browser-20261017/README.md).

Capture implementation: [launcher/fixture runner](run-capture.py), [Playwright walkthrough](capture.mjs). It used installed `/usr/bin/chromium` and `/usr/bin/ffmpeg`; no dependency downloads or provider turns. For a new capture, copy these two scripts into a new evidence directory first, then run its `run-capture.py` from this checkout so this evidence is preserved. [Media processing](media-processing.json) records the exact MP4 conversion; both videos passed a complete decode. [SHA-256 manifest](manifest.json) identifies every deliverable.
