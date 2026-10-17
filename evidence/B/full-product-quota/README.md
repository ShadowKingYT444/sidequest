# Subscription reserve readiness checkpoint

Base: `33a4ea15686651e8f6bab9aa4779002688eb027a`. Isolated branch: `repair/quota-reserve-20261014`.

The read-only `agent.capabilities` result adds `subscription_reserve` without changing the existing two nullable `subscription_quota` boolean fields. Only exact Python int/float values, finite and within 0–100, are accepted for `rateLimits.primary.usedPercent` and `rateLimits.secondary.usedPercent`. Strings, booleans, invalid ranges, missing windows, NaN and infinity stay unknown. Both windows must be known to report minimum remaining percentage or readiness. `ready` is true only when minimum remaining is strictly greater than 10%; exactly 10% is false.

This is snapshot readiness telemetry, not a usage reservation or authorization. Provider execution stays unavailable and `usd_cost_enforced` stays false. No model invocation, account refresh, credential copy, authentication grant or spending occurred. All account/rate-limit responses in this checkpoint are deterministic fixtures; real quota is not verified here.

Evidence:

- `red.log`: new reserve regression fails before implementation (missing method).
- `green.log`: all 20 Codex bridge tests pass, including numeric capability telemetry, unknown inputs, threshold boundaries and proof that read-only numeric readiness never opens the USD execution gate.
- `tools.log`: complete tools unit suite result.

Commands: `python3 -m unittest discover -s services/tools/tests -p test_codex_bridge.py -v`; `python3 -m unittest discover -s services/tools/tests -p 'test_*.py' -v`; `git diff --check`.
