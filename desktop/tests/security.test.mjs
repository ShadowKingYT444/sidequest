import assert from 'node:assert/strict';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import os from 'node:os';
import path from 'node:path';
import vm from 'node:vm';
import test from 'node:test';

const require = createRequire(import.meta.url);
const security = require('../electron/security.cjs');
const { createStaticAssetHandler } = require('../electron/static-server.cjs');
const preloadSource = readFileSync(new URL('../electron/preload.cjs', import.meta.url), 'utf8');
const mainSource = readFileSync(new URL('../electron/main.cjs', import.meta.url), 'utf8');
const staticSource = readFileSync(new URL('../electron/static-server.cjs', import.meta.url), 'utf8');

test('preload exposes fixed read and validated local-runtime capabilities without shell or credentials', async () => {
  const calls = [];
  let exposed;
  const electron = {
    contextBridge: { exposeInMainWorld: (name, api) => { exposed = { name, api }; } },
    ipcRenderer: { invoke: (...args) => { calls.push(args); return Promise.resolve({ ok: true }); } },
  };
  vm.runInNewContext(preloadSource, {
    require: (name) => {
      assert.equal(name, 'electron');
      return electron;
    },
    Promise,
    Error,
    Object,
  });

  assert.equal(exposed.name, 'sidequest');
  assert.deepEqual(Object.keys(exposed.api), ['runtime', 'snapshot', 'diff']);
  assert.equal(Object.isFrozen(exposed.api.runtime), true);
  assert.deepEqual(Object.keys(exposed.api.runtime), ['snapshot','capabilities','job','artifact','artifacts','files','text','diff','register','submitInspection','run','stop']);
  assert.equal(Object.isFrozen(exposed.api), true);
  assert.deepEqual(await exposed.api.snapshot(), { ok: true });
  assert.deepEqual(calls, [['sidequest:snapshot']]);
  await exposed.api.diff('f_' + 'a'.repeat(32));
  assert.deepEqual(calls[1], ['sidequest:diff', 'f_' + 'a'.repeat(32)]);
  await assert.rejects(exposed.api.diff('../secret'), { code: 'INVALID_INPUT' });
  assert.equal(calls.length, 2, 'invalid identifiers never cross IPC');
  await exposed.api.runtime.run('job-1', 12);
  assert.equal(JSON.stringify(calls[2]), JSON.stringify(['sidequest:runtime', 'run', ['job-1', 12]]));
});

test('Electron security helpers trust only the app origin or configured loopback dev origin', () => {
  const devServer = security.normalizeDevServerUrl('http://127.0.0.1:5173');
  assert.equal(devServer.origin, 'http://127.0.0.1:5173');
  assert.equal(security.isTrustedRendererUrl('app://sidequest/index.html'), true);
  assert.equal(security.isTrustedRendererUrl('app://elsewhere/index.html'), false);
  assert.equal(security.isTrustedRendererUrl('file:///tmp/index.html'), false);
  assert.equal(security.isTrustedRendererUrl('http://127.0.0.1:5173/src/main.tsx', devServer.origin), true);
  assert.equal(security.isTrustedRendererUrl('http://127.0.0.1:5174/', devServer.origin), false);
  assert.equal(security.isTrustedRendererUrl('https://127.0.0.1:5173/', devServer.origin), false);
  assert.throws(() => security.normalizeDevServerUrl('https://example.com'));
  assert.throws(() => security.normalizeDevServerUrl('http://example.com:5173'));
  assert.throws(() => security.normalizeDevServerUrl('http://user@127.0.0.1:5173'));
});

test('IPC sender validation requires the current main frame and opaque file IDs', () => {
  const mainFrame = { url: 'app://sidequest/index.html' };
  const webContents = { mainFrame };
  const window = { webContents };
  assert.equal(security.isTrustedIpcSender({ sender: webContents, senderFrame: mainFrame }, window), true);
  assert.equal(security.isTrustedIpcSender({ sender: webContents, senderFrame: { url: mainFrame.url } }, window), false);
  assert.equal(security.isTrustedIpcSender({ sender: {}, senderFrame: mainFrame }, window), false);
  assert.equal(security.isTrustedIpcSender({ sender: webContents, senderFrame: { url: 'file:///tmp/evil' } }, window), false);
  assert.equal(security.isValidFileId('f_' + 'b'.repeat(32)), true);
  for (const invalid of ['../file', 'f_' + 'b'.repeat(31), 'f_' + 'b'.repeat(33), null, 7]) {
    assert.equal(security.isValidFileId(invalid), false);
  }
});

