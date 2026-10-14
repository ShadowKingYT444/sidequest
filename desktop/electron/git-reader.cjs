'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');

const LIMITS = Object.freeze({
  commandMs: 5_000,
  treeBytes: 32 * 1024 * 1024,
  diffBytes: 8 * 1024 * 1024,
  blobBytes: 512 * 1024,
  files: 1_000,
  revisionChars: 256,
});
const MAX_GIT_PROCESSES = 4;
const MAX_QUEUED_GIT = 32;
let activeGitProcesses = 0;
const queuedGitReads = [];

function readerError(code, message) {
  const error = new Error(message);
  error.code = code;
  return error;
}

function acquireGitSlot() {
  if (activeGitProcesses < MAX_GIT_PROCESSES) {
    activeGitProcesses += 1;
    return Promise.resolve();
  }
  if (queuedGitReads.length >= MAX_QUEUED_GIT) {
    return Promise.reject(readerError('RATE_LIMIT', 'Too many Git reads are in progress.'));
  }
  return new Promise((resolve) => queuedGitReads.push(resolve));
}

function releaseGitSlot() {
  const next = queuedGitReads.shift();
  if (next) next();
  else activeGitProcesses -= 1;
}

function runGit(root, args, maxOutputBytes = 1024 * 1024) {
  return acquireGitSlot().then(() => new Promise((resolve, reject) => {
    let child;
    const cleanEnvironment = Object.fromEntries(
      Object.entries(process.env).filter(([name]) => !name.startsWith('GIT_')),
    );
    const noHooksPath = process.platform === 'win32' ? 'NUL' : '/dev/null';
    try {
      child = spawn('git', [
        '-c', `core.hooksPath=${noHooksPath}`,
        '-c', 'core.fsmonitor=false',
        '-c', 'diff.external=',
        '-c', 'core.pager=cat',
        ...args,
      ], {
        cwd: root,
        shell: false,
        windowsHide: true,
        stdio: ['ignore', 'pipe', 'pipe'],
        env: {
          ...cleanEnvironment,
          GIT_CONFIG_NOSYSTEM: '1',
          GIT_CONFIG_GLOBAL: process.platform === 'win32' ? 'NUL' : '/dev/null',
          GIT_OPTIONAL_LOCKS: '0',
          GIT_TERMINAL_PROMPT: '0',
          GIT_NO_REPLACE_OBJECTS: '1',
        },
      });
    } catch {
      releaseGitSlot();
      reject(readerError('GIT_UNAVAILABLE', 'Git could not be started.'));
      return;
    }

    const stdout = [];
    let stdoutBytes = 0;
    let settled = false;
    let timedOut = false;
    let tooLarge = false;
    let timer;
    const finish = (fn, value) => {
      if (settled) return;
      settled = true;
      if (timer) clearTimeout(timer);
      releaseGitSlot();
      fn(value);
    };
    timer = setTimeout(() => {
      timedOut = true;
      child.kill('SIGKILL');
    }, LIMITS.commandMs);
    timer.unref?.();

    child.stdout.on('data', (chunk) => {
      stdoutBytes += chunk.length;
      if (stdoutBytes > maxOutputBytes) {
        tooLarge = true;
        child.kill('SIGKILL');
        return;
      }
      stdout.push(chunk);
    });
    child.stderr.on('data', () => {});
    child.on('error', () => {
      finish(reject, readerError('GIT_UNAVAILABLE', 'Git could not be started.'));
    });
    child.on('close', (code) => {
      if (tooLarge) {
        finish(reject, readerError('OUTPUT_LIMIT', 'Git output exceeded the configured limit.'));
      } else if (timedOut) {
        finish(reject, readerError('GIT_TIMEOUT', 'Git did not finish within the time limit.'));
      } else if (code !== 0) {
        // Git errors may contain local paths or configured remote details. Keep them private.
        finish(reject, readerError('GIT_FAILED', 'The requested Git data is unavailable.'));
      } else {
        finish(resolve, Buffer.concat(stdout, stdoutBytes));
      }
    });
  }));
}

function cleanText(value, maxLength = 128) {
  return value.replace(/[\u0000-\u001f\u007f-\u009f]/g, '').slice(0, maxLength);
}

function validRevision(value) {
  return typeof value === 'string' && value.length > 0 && value.length <= LIMITS.revisionChars && !/[\u0000-\u001f\u007f]/.test(value);
}

function safeRepoPath(value) {
  if (!value || value.length > 1024 || value.startsWith('/') || value.includes('\\')) return false;
  if (/[\u0000-\u001f\u007f-\u009f]/.test(value)) return false;
  const segments = value.split('/');
  if (segments.some((part) => !part || part === '.' || part === '..')) return false;
  return path.posix.normalize(value) === value;
}

