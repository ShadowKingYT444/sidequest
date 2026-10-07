# Visual authority: the completed office

The owner has completed the office assets. Preserve them. This replaces the initial factory-machine art brief. Do not generate new art, shop for asset packs, add slogan posters, recreate a new room, or copy screenshots as shipped textures.

Read [ASSET_BINDING.md](ASSET_BINDING.md) for stable anchor/worker bindings and [COMPUTER_UI.md](COMPUTER_UI.md) for actual interaction. The old [screen diagram](design/screen-layout.svg) and [station kit](design/station-kit.svg) remain historical concepts only. They are not instructions to replace the owner's office with six labeled machines. The old external game-reference downloader is optional historical tooling, not a C1 requirement.

## New UI only

Office overview: environment first, small active-worker/status display, quiet notification indicator and visible Stop. No permanent right-hand paragraph panel, floor instructions or fake production statistics. Details open on selecting a worker or using a computer. Preserve the existing palette/materials rather than imposing another art system.

At the computer, Work/Files/Diff/Runs/Preview/Checks are concise tabs. A unified diff and a test screenshot are real content, not decorative code textures. Source/log text is literal, readable and scrollable. Expand enlarges the same view without changing job/run selection. Escape returns to the office. Keep keyboard access, sufficient text contrast and visible disabled/error states. Color alone never indicates failure or authorization.

Actual status comes from backend events. Decorative worker travel never gates execution. Remove repeated movement in reduced-motion mode; do not hide progress changes. No invented model skill multipliers, coffee-token economy or intelligence upgrades. Any cosmetic counter is labeled separately from measured/unknown API cost.

## Visual gate

Capture actual Unity at 1920x1080 and 1280x720: office overview, main-computer diff, image/check evidence, blocked job and enlarged view. Reject clipped/overlapping UI, tiny text, stale data under the wrong worker, fake success animations, or external-browser-only artifact viewing. Preserve completed asset hashes except explicit wiring changes outside protected art files.

This is UI integration, not a new visual-design project. The agent should spend time making the existing computers and workers functional.