test('BrowserWindow and main process keep Node access disabled and deny navigation, windows, downloads, and capture', () => {
  const prefs = security.secureWebPreferences('/app/electron/preload.cjs');
  assert.equal(prefs.preload, '/app/electron/preload.cjs');
  assert.equal(prefs.sandbox, true);
  assert.equal(prefs.contextIsolation, true);
  assert.equal(prefs.nodeIntegration, false);
  assert.equal(prefs.webSecurity, true);
  assert.equal(prefs.allowRunningInsecureContent, false);
  assert.equal(prefs.webviewTag, false);

  assert.match(mainSource, /contents\.setWindowOpenHandler\(\(\) => \(\{ action: 'deny' \}\)\)/);
  assert.match(mainSource, /setPermissionRequestHandler\([^\n]+callback\(false\)/);
  assert.match(mainSource, /setPermissionCheckHandler\(\(\) => false\)/);
  assert.match(mainSource, /setDisplayMediaRequestHandler\([^\n]+callback\(\{\}\)/);
  assert.match(mainSource, /will-download/);
  assert.match(mainSource, /will-navigate/);
  assert.match(mainSource, /will-redirect/);
  assert.match(mainSource, /will-attach-webview/);
  assert.match(mainSource, /protocol\.handle\('app', serveAppRequest\)/);
  assert.match(staticSource, /path\.resolve\(root, 'public', relative\)/);
  assert.match(staticSource, /model\/gltf-binary/);
  assert.match(staticSource, /worker-src 'self' blob:/);
  assert.match(staticSource, /frame-src 'none'/);
  assert.match(mainSource, /SIDEQUEST_DEV_SERVER_URL/);
  assert.match(mainSource, /SIDEQUEST_REPO/);
  assert.match(mainSource, /SIDEQUEST_BASE/);
  assert.doesNotMatch(mainSource, /--no-sandbox/);
  assert.doesNotMatch(preloadSource, /ipcRenderer\.(?:send|on|once|sendSync)\s*\(/);
});

test('app protocol serves dist assets and root office URLs from copied public assets safely', async (t) => {
  const temp = mkdtempSync(path.join(os.tmpdir(), 'sidequest-app-protocol-'));
  const dist = path.join(temp, 'dist');
  const publicDir = path.join(dist, 'public');
  mkdirSync(publicDir, { recursive: true });
  writeFileSync(path.join(dist, 'index.html'), '<main>Sidequest</main>');
  writeFileSync(path.join(publicDir, 'room.glb'), Buffer.from([0, 1, 2, 3]));
  const outside = path.join(temp, 'outside.txt');
  writeFileSync(outside, 'private');
  symlinkSync(outside, path.join(publicDir, 'escape.txt'));
  t.after(() => rmSync(temp, { recursive: true, force: true }));
  const serve = createStaticAssetHandler(dist);

  const root = await serve({ method: 'GET', url: 'app://sidequest/' });
  assert.equal(root.status, 200);
  assert.equal(await root.text(), '<main>Sidequest</main>');

  const officeAsset = await serve({ method: 'GET', url: 'app://sidequest/room.glb' });
  assert.equal(officeAsset.status, 200);
  assert.equal(officeAsset.headers.get('content-type'), 'model/gltf-binary');
  assert.equal(new Uint8Array(await officeAsset.arrayBuffer()).length, 4);
  assert.match(officeAsset.headers.get('content-security-policy'), /worker-src 'self' blob:/);
  assert.match(officeAsset.headers.get('content-security-policy'), /frame-src 'none'/);

  for (const url of [
    'app://sidequest/a%2f..%2foutside.txt',
    'app://sidequest/%5c..%5coutside.txt',
    'app://other/index.html',
    'file:///etc/passwd',
  ]) {
    assert.equal((await serve({ method: 'GET', url })).status, 404, url);
  }
  assert.equal((await serve({ method: 'GET', url: 'app://sidequest/escape.txt' })).status, 404);
  assert.equal((await serve({ method: 'POST', url: 'app://sidequest/' })).status, 405);
  assert.equal(existsSync(path.join(dist, 'outside.txt')), false);
});
