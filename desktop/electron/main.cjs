'use strict';

const { app, BrowserWindow, ipcMain, protocol, session } = require('electron');
const path = require('node:path');
const { createGitReader } = require('./git-reader.cjs');
const { createRuntimeClient, dispatchRuntime } = require('./runtime-client.cjs');
const {discoverProviders}=require('./provider-discovery.cjs');
const { createStaticAssetHandler } = require('./static-server.cjs');
const {
  isTrustedIpcSender,
  isTrustedRendererUrl,
  isValidFileId,
  normalizeDevServerUrl,
  secureWebPreferences,
} = require('./security.cjs');

protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { standard: true, secure: true, supportFetchAPI: true, corsEnabled: false } },
]);

const APP_ROOT = path.resolve(__dirname, '..');
const DIST_ROOT = path.join(APP_ROOT, 'dist');
const serveAppRequest = createStaticAssetHandler(DIST_ROOT);
const DEV_SERVER = process.env.SIDEQUEST_DEV_SERVER_URL
  ? normalizeDevServerUrl(process.env.SIDEQUEST_DEV_SERVER_URL)
  : null;
const DEV_ORIGIN = DEV_SERVER?.origin || null;
let mainWindow = null;
let gitReader = null;
let runtimeClient = null;
const hardenedSessions = new WeakSet();

function hardenWindow(window) {
  const contents = window.webContents;
  const sessionForWindow = contents.session || session.defaultSession;
  if (!hardenedSessions.has(sessionForWindow)) {
    sessionForWindow.setPermissionRequestHandler((_webContents, _permission, callback) => callback(false));
    sessionForWindow.setPermissionCheckHandler(() => false);
    if (typeof sessionForWindow.setDisplayMediaRequestHandler === 'function') {
      sessionForWindow.setDisplayMediaRequestHandler((_request, callback) => callback({}));
    }
    sessionForWindow.on('will-download', (event) => event.preventDefault());
    hardenedSessions.add(sessionForWindow);
  }
  contents.setWindowOpenHandler(() => ({ action: 'deny' }));
  contents.on('will-navigate', (details) => {
    if (!details.isMainFrame || !isTrustedRendererTarget(details.url)) details.preventDefault();
  });
  contents.on('will-redirect', (details) => {
    if (!details.isMainFrame || !isTrustedRendererTarget(details.url)) details.preventDefault();
  });
  contents.on('will-attach-webview', (event) => event.preventDefault());
  contents.on('will-frame-navigate', (details) => {
    if (!details.isMainFrame || !isTrustedRendererTarget(details.url)) details.preventDefault();
  });
  contents.on('devtools-opened', () => {
    if (app.isPackaged) contents.closeDevTools();
  });
}

function isTrustedRendererTarget(target) {
  return isTrustedRendererUrl(target, DEV_ORIGIN);
}

function assertTrustedSender(event) {
  if (!isTrustedIpcSender(event, mainWindow, DEV_ORIGIN)) {
    const error = new Error('This request is not allowed.');
    error.code = 'UNAUTHORIZED';
    throw error;
  }
}

function registerIpc() {
  ipcMain.removeHandler('sidequest:providers');
  ipcMain.handle('sidequest:providers',async(event,...args)=>{assertTrustedSender(event);if(args.length)throw new Error('Invalid provider discovery request.');return discoverProviders();});
  ipcMain.removeHandler('sidequest:snapshot');
  ipcMain.removeHandler('sidequest:diff');
  ipcMain.removeHandler('sidequest:runtime');
  ipcMain.handle('sidequest:runtime', async (event, method, args, ...extra) => {
    assertTrustedSender(event);
    if (extra.length || !runtimeClient) throw new Error('Local runtime is not configured.');
    return dispatchRuntime(runtimeClient, method, args);
  });
  ipcMain.handle('sidequest:snapshot', async (event, ...args) => {
    assertTrustedSender(event);
    if (args.length !== 0) {
      const error = new Error('This request is not allowed.');
      error.code = 'INVALID_INPUT';
      throw error;
    }
    if (!gitReader) {
      const error = new Error('A local repository is not configured.');
      error.code = 'NOT_CONFIGURED';
      throw error;
    }
    return gitReader.snapshot();
  });
  ipcMain.handle('sidequest:diff', async (event, fileId, ...args) => {
    assertTrustedSender(event);
    if (!isValidFileId(fileId) || args.length !== 0) {
      const error = new Error('The file identifier is invalid.');
      error.code = 'INVALID_INPUT';
      throw error;
    }
    if (!gitReader) {
      const error = new Error('A local repository is not configured.');
      error.code = 'NOT_CONFIGURED';
      throw error;
    }
    return gitReader.diff(fileId);
  });
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 960,
    minWidth: 960,
    minHeight: 640,
    show: false,
    backgroundColor: '#111318',
    webPreferences: secureWebPreferences(path.join(__dirname, 'preload.cjs')),
  });
  hardenWindow(mainWindow);
  mainWindow.once('ready-to-show', () => mainWindow && mainWindow.show());
  mainWindow.on('closed', () => { mainWindow = null; });
  if (!app.isPackaged && DEV_SERVER) {
    await mainWindow.loadURL(DEV_SERVER.href);
  } else {
    await mainWindow.loadURL('app://sidequest/index.html');
  }
}

async function start() {
  const repo = process.env.SIDEQUEST_REPO;
  if (repo) gitReader = createGitReader(repo, process.env.SIDEQUEST_BASE || 'HEAD~1');
  runtimeClient = createRuntimeClient({url:process.env.SIDEQUEST_RUNTIME_URL,token:process.env.SIDEQUEST_RUNTIME_TOKEN,tokenFile:process.env.SIDEQUEST_API_TOKEN_FILE,repo,baseRef:process.env.SIDEQUEST_PROJECT_BASE || 'HEAD'});
  await protocol.handle('app', serveAppRequest);
  registerIpc();
  await createWindow();
}

app.whenReady().then(start).catch(() => {
  // Keep startup failures generic; Git errors can include paths and local repository details.
  app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow().catch(() => app.quit());
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
