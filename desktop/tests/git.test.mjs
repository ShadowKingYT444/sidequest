import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync, symlinkSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import test from 'node:test';

const require = createRequire(import.meta.url);
const { createGitReader } = require('../electron/git-reader.cjs');

function git(root, ...args) {
  return execFileSync('git', args, { cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}

function write(root, name, contents) {
  const fullPath = path.join(root, name);
  mkdirSync(path.dirname(fullPath), { recursive: true });
  writeFileSync(fullPath, contents);
}

function fixture(t) {
  const root = mkdtempSync(path.join(os.tmpdir(), 'sidequest-git-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  git(root, 'init', '-q', '-b', 'main');
  git(root, 'config', 'user.name', 'Sidequest Test');
  git(root, 'config', 'user.email', 'sidequest@example.invalid');

  write(root, 'edit.txt', 'before\nsecond line\n');
  write(root, 'remove.md', 'remove me\n');
  write(root, 'rename-old.txt', 'renamed text\n');
  write(root, 'keep.txt', 'unchanged\n');
  write(root, 'notes.txt', 'access_token=private-old-secret\n');
  write(root, 'notes.json', '{"private_key": "private-key-material-old"}\n');
  write(root, 'serviceAccountKey.json', '{"private_key": "service-account-private-key"}\n');
  write(root, '.env.local', 'API_TOKEN=should-not-appear\n');
  write(root, 'config/app.json', '{"password":"should-not-appear"}\n');
  write(root, 'logs/app.log', 'secret output\n');
  write(root, 'keys/id_rsa', 'private key\n');
  write(root, 'private-key.pem', 'private key\n');
  write(root, 'vault/credentials.json', '{"password":"hidden"}\n');
  write(root, 'hidden\nname.txt', 'unsafe displayed path\n');
  symlinkSync('keep.txt', path.join(root, 'link-to-file'));
  git(root, 'add', '-A');
  git(root, 'commit', '-qm', 'base');
  const base = git(root, 'rev-parse', 'HEAD');

  write(root, 'edit.txt', 'after\nsecond line changed\nthird line\n');
  rmSync(path.join(root, 'remove.md'));
  git(root, 'mv', 'rename-old.txt', 'rename-new.txt');
  write(root, 'added.ts', 'export const value: number = 42;\n');
  write(root, 'picture.bin', Buffer.from([0, 1, 2, 3, 4]));
  write(root, '-option-name.txt', 'flag-like path\n');
  write(root, 'notes.txt', 'access_token=private-new-secret\n');
  write(root, 'notes.json', '{"private_key": "private-key-material-new"}\n');
  write(root, 'serviceAccountKey.json', '{"private_key": "changed-service-account-private-key"}\n');
  write(root, '.env.local', 'API_TOKEN=changed-secret\n');
  write(root, 'config/app.json', '{"password":"changed-secret"}\n');
  write(root, 'logs/app.log', 'changed log secret\n');
  write(root, 'keys/id_rsa', 'changed private key\n');
  write(root, 'private-key.pem', 'changed private key\n');
  write(root, 'vault/credentials.json', '{"password":"changed-hidden"}\n');
  write(root, 'hidden\nname.txt', 'changed unsafe path\n');
  git(root, 'add', '-A');
  git(root, 'commit', '-qm', 'candidate');
  const candidate = git(root, 'rev-parse', 'HEAD');
  return { root, base, candidate };
}

test('snapshot exposes bounded changed-file metadata and filters credentials, config, logs, symlinks, and unsafe names', async (t) => {
  const { root, base, candidate } = fixture(t);
  const reader = createGitReader(root, base);
  const snapshot = await reader.snapshot();

  assert.equal(snapshot.v, 1);
  assert.equal(snapshot.mode, 'local-git');
  assert.equal(snapshot.project.name, path.basename(root));
  assert.equal(snapshot.project.branch, 'main');
  assert.equal(snapshot.baseRevision, base);
  assert.equal(snapshot.candidateRevision, candidate);
  assert.deepEqual(snapshot.agent, {
    state: 'unavailable',
    message: 'Agent services are not connected in this desktop build.',
  });

  const byPath = new Map(snapshot.files.map((item) => [item.path, item]));
  assert.deepEqual([...byPath.keys()].sort(), ['-option-name.txt', 'added.ts', 'edit.txt', 'notes.json', 'notes.txt', 'picture.bin', 'remove.md', 'rename-new.txt'].sort());
  assert.equal(byPath.get('edit.txt').status, 'modified');
  assert.equal(byPath.get('added.ts').status, 'added');
  assert.equal(byPath.get('remove.md').status, 'deleted');
  assert.equal(byPath.get('rename-new.txt').status, 'renamed');
  assert.equal(byPath.get('picture.bin').binary, true);
  assert.equal(byPath.get('edit.txt').additions, 3);
  assert.equal(byPath.get('edit.txt').deletions, 2);
  assert.match(byPath.get('edit.txt').id, /^f_[a-f0-9]{32}$/);
  assert.doesNotMatch(byPath.get('edit.txt').id, /edit|txt/);

  const serialized = JSON.stringify(snapshot);
  for (const hidden of ['API_TOKEN', 'changed-secret', 'private key', 'private-old-secret', 'private-new-secret', 'private-key-material-old', 'private-key-material-new', 'serviceAccountKey.json', 'should-not-appear', 'hidden\nname.txt', 'app.log']) {
    assert.equal(serialized.includes(hidden), false, `snapshot should omit ${hidden}`);
  }
});

test('diff reads only pinned commits, handles additions/deletions/renames/binary, and is read-only', async (t) => {
  const { root, base, candidate } = fixture(t);
  const reader = createGitReader(root, base);
  const first = await reader.snapshot();
  const entries = new Map(first.files.map((item) => [item.path, item]));

  const edited = await reader.diff(entries.get('edit.txt').id);
  assert.deepEqual(edited, {
    id: entries.get('edit.txt').id,
    path: 'edit.txt',
    original: 'before\nsecond line\n',
    modified: 'after\nsecond line changed\nthird line\n',
    language: 'plaintext',
    binary: false,
    baseRevision: base,
    candidateRevision: candidate,
    readOnly: true,
  });
  assert.equal((await reader.diff(entries.get('added.ts').id)).original, '');
  assert.equal((await reader.diff(entries.get('added.ts').id)).modified, 'export const value: number = 42;\n');
  assert.equal((await reader.diff(entries.get('remove.md').id)).original, 'remove me\n');
  assert.equal((await reader.diff(entries.get('remove.md').id)).modified, '');
  assert.equal((await reader.diff(entries.get('rename-new.txt').id)).original, 'renamed text\n');
  assert.equal((await reader.diff(entries.get('rename-new.txt').id)).modified, 'renamed text\n');

  const binary = await reader.diff(entries.get('picture.bin').id);
  assert.equal(binary.binary, true);
  assert.equal(binary.original, '');
  assert.equal(binary.modified, '');
  const credentialLike = await reader.diff(entries.get('notes.txt').id);
  assert.equal(credentialLike.binary, false);
  assert.equal(credentialLike.original, '');
  assert.equal(credentialLike.modified, '');
  assert.equal(credentialLike.unavailableReason, 'Potential sensitive content was withheld by the local Git reader.');
  const privateKeyJson = await reader.diff(entries.get('notes.json').id);
  assert.equal(privateKeyJson.binary, false);
  assert.equal(privateKeyJson.original, '');
  assert.equal(privateKeyJson.modified, '');
  assert.equal(privateKeyJson.unavailableReason, 'Potential sensitive content was withheld by the local Git reader.');

  // The service pins HEAD during initialization and never reads the working tree.
  write(root, 'edit.txt', 'unstaged local secret\n');
  assert.equal((await reader.diff(entries.get('edit.txt').id)).modified, 'after\nsecond line changed\nthird line\n');
  assert.equal(git(root, 'rev-parse', 'HEAD'), candidate);
  assert.equal(readFileSync(path.join(root, 'edit.txt'), 'utf8'), 'unstaged local secret\n');
});

test('rejects malformed identifiers and identifiers outside the captured manifest', async (t) => {
  const { root, base } = fixture(t);
  const reader = createGitReader(root, base);
  await reader.snapshot();
  await assert.rejects(reader.diff('../edit.txt'), { code: 'INVALID_INPUT' });
  await assert.rejects(reader.diff('f_00000000000000000000000000000000'), { code: 'NOT_FOUND' });
  await assert.rejects(reader.diff('f_' + 'a'.repeat(200)), { code: 'INVALID_INPUT' });
});

test('pins a caller-selected base and rejects a non-commit or non-repository root', async (t) => {
  const { root, candidate } = fixture(t);
  const reader = createGitReader(root, candidate);
  assert.deepEqual((await reader.snapshot()).files, []);
  const outside = mkdtempSync(path.join(os.tmpdir(), 'sidequest-not-git-'));
  t.after(() => rmSync(outside, { recursive: true, force: true }));
  await assert.rejects(createGitReader(outside, 'HEAD').snapshot(), { code: 'GIT_FAILED' });
});

test('ignores inherited Git repository and config redirects', async (t) => {
  const { root, base, candidate } = fixture(t);
  const decoy = mkdtempSync(path.join(os.tmpdir(), 'sidequest-git-decoy-'));
  t.after(() => rmSync(decoy, { recursive: true, force: true }));
  git(decoy, 'init', '-q', '-b', 'decoy');
  git(decoy, 'config', 'user.name', 'Decoy');
  git(decoy, 'config', 'user.email', 'decoy@example.invalid');
  write(decoy, 'secret.txt', 'decoy repository\n');
  git(decoy, 'add', '-A');
  git(decoy, 'commit', '-qm', 'decoy');

  const names = ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_CONFIG_COUNT', 'GIT_CONFIG_KEY_0', 'GIT_CONFIG_VALUE_0'];
  const previous = Object.fromEntries(names.map((name) => [name, process.env[name]]));
  Object.assign(process.env, {
    GIT_DIR: path.join(decoy, '.git'),
    GIT_WORK_TREE: decoy,
    GIT_COMMON_DIR: path.join(decoy, '.git'),
    GIT_CONFIG_COUNT: '1',
    GIT_CONFIG_KEY_0: 'core.worktree',
    GIT_CONFIG_VALUE_0: decoy,
  });
  try {
    const snapshot = await createGitReader(root, base).snapshot();
    assert.equal(snapshot.candidateRevision, candidate);
    assert.equal(snapshot.files.some((entry) => entry.path === 'secret.txt'), false);
  } finally {
    for (const name of names) {
      if (previous[name] === undefined) delete process.env[name];
      else process.env[name] = previous[name];
    }
  }
});

test('does not execute repository-configured external diff commands', async (t) => {
  const root = mkdtempSync(path.join(os.tmpdir(), 'sidequest-diff-driver-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const marker = path.join(root, 'external-diff-ran');
  git(root, 'init', '-q', '-b', 'main');
  git(root, 'config', 'user.name', 'Sidequest Test');
  git(root, 'config', 'user.email', 'sidequest@example.invalid');
  write(root, '.gitattributes', 'unsafe.txt diff=unsafe\n');
  write(root, 'unsafe.txt', 'old\n');
  git(root, 'add', '-A');
  git(root, 'commit', '-qm', 'base');
  const base = git(root, 'rev-parse', 'HEAD');
  write(root, 'unsafe.txt', 'new\n');
  git(root, 'add', '-A');
  git(root, 'commit', '-qm', 'candidate');
  git(root, 'config', 'diff.unsafe.command', `touch '${marker}'`);

  const reader = createGitReader(root, base);
  const snapshot = await reader.snapshot();
  await reader.diff(snapshot.files[0].id);
  assert.equal(existsSync(marker), false);
});
