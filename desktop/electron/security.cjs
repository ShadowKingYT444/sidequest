'use strict';

const FILE_ID_PATTERN = /^f_[a-f0-9]{32}$/;

function normalizeDevServerUrl(value) {
  if (!value) return null;
  let parsed;
  try {
    parsed = new URL(value);
  } catch {
    throw new Error('The development server URL is invalid.');
  }
  const loopback = parsed.hostname === '127.0.0.1' || parsed.hostname === 'localhost' || parsed.hostname === '[::1]';
  if (parsed.protocol !== 'http:' || !loopback || parsed.username || parsed.password || parsed.search || parsed.hash) {
    throw new Error('The development server must use an unauthenticated loopback HTTP URL.');
  }
  return parsed;
}

function isTrustedRendererUrl(value, devOrigin = null) {
  let parsed;
  try {
    parsed = new URL(value);
  } catch {
    return false;
  }
  if (parsed.protocol === 'app:' && parsed.hostname === 'sidequest' && !parsed.username && !parsed.password) return true;
  return Boolean(devOrigin && parsed.origin === devOrigin);
}

function isTrustedIpcSender(event, mainWindow, devOrigin = null) {
  if (!mainWindow || !mainWindow.webContents || event.sender !== mainWindow.webContents) return false;
  if (!event.senderFrame || event.senderFrame !== mainWindow.webContents.mainFrame) return false;
  return isTrustedRendererUrl(event.senderFrame.url, devOrigin);
}

function isValidFileId(value) {
  return typeof value === 'string' && FILE_ID_PATTERN.test(value);
}

function secureWebPreferences(preloadPath) {
  return {
    preload: preloadPath,
    sandbox: true,
    contextIsolation: true,
    nodeIntegration: false,
    webSecurity: true,
    allowRunningInsecureContent: false,
    webviewTag: false,
  };
}

module.exports = {
  isTrustedIpcSender,
  isTrustedRendererUrl,
  isValidFileId,
  normalizeDevServerUrl,
  secureWebPreferences,
};
