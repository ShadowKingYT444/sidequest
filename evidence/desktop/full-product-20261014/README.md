# Full product checkpoint — blocked

Continued from published PR head `33a4ea15686651e8f6bab9aa4779002688eb027a`. The October 14, 2026 19:54 UTC deadline was missed. This checkpoint establishes independently tested readiness work and fresh host failures, not complete product acceptance.

Implemented: the read-only Codex capability result reports strict primary/secondary usage and a nullable 10% reserve snapshot. Both numeric windows must be finite and in 0–100; unknown/invalid values remain unknown. Readiness requires strictly more than 10% remaining. Runtime refresh/cache/public capabilities preserve this telemetry, discard unrelated account data and recompute derived values instead of trusting adapter claims. The readiness cache preserves fractional JSON numbers; the monetary canonicalizer had converted them to strings. No USD or dispatch gate was relaxed. A quota snapshot does not reserve future usage or authorize spending.

TDD evidence:

- Bridge reserve regression: [red](../../B/full-product-quota/red.log), [green](../../B/full-product-quota/green.log).
- Runtime propagation and fractional-cache regression: [red](reserve-api-red.log), [first repair still failing](reserve-api-green.log), [final green](reserve-api-green-final.log). Boundary, invalid, privacy, cached-read and stale-read assertions remain intact.
- Integrated checks: **50 runtime**, **44 tools**, **50 desktop** tests pass. [Runtime log](runtime-tests.log), [tools log](tools-tests-integrated.log), [desktop log](desktop-tests.log), [typecheck/build log](desktop-build.log).
- [Exact verification and hashes](verification.json). All 126 protected art hashes and the earlier frozen 20-test browser log remain unchanged. The prior browser pass is on `abf9496`, published with evidence at `33a4ea1`; the browser suite was not rerun for this backend readiness checkpoint. UI source and assets are unchanged.

Fresh host evidence:

| Action and target | Outcome and reason | Required next prerequisite |
| --- | --- | --- |
| Direct Electron 44.7.1 startup, original sandbox enabled | SIGTRAP, return code -5. Local helper is uid 1000 / mode 0755; Chromium aborts. No desktop display is configured. [Record](native-startup.json), [log](native-startup.log). | A managed sandbox-capable desktop host with a display. No helper permissions or security settings were changed here. |
| Read-only Codex app-server initialization; existing auth locator and separate writable `/tmp` SQLite state | Exit 1, zero initialization responses, `Read-only file system (os error 30)`. [Record](codex-initialize.json), [stderr](codex-initialize.stderr.log). | A supported writable runtime layout preserving the original authentication, or an existing supported authenticated host endpoint. No protected state was copied or redirected. |
| Existing CLI login status | Exit 0, `Logged in using ChatGPT`. [Log](codex-login-status.log). This does not verify app-server account reachability, quota or dispatch. | Fresh supported app-server account/quota reads after initialization works. |
| Real model/session dispatch | Product policy denies execution: no verified enforceable USD ceiling. Actual quota and the requested 10% reserve remain **unverifiable**. | Verified provider/host enforcement and reserve telemetry, without authorizing new spending or bypassing the guard. |

The existing compact office, recorded trace, artifacts/diffs, completion/attention fixtures and reload ownership remain supported browser flows. A real agent session at an empty desk, same-session follow-up messages, supported attachment sending and reconnect to a live provider are not accepted workflows yet. The public runtime has no message/attachment transport; Send remains disabled and files stay local. These are remaining implementation/verification gaps, not completed features.

No model turn, paid spending, new authentication, credential copying, sandbox weakening, security permission changes, merge, deployment or force push occurred. The old integrator was not restarted. Failed logs, original source/art and earlier screenshots remain preserved. Estimate: **2–4 additional hours after the required host and spending prerequisites become available**; this is an estimate, not a completion promise.
