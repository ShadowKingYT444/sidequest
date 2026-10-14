'use strict';

const fs = require('node:fs/promises');
const { constants } = require('node:fs');
const path = require('node:path');

const PROVIDERS = Object.freeze([
  { id: 'codex', name: 'Codex', binaries: ['codex'], home: 'codex' },
  { id: 'claude', name: 'Claude', binaries: ['claude'], home: 'host' },
  { id: 'cursor', name: 'Cursor', binaries: ['cursor-agent'], home: 'host' },
  { id: 'grok', name: 'Grok', binaries: ['grok'], home: 'host' },
  { id: 'opencode', name: 'OpenCode', binaries: ['opencode'], home: 'host' },
  { id: 'antigravity', name: 'Antigravity', binaries: ['agy', 'antigravity'], home: 'host' },
]);

async function locateBinary(binaryNames, searchPath) {
  const directories = searchPath.split(path.delimiter)
    .filter((directory) => directory && path.isAbsolute(directory))
    .slice(0, 64);
  for (const binaryName of binaryNames) {
    for (const directory of directories) {
      const candidate = path.join(directory, binaryName);
      try {
        await fs.access(candidate, constants.X_OK);
        const metadata = await fs.stat(candidate);
        if (metadata.isFile()) return candidate;
      } catch {
        // An inaccessible candidate is treated as absent; no process is launched.
      }
    }
  }
  return null;
}

async function discoverProviders() {
  const searchPath = process.env.PATH || '';
  const hostHome = process.env.HOME || null;
  const codexHome = process.env.CODEX_HOME || (hostHome ? path.join(hostHome, '.codex') : null);
  const providers = await Promise.all(PROVIDERS.map(async (provider) => {
    const binaryPath = await locateBinary(provider.binaries, searchPath);
    return {
      id: provider.id,
      name: provider.name,
      installed: binaryPath !== null,
      binaryPath,
      version: null,
      homePath: provider.home === 'codex' ? codexHome : hostHome,
      runtime: 'local',
    };
  }));

  return { v: 1, observedAt: new Date().toISOString(), providers };
}

module.exports = { discoverProviders };
