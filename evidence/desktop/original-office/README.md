# Integrated UI update

Root cherry-picked the asset source commit as `6b4db20` and mounts all 26 supplied reference figures with 20 original caps. Typing/Point/Walk poses are sampled once and labeled staged/unconnected. The integrated UI disables unnecessary Meshopt, keeps CSP unchanged, loads embedded original textures through TextureLoader and replaces secondary monitor HTML roots with lightweight canvas UI textures. The final overview uses a closer/brighter presentation without changing imported geometry/material bytes. Original workstation pick metadata and measured monitor/board bindings drive object interactions.

The asset-task failure is retained as `asset-import-browser-validation.json`, `browser-capture.log` and `browser-binding-first-attempt.log`; current browser-validation.json belongs to root integration. The source report below describes the asset-only checkpoint and its then-current failure. See the parent directory verification.json for final UI source hashes and acceptance scope.

# Original office recovery and integration

This branch is based on `1e4b7440cb526f09203a7351af1abe8b69dd922f` and owns only `desktop/public/office/` and this evidence directory. It imports the owner's October 7 art kit. No UI, backend, Unity, authentication, or security files changed.

## Recovered originals

All eight Drive archive parts were downloaded from approved hosts. Every part passed the supplied checksum. The reconstructed archive is **535,951,540 bytes**, SHA-256 `f7159fbda50771486d65e1a5bd2a42d265120a422d88a686471a9bbb6fb60a95`. Before extraction, every archive path and entry type was checked: 1,725 entries, 1,336,239,187 uncompressed bytes, no links, special entries, absolute paths, traversal or duplicate paths. No bundled archive scripts were run.

The parts, reconstructed archive, extracted kit, native master and original embedded runtime GLB remain outside Git at `/workspace/sidequest-originals/`. They are not required to run the imported desktop assets.

## Runtime assets

- `office.glb`: original batched environment geometry, materials, semantic roots and anchors. The 131,678,516-byte source GLB exceeds Git's single-file limit. Its 90 original image payloads were relocated unchanged into local texture files; the resulting GLB is 54,670,564 bytes. No image recompression, mesh simplification, replacement furniture or new art was used. `lossless-resource-verification.json` records source/output hashes and byte identity.
- `bindings.json`: 24 stable desk IDs (`parent_001`–`parent_024`), measured left-monitor surfaces, focus poses, original board surface and an overview derived from the supplied full-office camera. Collection instances were evaluated in Blender 4.3.2 at frame 48 with automatic script execution disabled. Coordinates are glTF Y-up metres. All 24 source monitor meshes match runtime geometry within 0.00000154 metres. No authored actor ID is assigned as a backend worker ID.
- `provenance.json`: archive, source GLB, native master, installed GLB and all copied-resource hashes.
- `actors.json`, `actors/`, `caps/`: seven original human variants (including Slate's cap-ready companion), twelve original fit/identity caps, six exact identity textures and original attachment profiles. Each human retains one 17-joint skin and Idle, Typing, Walk and Point clips. All copies match source bytes.

## Integrate

Fetch `assets/original-drive-import-v2` and cherry-pick its reviewed asset commit into the UI branch. The runtime assets are deliberately tracked on this branch despite the existing local-input ignore rule. Rebuild the desktop with `npm run build`; Vite copies all local resources into `dist/office/` for Electron. Use the supplied same-origin `/office/office.glb` and `/office/bindings.json` paths; no external decoder is needed.

The static environment intentionally excludes staged people and subordinate assemblies, as documented by the supplied kit. The captured overview therefore shows the actual room, furniture and empty chairs. The UI owner can spawn the unchanged rigged models from `actors.json`; `stagedReferenceInstances` records the original visual placements and pose hints. These are artwork references, not connected sessions. Apply each supplied glTF matrix once. Use the corresponding cap fit, shared head joint and original inverse head-rest matrix. Slate's branded cap requires the cap-ready companion. Do not add a second environment or infer live ownership from the artwork. Child mini-computer assemblies remain in the preserved source kit for future lifecycle integration.

## Verification and remaining integration issue

`npm ci --ignore-scripts --cache /tmp/sidequest-assets-npm-cache`, `npm test` (27/27), and `npm run build` passed. `validate-assets.mjs` passed the actual binding parser, every monitor's source-to-runtime geometry comparison, all resource hashes and local URL validation. Browser captures show the real imported office, actual committed Git diff at Computer 19, readable expanded viewer and Escape return. Additional browser checks selected Computers 01, 03, 19 and 24 and confirmed the measured board hotspot opens the existing jobs region. Seven original rigged humans, all 28 retained clips and twelve caps loaded and rendered through the browser GLTFLoader without additional actor errors. All 92 office HTTP requests returned 200 and none failed.

The integrated capture's clean-console assertion **failed**: `OfficeScene.tsx:37` enables Meshopt in `useGLTF(url, false, true, ...)`, causing the loader to initialize WebAssembly that the app's existing `script-src 'self'` CSP blocks. The imported assets have no required compression extensions. The UI owner should disable the unnecessary Meshopt decoder (`useGLTF(url, false, false, ...)`) and rerun the integrated browser check. A response-only diagnostic probe disabled that one loader option and rendered the office and Git diff with zero page errors; see `loader-fix-probe.json`. Product files and CSP remained unchanged. No CSP or security setting was changed here. The failure is retained in `browser-capture.log` and `browser-validation.json`; rendering success is not a clean-console pass. Native Electron execution and owner-device performance were not measured in this asset task.

The overview screenshot was saved to Library as `libfile_7987934df1cc8191a62fcc1dd8d08c2c`, File Service ID `file_0000000070fc81f58457ad0aad239f9c`. `screenshot-library.json` ties its persisted identity to the captured PNG's checksum.

To rerun local validation after installing desktop dependencies:

```sh
node evidence/desktop/original-office/validate-assets.mjs
cd desktop
npm test
npm run build
npm run dev
# In another terminal at the repository root:
node evidence/desktop/original-office/capture-browser.mjs
node evidence/desktop/original-office/check-browser-bindings.mjs
node evidence/desktop/original-office/check-browser-actors.mjs
```

No merge or deployment was performed.
