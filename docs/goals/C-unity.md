# Lane C — Unity client and art

Own only: `unity/`, `journals/C.md`, `evidence/C/`. Read AGENTS.md and contracts/PROTOCOL.md. Three goals; finish and validate one before the next. Shared files are read-only.

## C1: Create the actual Unity project and visual foundation

/goal Complete C1 from docs/goals/C-unity.md. Meet all C1 checks. Keep journals/C.md. Do not start the next goal.

Inspect installed editor. Create a Unity 6 desktop project with URP, record exact editor/package lock and use Force Text. All .meta files belong here. Do not hand-invent an installed version.

Read ART_DIRECTION and view both local SVG boards and external game screenshots. Create one orthographic miniature workshop scene with all six distinct building silhouettes and a small worker crew. No stock SaaS dashboard.

Acceptance evidence:

- **C1-1** — Open and compile in the recorded editor, zero new Console errors; report actual version and test command.
- **C1-2** — Capture actual scene at 1920x1080 and 1280x720; compare composition and silhouettes against references, not a mockup.
- **C1-3** — All assets include .meta; no generated Library files, unlicensed shipped textures or unexplained package additions.

## C2: Implement all first-build interactions against fixtures

/goal Complete C2 from docs/goals/C-unity.md. Meet all C2 checks. Keep journals/C.md. Do not start the next goal.

Build snapshot polling, commands, world selection, mission board, inspection panel, approvals, workshop activation/pause, layout connections and compact task-list fallback.

Use dev/mock_runtime.py or a lane-owned richer fixture server. Make fixture mode unmistakable. UI state comes from snapshots, not local success timers. Add accessible text/icons and keyboard controls.

Acceptance evidence:

- **C2-1** — PlayMode tests exercise create, assign, inspect, pause, approve and workshop actions against fixture responses.
- **C2-2** — HTTP failures, stale revision and failed checks visibly block progress; animation cannot bypass state.
- **C2-3** — Record an actual interaction clip/screenshots with fixture badge, small-screen legibility and reduced-motion mode.

## C3: Package and validate the complete presentation

/goal Complete C3 from docs/goals/C-unity.md. Meet all C3 checks. Keep journals/C.md. Do not start the next goal.

Polish lighting, materials, job motion and readable states using the design rubric. Provide startup config for real runtime without requiring its code to exist in this branch.

Produce a Linux desktop build, test it with the fixture service, and provide evidence and instructions. Close builder editor before the fresh validator opens its candidate checkout.

Acceptance evidence:

- **C3-1** — Fresh validator builds/launches the desktop target and exercises the fixture workflow; missing editor/display is BLOCKED.
- **C3-2** — Capture own screenshots at both sizes and review all design rubric items, including no overlaps, labels and silhouettes.
- **C3-3** — Test disconnect/reconnect, unknown state, client close/reopen and stop control; outputs remain explicitly fixture mode.