function isSensitivePath(value) {
  const parts = value.toLowerCase().split('/');
  const blockedSegments = new Set([
    '.aws', '.azure', '.config', '.docker', '.gcloud', '.kube', '.ssh',
    'config', 'configs', 'configuration', 'configurations', 'credential', 'credentials',
    'secret', 'secrets', 'log', 'logs', 'setting', 'settings',
  ]);
  if (parts.some((part) => blockedSegments.has(part))) return true;
  if (parts.some((part) => (
    /^\.env(?:[.-]|$)/.test(part)
    || /(?:credential|creds?|secret|private[-_.]?key|access[-_.]?key|api[-_.]?key|service[-_.]?account|token)/.test(part)
    || /(?:^|[._-])config(?:$|[._-])/.test(part)
    || /^logs?(?:[._-]|$)/.test(part)
  ))) return true;

  const basename = parts.at(-1) || '';
  if (/^\.env(?:[.-]|$)/.test(basename) || /(?:^|\.)env$/.test(basename)) return true;
  if (/^(?:\.netrc|\.npmrc|\.pypirc|\.git-credentials|\.htpasswd|\.pgpass)$/.test(basename)) return true;
  if (/^(?:id_rsa|id_dsa|id_ecdsa|id_ed25519|authorized_keys|known_hosts)(?:\.|$)/.test(basename)) return true;
  if (/(?:credential|secret|private[-_.]?key|access[-_.]?key|token)/.test(basename)) return true;
  if (/\.(?:key|pem|p12|pfx|p7b|p7c|jks|keystore|crt|cer|der|asc|gpg|age|kdbx|log|out|trace)(?:\.[^/]*)?$/.test(basename)) return true;
  if (/^(?:config|settings?)(?:\.|$)/.test(basename) || /\.(?:config|log)$/.test(basename)) return true;
  return false;
}

function decodePath(buffer) {
  const value = buffer.toString('utf8');
  if (!Buffer.from(value, 'utf8').equals(buffer) || !safeRepoPath(value)) return null;
  return value;
}

function parseTree(buffer) {
  const entries = new Map();
  let start = 0;
  while (start < buffer.length) {
    let end = buffer.indexOf(0, start);
    if (end < 0) end = buffer.length;
    if (end === start) {
      start = end + 1;
      continue;
    }
    const record = buffer.subarray(start, end);
    const tab = record.indexOf(9);
    if (tab > 0) {
      const header = record.subarray(0, tab).toString('ascii').split(' ');
      const repoPath = decodePath(record.subarray(tab + 1));
      if (header.length === 3 && repoPath && !isSensitivePath(repoPath)) {
        const [mode, type, oid] = header;
        if (/^[0-7]{6}$/.test(mode) && /^[0-9a-f]{40,64}$/.test(oid)) {
          entries.set(repoPath, { mode, type, oid });
        }
      }
    }
    start = end + 1;
  }
  return entries;
}

function splitNul(buffer) {
  const fields = [];
  let start = 0;
  while (start < buffer.length) {
    const end = buffer.indexOf(0, start);
    if (end < 0) {
      fields.push(buffer.subarray(start));
      break;
    }
    fields.push(buffer.subarray(start, end));
    start = end + 1;
  }
  return fields;
}

function parseNameStatus(buffer) {
  const fields = splitNul(buffer);
  const changes = [];
  for (let index = 0; index < fields.length;) {
    const statusField = fields[index++].toString('ascii');
    if (!statusField) continue;
    const status = statusField[0];
    if (status === 'R' || status === 'C') {
      const oldBytes = fields[index++];
      const newBytes = fields[index++];
      const oldPath = oldBytes && decodePath(oldBytes);
      const newPath = newBytes && decodePath(newBytes);
      if (oldPath !== undefined && newPath !== undefined) changes.push({ status, oldPath, path: newPath });
    } else {
      const bytes = fields[index++];
      const repoPath = bytes && decodePath(bytes);
      if (repoPath !== undefined) changes.push({ status, oldPath: null, path: repoPath });
    }
  }
  return changes;
}

function parseNumstat(buffer) {
  const fields = buffer.toString('utf8').split('\0');
  const result = new Map();
  for (let index = 0; index < fields.length;) {
    const record = fields[index++];
    if (!record) continue;
    const firstTab = record.indexOf('\t');
    const secondTab = record.indexOf('\t', firstTab + 1);
    if (firstTab < 0 || secondTab < 0) continue;
    const addedText = record.slice(0, firstTab);
    const deletedText = record.slice(firstTab + 1, secondTab);
    const inlinePath = record.slice(secondTab + 1);
    let repoPaths;
    if (inlinePath) {
      repoPaths = [inlinePath];
    } else {
      const oldPath = fields[index++];
      const newPath = fields[index++];
      repoPaths = [oldPath, newPath].filter(Boolean);
    }
    const binary = addedText === '-' || deletedText === '-';
    const additions = binary ? undefined : Number(addedText);
    const deletions = binary ? undefined : Number(deletedText);
    for (const repoPath of repoPaths) result.set(repoPath, { binary, additions, deletions });
  }
  return result;
}

