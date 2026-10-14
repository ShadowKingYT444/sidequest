'use strict';

const fs = require('node:fs/promises');
const { constants } = require('node:fs');
const path = require('node:path');

// Fixed names only. Current Cursor installs `agent`; `cursor-agent` supports
// older installations. Antigravity's `antigravity` launcher is the IDE, not
// evidence that its documented `agy` coding CLI is installed.
// Sources: https://cursor.com/docs/cli/installation
// https://code.claude.com/docs/en/setup
// https://antigravity.google/docs/getting-started?tab=cli
// https://github.com/anomalyco/opencode/blob/dev/install
// Grok's fixed name matches T3 Code's pinned provider-grok settings at
// d765d03cb7f980794c409c38e6ea5e25d89fde33. No upstream probing code is reused.
const PROVIDERS = Object.freeze([
  { id: 'codex', name: 'Codex', binaries: ['codex'], installBins: [], home: 'codex' },
  { id: 'claude', name: 'Claude', binaries: ['claude'], installBins: ['.local/bin'], home: 'host' },
  { id: 'cursor', name: 'Cursor', binaries: ['cursor-agent', 'agent'], installBins: ['.local/bin', '.cursor/bin'], home: 'host' },
  { id: 'grok', name: 'Grok', binaries: ['grok'], installBins: [], home: 'host' },
  { id: 'opencode', name: 'OpenCode', binaries: ['opencode'], installBins: ['.opencode/bin'], home: 'host' },
  { id: 'antigravity', name: 'Antigravity', binaries: ['agy'], installBins: ['.local/bin'], home: 'host' },
]);

function absoluteLocator(value) {
  if (typeof value !== 'string' || value.length === 0 || value.length > 4096 ||
      /[\x00-\x1f\x7f]/.test(value) || !path.isAbsolute(value)) return null;
  return path.normalize(value);
}

function pathDirectories(searchPath) {
  // Ignore relative/empty entries so renderer working directories never become
  // discovery roots. This bounds all work even with a malformed inherited PATH.
  const entries = typeof searchPath === 'string' ? searchPath.slice(0, 65536).split(path.delimiter) : [];
  if (typeof searchPath === 'string' && searchPath.length > 65536) entries.pop();
  const directories = new Map();
  for (const entry of entries) {
    const directory = absoluteLocator(entry);
    if (!directory) continue;
    const key = process.platform === 'win32' ? directory.toLowerCase() : directory;
    if (!directories.has(key)) directories.set(key, { directory, source: 'path' });
    if (directories.size === 64) break;
  }
  return [...directories.values()];
}

function searchDirectories(provider, inheritedPath, hostHome, localAppData) {
  const directories = [...inheritedPath];
  const knownBins = process.platform === 'win32'
    ? provider.id === 'antigravity' && localAppData ? [path.join(localAppData, 'agy', 'bin')] : []
    : hostHome ? provider.installBins.map((bin) => path.join(hostHome, bin)) : [];
  for (const directory of knownBins) {
    if (!directories.some((entry) => entry.directory === directory)) {
      directories.push({ directory, source: 'known-install' });
    }
  }
  return directories;
}

async function locateBinary(provider, directories) {
  // Fixed extensions, never inherited PATHEXT or a caller-supplied command.
  const extensions = process.platform === 'win32' ? ['', '.exe', '.cmd', '.bat'] : [''];
  for (const { directory, source } of directories) {
    for (const binaryName of provider.binaries) {
      for (const extension of extensions) {
        const candidate = path.join(directory, binaryName + extension);
        try {
          await fs.access(candidate, constants.X_OK);
          const metadata = await fs.stat(candidate);
          if (metadata.isFile()) return { binaryPath: candidate, discoverySource: source };
        } catch {
          // An inaccessible candidate is treated as absent; no process is launched.
        }
      }
    }
  }
  return { binaryPath: null, discoverySource: null };
}

async function discoverProviders() {
  const inheritedPath = pathDirectories(process.env.PATH);
  const hostHome = absoluteLocator(process.env.HOME || process.env.USERPROFILE);
  const localAppData = absoluteLocator(process.env.LOCALAPPDATA) ||
    (process.platform === 'win32' && hostHome ? path.join(hostHome, 'AppData', 'Local') : null);
  const codexHome = process.env.CODEX_HOME
    ? absoluteLocator(process.env.CODEX_HOME)
    : hostHome ? path.join(hostHome, '.codex') : null;
  const providers = await Promise.all(PROVIDERS.map(async (provider) => {
    let { binaryPath, discoverySource } = await locateBinary(provider,
      searchDirectories(provider, inheritedPath, hostHome, localAppData));
    // Optional operator-controlled locator after automatic discovery fails.
    // This is metadata only; the renderer cannot supply a path or argv.
    if (!binaryPath) {
      const configured = absoluteLocator(process.env[`SIDEQUEST_${provider.id.toUpperCase()}_EXECUTABLE`]);
      if (configured) {
        try {
          await fs.access(configured, constants.X_OK);
          if ((await fs.stat(configured)).isFile()) {
            binaryPath = configured;
            discoverySource = 'host-setting';
          }
        } catch { /* An invalid manual locator does not grant a capability. */ }
      }
    }
    return {
      id: provider.id,
      name: provider.name,
      installed: binaryPath !== null,
      binaryPath,
      discoverySource,
      version: null,
      // Executable metadata does not establish identity, account state, quota
      // or provider connectivity. Status refresh performs no process/network IO.
      authentication: 'unknown',
      reachability: 'unknown',
      homePath: provider.home === 'codex' ? codexHome : hostHome,
      runtime: 'local',
    };
  }));

  return { v: 1, observedAt: new Date().toISOString(), providers };
}

module.exports = { discoverProviders };
