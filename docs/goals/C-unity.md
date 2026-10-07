# C — existing office and functional computers

Own unity/, journals/C.md and evidence/C/. You are the only Unity writer. Assets are complete: no replacement art, furniture, workers, shaders or room. Read the current goal's sources only. The old robot-factory diagrams are historical and must not direct asset creation.

## C1 — bind the existing project

/goal Complete C1 only. Read AGENTS.md, ASSET_BINDING.md, ART_DIRECTION.md and COMPUTER_UI.md implementation section.

Open the owner's actual project, record editor/lock/render/input state and protect its art manifest. Create OfficeBindings and wrapper components for supplied desk screens, worker stations, board, review/workshop areas and camera poses. Validate stable IDs and serialized references. Create the specified Client/Presentation/Editor assembly boundary and explicit OfficeBootstrap; do not introduce a new architecture or regenerate assets. Implement camera focus/return and a minimal native world-space monitor surface using supplied bounds.

- **C1-1**: Actual editor opens/compiles; binding test detects missing/duplicate/null anchors; record exact installed version and module availability.
- **C1-2**: Capture supplied office at both target sizes with main monitor focus/return; art hashes remain unchanged except permitted scene wiring/wrappers.
- **C1-3**: Metadata and dependency lock are correct; no Library/Temp/build output committed; no replacement assets or conflicting EventSystem/input module.

Missing assets/editor is BLOCKED, not a request to invent a room. Use UNITY_EDITOR and named Unity test methods; record actual commands/results before review.

## C2 — real artifact and swarm controls inside computers

/goal Complete C2 only. Read COMPUTER_UI.md in full, contracts/EXTENSIONS.md and the base snapshot/commands. Build against a lane-owned fixture server, not another lane's unfinished code.

Implement RuntimeClient/SnapshotStore/WorkerPresenter and the named computer views. Main computer is project-wide; worker computers are correctly scoped. Implement Work, Files, Diff, Runs, Preview, Checks; selected job assignment/pause/resume/cancel, exact approval, workshop activation/pause and watcher capability/settings. Same view model for world-space and enlarged views. Native text/diff/image viewing is mandatory. Pool rows, bound pages/images, sanitize text, suppress stale requests and label fixture/unverified data. Never spawn a browser to substitute for the core viewer.

- **C2-1**: Interaction tests cover project/worker selection and all viewer tabs using added/edited/renamed/deleted/binary fixture files; focus/Expand/Escape preserve state.
- **C2-2**: Tests cover long text, paging, literal TMP markup/ANSI, invalid image, stale responses, 403/409/disconnect and blocked approval. No fake success timers.
- **C2-3**: Actual PlayMode capture shows job controls, artifacts, test evidence, workshop and watcher state inside the monitor; fixture badge visible and Stop available.

Keep fixture server and tests inside unity/ so there is no ownership overlap. Code and UI must use the frozen endpoint shapes.

## C3 — desktop build and usability proof

/goal Complete C3 only. Read ART_DIRECTION.md's visual gate, COMPUTER_UI.md acceptance section and FEATURE_MATRIX.md UI/COST assertions.

Implement Linux build entry Sidequest.Editor.BuildLinux.Perform and document the precise editor invocation. Run native EditMode/PlayMode suites, build and launch the desktop app against the fixture service. Test reduced motion, keyboard focus, reconnect, client restart and monitor readability. Do not wait for backend source or claim a fixture proves the full product. Close the builder editor before independent candidate validation.

- **C3-1**: Fresh validator builds/launches actual desktop target and uses the main computer with fixture service; missing license/display/module is BLOCKED.
- **C3-2**: Real 1920x1080 and 1280x720 captures show diff, image, checks and blocked state with readable unclipped UI and preserved completed assets.
- **C3-3**: Input/reconnect/close-reopen/reduced-motion tests pass; idle/viewing makes no model call and backend state is never inferred from animation.
