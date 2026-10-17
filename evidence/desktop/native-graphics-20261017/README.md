# WebGL failure diagnosis and recovery — 17 October 2026

The independent desktop VM passed native shell/isolated IPC but failed to render the office with `WebGL2 blocklisted`. The previous UI mislabeled every scene error as unimported assets. This repair attributes graphics, bindings, model-loading and unknown scene failures separately, exposes Retry office/recovery instructions, and keeps Git, Settings and Jobs available. The footer no longer says figures are loading after a fatal scene failure. Retrying clears the failed office-model cache where appropriate without replacing original art or discarding the App's draft stores.

## Independent VM verification

The [unaltered independent report](vm/GRAPHICS-VERIFICATION.txt) and [hashed import manifest](vm/manifest.json) now establish **2/2 sandbox-enabled browser regressions**, three classification tests and a production build on the transferred graphics-recovery source. Browser cases deliberately inject graphics/bindings failures. Actual native Electron also showed the correct graphics diagnosis, safe retry, retained Git/Settings/Jobs and local inspection artifacts. The physical office still fails on this VM's WebGL2 stack.

[Native recovery screenshot](vm/captures/native-graphics-recovery.png) shows the genuine failure. [Recorded-session/draft reload screenshot](vm/captures/native-reload-recovery.png) predates the graphics patch and establishes local recorded output/draft retention, not live provider execution. The report identifies the archive and applied transfers precisely; it is not a full checkout of a later published commit. The subsequent compact UI candidate also removes unsafe graphics defaults from the shared Playwright config; its visual checks remain separate.

## Historical coding-container checks and limits

- [Red regression](red/browser.log), [original failure context](red/playwright-results/office-failure-WebGL-failu-3efd5-aves-local-tools-accessible/error-context.md): injected `WebGL2 blocklisted` before implementation reproduces the false asset claim.
- [90 desktop tests pass](unit.log), including three classification/privacy regressions. [Final TypeScript/production build passes](build-final.log).
- [Initial browser repair run](browser-green.log): 1 passed (bindings retry), 1 failed. Graphics diagnosis, retry, Git and Settings assertions passed; the new test incorrectly looked for a Jobs dialog rather than the actual Local jobs board region. The selector is corrected. [Intermediate screenshot](green/graphics-unavailable.png) is from this injected-error run before final spacing styles; it is not native evidence.
- [Final sandbox-preserving browser attempt](browser-sandbox.log): blocked before page startup by this container's unsupported SUID sandbox helper. The final regression explicitly removes Playwright's automatic `--enable-unsafe-swiftshader` and enables Chromium sandbox. No sandbox permission or production graphics flag was changed. Earlier browser runs used the pre-existing Playwright harness defaults; those are UI evidence, not production graphics/security acceptance.
- No provider turn, account login, runtime mutation, imported art change, GPU-blocklist override or sandbox change was made. The later independent VM result is recorded above.

Run the final regression on a sandbox-capable host from `desktop/` (with a fresh evidence directory and the configured trusted Git repository):

```sh
SIDEQUEST_EVIDENCE_DIR=/absolute/path/to/new-evidence npx playwright test tests/browser/office-failure.spec.ts --reporter=line --output=/absolute/path/to/new-evidence/playwright-results
```

It injects graphics/bindings failures intentionally. It establishes recovery UI behavior, not successful real WebGL rendering or AI execution.

## Supported software rendering investigation

[Chromium's SwiftShader documentation](https://chromium.googlesource.com/chromium/src/+/main/docs/gpu/swiftshader.md) documents the OpenGL ES driver route `--use-gl=angle --use-angle=swiftshader` separately from its unsafe WebGL fallback. The latter requires an explicit reduced-security opt-in and is not a production recovery recommendation. [Electron's API](https://www.electronjs.org/docs/latest/api/app#appdisablehardwareacceleration) supports disabling hardware acceleration before readiness, but that does not promise WebGL2 availability. Electron's documented supported-switch list does not establish the Chromium driver flags as a portable Electron fix.

A sandbox-enabled Chromium driver probe here stopped at the same SUID-helper startup failure, before a context could be tested. Inspection also revealed Playwright's automatically added unsafe SwiftShader default; the final regression removes it. We have not established a compatible software-driver solution on the native VM. No automatic or persistent fallback is shipped. The safe available recovery is an honest error, retained local tools and trying a normal desktop/browser with working WebGL2; browser mode is not a guarantee that this VM can render 3D.