function languageFor(filePath) {
  const extension = path.posix.extname(filePath).toLowerCase();
  const languages = {
    '.c': 'c', '.cc': 'cpp', '.cpp': 'cpp', '.cs': 'csharp', '.css': 'css',
    '.go': 'go', '.h': 'c', '.hpp': 'cpp', '.html': 'html', '.java': 'java',
    '.js': 'javascript', '.jsx': 'javascript', '.json': 'json', '.md': 'markdown',
    '.mjs': 'javascript', '.php': 'php', '.py': 'python', '.rb': 'ruby',
    '.rs': 'rust', '.sh': 'shell', '.sql': 'sql', '.swift': 'swift',
    '.ts': 'typescript', '.tsx': 'typescript', '.txt': 'plaintext', '.xml': 'xml',
    '.yaml': 'yaml', '.yml': 'yaml',
  };
  return languages[extension] || 'plaintext';
}

function containsCredentialMaterial(text) {
  return [
    /-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/i,
    /-----BEGIN PGP PRIVATE KEY BLOCK-----/i,
    /\b(?:AKIA|ASIA)[A-Z0-9]{16}\b/,
    /\bgh[pousr]_[A-Za-z0-9_]{20,}\b/,
    /\bgithub_pat_[A-Za-z0-9_]{20,}\b/,
    /\bxox[baprs]-[A-Za-z0-9-]{20,}\b/,
    /\b(?:authorization|proxy-authorization)\s*[:=]\s*bearer\s+[^\s"'<>]{8,}/i,
    /['"]?(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|private[_-]?key|password|secret|token)['"]?\s*[:=]\s*['"]?([A-Za-z0-9/+_.=-]{8,})/i,
  ].some((pattern) => pattern.test(text));
}

function parseCommit(buffer) {
  const value = buffer.toString('ascii').trim();
  if (!/^[0-9a-f]{40,64}$/.test(value)) throw readerError('GIT_FAILED', 'The requested Git revision is unavailable.');
  return value;
}

function createGitReader(repo, base = process.env.SIDEQUEST_BASE || 'HEAD~1') {
  if (typeof repo !== 'string' || repo.length === 0 || repo.length > 4096) {
    throw readerError('INVALID_INPUT', 'A repository root is required.');
  }
  if (!validRevision(base)) throw readerError('INVALID_INPUT', 'The base revision is invalid.');

  let root;
  try {
    root = fs.realpathSync(repo);
    if (!fs.statSync(root).isDirectory()) throw new Error('not a directory');
  } catch {
    throw readerError('INVALID_INPUT', 'The repository root is unavailable.');
  }

  const fileIds = new Map();
  let manifest;

  async function initialize() {
    const top = (await runGit(root, ['rev-parse', '--show-toplevel'], 4096)).toString('utf8').trim();
    let canonicalTop;
    try {
      canonicalTop = fs.realpathSync(top);
    } catch {
      throw readerError('INVALID_REPOSITORY', 'The configured directory is not a Git worktree.');
    }
    if (canonicalTop !== root) throw readerError('INVALID_REPOSITORY', 'Configure the Git worktree root directly.');

    const candidateRevision = parseCommit(await runGit(root, ['rev-parse', '--verify', '--end-of-options', 'HEAD^{commit}'], 256));
    const baseRevision = parseCommit(await runGit(root, ['rev-parse', '--verify', '--end-of-options', `${base}^{commit}`], 256));
    const branchOutput = await runGit(root, ['branch', '--show-current'], 1024);
    const branch = cleanText(branchOutput.toString('utf8').trim() || '(detached)');

    const [baseTreeBuffer, candidateTreeBuffer, nameStatusBuffer, numstatBuffer] = await Promise.all([
      runGit(root, ['ls-tree', '-rz', '--full-tree', baseRevision], LIMITS.treeBytes),
      runGit(root, ['ls-tree', '-rz', '--full-tree', candidateRevision], LIMITS.treeBytes),
      runGit(root, ['--no-pager', 'diff', '--no-ext-diff', '--no-textconv', '--find-renames=50%', '--name-status', '-z', baseRevision, candidateRevision, '--'], LIMITS.diffBytes),
      runGit(root, ['--no-pager', 'diff', '--no-ext-diff', '--no-textconv', '--find-renames=50%', '--numstat', '-z', baseRevision, candidateRevision, '--'], LIMITS.diffBytes),
    ]);
    const baseTree = parseTree(baseTreeBuffer);
    const candidateTree = parseTree(candidateTreeBuffer);
    const numstat = parseNumstat(numstatBuffer);
    const changes = parseNameStatus(nameStatusBuffer);
    if (changes.length > LIMITS.files) throw readerError('OUTPUT_LIMIT', 'The change set contains too many files.');

    const files = [];
    for (const change of changes) {
      if (!safeRepoPath(change.path) || (change.oldPath && !safeRepoPath(change.oldPath))) continue;
      if (isSensitivePath(change.path) || (change.oldPath && isSensitivePath(change.oldPath))) continue;
      const oldEntry = change.oldPath ? baseTree.get(change.oldPath) : baseTree.get(change.path);
      const nextEntry = candidateTree.get(change.path);
      if (oldEntry?.mode === '120000' || nextEntry?.mode === '120000') continue;
      if (oldEntry?.type === 'commit' || nextEntry?.type === 'commit') continue;
      if (oldEntry && oldEntry.type !== 'blob' || nextEntry && nextEntry.type !== 'blob') continue;
      const status = change.status === 'A' ? 'added'
        : change.status === 'D' ? 'deleted'
          : change.status === 'R' ? 'renamed'
            : change.status === 'C' ? 'added'
              : 'modified';
      const counts = numstat.get(change.path) || (change.oldPath ? numstat.get(change.oldPath) : undefined);
      const id = `f_${crypto.randomBytes(16).toString('hex')}`;
      const item = {
        id,
        path: change.path,
        status,
        ...(counts?.binary ? { binary: true } : {}),
        ...(typeof counts?.additions === 'number' ? { additions: counts.additions } : {}),
        ...(typeof counts?.deletions === 'number' ? { deletions: counts.deletions } : {}),
      };
      files.push(item);
      fileIds.set(id, {
        path: change.path,
        oldPath: change.oldPath,
        status,
        binary: Boolean(counts?.binary),
        oldEntry,
        nextEntry,
      });
    }

    manifest = {
      v: 1,
      mode: 'local-git',
      project: {
        name: path.basename(root),
        branch,
        rootLabel: path.basename(root),
      },
      baseRevision,
      candidateRevision,
      files,
      agent: {
        state: 'unavailable',
        message: 'Agent services are not connected in this desktop build.',
      },
    };
  }

  const ready = initialize();
  // Keep initialization failures for the API caller without creating an unhandled rejection at startup.
  ready.catch(() => {});

  async function snapshot() {
    await ready;
    return structuredClone(manifest);
  }

  async function blobText(entry) {
    if (!entry) return '';
    const sizeBuffer = await runGit(root, ['cat-file', '-s', entry.oid], 128);
    const size = Number(sizeBuffer.toString('ascii').trim());
    if (!Number.isSafeInteger(size) || size < 0) throw readerError('GIT_FAILED', 'The requested Git blob is unavailable.');
    if (size > LIMITS.blobBytes) throw readerError('OUTPUT_LIMIT', 'The requested file exceeds the display limit.');
    const content = await runGit(root, ['cat-file', 'blob', entry.oid], LIMITS.blobBytes);
    if (content.includes(0)) return null;
    const text = content.toString('utf8');
    if (!Buffer.from(text, 'utf8').equals(content)) return null;
    return text;
  }

  async function diff(fileId) {
    await ready;
    if (typeof fileId !== 'string' || !/^f_[a-f0-9]{32}$/.test(fileId)) {
      throw readerError('INVALID_INPUT', 'The file identifier is invalid.');
    }
    const entry = fileIds.get(fileId);
    if (!entry) throw readerError('NOT_FOUND', 'The requested file is not in this change set.');
    let binary = entry.binary;
    let unavailableReason;
    let original = '';
    let modified = '';
    if (!binary) {
      const [oldText, nextText] = await Promise.all([blobText(entry.oldEntry), blobText(entry.nextEntry)]);
      if (oldText === null || nextText === null) {
        binary = true;
      } else if (containsCredentialMaterial(oldText) || containsCredentialMaterial(nextText)) {
        unavailableReason = 'Potential sensitive content was withheld by the local Git reader.';
      } else {
        if (Buffer.byteLength(oldText, 'utf8') + Buffer.byteLength(nextText, 'utf8') > 1024 * 1024) {
          throw readerError('OUTPUT_LIMIT', 'The requested diff exceeds the display limit.');
        }
        original = oldText;
        modified = nextText;
      }
    }
    return {
      id: fileId,
      path: entry.path,
      original,
      modified,
      language: languageFor(entry.path),
      binary,
      baseRevision: manifest.baseRevision,
      candidateRevision: manifest.candidateRevision,
      readOnly: true,
      ...(unavailableReason ? { unavailableReason } : {}),
    };
  }

  return Object.freeze({ snapshot, diff });
}

module.exports = { createGitReader, LIMITS, isSensitivePath, safeRepoPath };
