# Existing office assets: binding, not art generation

The owner states that the office assets are finished. That is a fixed input. Inspection of main at 69bf066 found no unity/ project or asset package. The assets may be local to the owner's workspace. Do not infer missing assets from concept screenshots, regenerate them, or claim they were inspected here.

## One-time environment gate before parallel work

Open the owner's actual project. Resolve its root from Assets/, Packages/manifest.json and ProjectSettings/ProjectVersion.txt. Keep its editor patch, render pipeline, input system, materials and scene organization. Record the exact versions and asset location in unity/SETUP.md. When the asset set is not already a project, C creates only the minimal project wrapper compatible with the supplied assets; there is no new art phase.

Import/copy only assets the owner supplied and has rights to use. Preserve their .meta GUIDs when available. Large source assets are brought in before worktrees; do not let a managed worker bypass the controller's large-file guard or commit a generated Library directory. The gate must complete before a release build. A/B/D can still develop against fixtures without the assets.

The coordinator commits this setup baseline before dev/loop.py prepare. Existing active worktrees must first stop/checkpoint; never reset them to adopt a new contract. The implementation lanes then start from one common commit.

## Required bindings

C creates a wrapper SceneBindings/OfficeBindings object, not a second room. Use serialized object references and stable logical IDs. Required references are main computer screen/anchor/bounds/focus pose; at least four worker desk anchors and monitor anchors; board anchor; review area; workshop area; spawn/idle poses; overview camera pose. These are roles mapped onto existing desks/props; do not add six factory machines merely to match the old drawing.

Worker IDs are backend identifiers. Desk IDs are layout identifiers. A binding table maps them; array order and GameObject names are not identity. Validate duplicate/missing IDs, null refs and unusable monitor bounds in an Editor test. A missing reference is a concrete binding error, not permission to redesign furniture. When no dedicated prop exists for a role, use an existing surface plus an unobtrusive interaction hotspot.

Keep all completed art under its existing folders; record a manifest of GUID/path/hash before wiring. C may add scripts, wrappers, UI and scene references, but must not edit source meshes, textures, character art or lighting without an explicit owner decision. An automated comparison reports any protected asset changes. A script on a wrapper does not require modifying the original asset prefab.

## Visual authority

The owner's supplied office is the visual authority. The later calm-office concepts are mood references only. Earlier robot-factory boards, floor arrows, slogans and text-heavy inspectors are superseded. No image generation, new props, asset browsing, style exploration or shader framework work is part of C1.

Preserve clear walking space. Display details at the computer or a short selected-worker card. One quiet status indicator per active object; no continuously printed explanation labels. Reduced-motion mode removes decorative travel, not status updates. Cosmetic office placement must not grant permissions or alter running task dependencies.

## Evidence

Record the asset baseline and actual Unity version; run binding validation; capture the unchanged office plus the newly functional monitor. At least one screenshot must show a real diff on that monitor and another must show enlarged-view readability. Screenshots are evidence of rendering only, not proof that the backend action succeeded.
