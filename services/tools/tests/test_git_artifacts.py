from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import uuid

TOOLS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_ROOT))

from artifact_capture import deliver_candidate, freeze_candidate, tree_digest
from config import Settings
from git_ops import AdapterError, prepare_clone, resolve_commit


def synthetic_secret_json(key: str, value: str) -> str:
    """Build scanner fixtures at runtime so test source contains no secret sample."""
    return json.dumps({key: value}) + "\n"


def synthetic_private_key_header() -> str:
    return "-----BEGIN " + "PRIVATE " + "KEY" + "-----"


def git(cwd: Path, *args: str, input_data: bytes | None = None, env: dict[str, str] | None = None) -> bytes:
    command_env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_COUNT": "0",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
    }
    if env:
        command_env.update(env)
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=command_env,
        check=True,
        shell=False,
    ).stdout


class GitFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="sidequest-b1-test-")
        self.root = Path(self.temp.name)
        self.repos = self.root / "repos"
        self.staging = self.root / "staging"
        self.artifacts = self.root / "artifacts"
        self.delivery = self.root / "delivery"
        self.approvals = self.root / "approvals"
        self.state = self.root / "delivery-state"
        for directory in (self.repos, self.staging, self.artifacts, self.delivery, self.approvals, self.state):
            directory.mkdir(parents=True, exist_ok=True)
        self.settings = Settings(
            allowed_repo_roots=(self.repos,),
            staging_roots=(self.staging,),
            artifact_roots=(self.artifacts,),
            delivery_roots=(self.delivery,),
            approval_root=self.approvals,
            delivery_state_root=self.state,
            max_files=1000,
            max_total_bytes=2 * 1024 * 1024,
            max_file_bytes=1024 * 1024,
            git_timeout_seconds=15,
            max_git_output_bytes=4 * 1024 * 1024,
        )
        self.source = self.repos / "source"
        self.source.mkdir()
        self._init_repo(self.source)
        self._write(self.source, "README.md", b"fixture repo\n")
        self._write(self.source, "src/edit.txt", b"before\n")
        self._write(self.source, "src/delete.txt", b"remove me\n")
        self._write(self.source, "docs/old-name.txt", b"move this exact file\n")
        self._write(self.source, "assets/icon.bin", b"\x00base\xff")
        self._commit(self.source, "base")
        self.base = git(self.source, "rev-parse", "HEAD").decode().strip()

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _init_repo(path: Path) -> None:
        subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "--quiet", str(path)], check=True)

    @staticmethod
    def _write(root: Path, relative: str, data: bytes) -> Path:
        target = root.joinpath(*relative.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return target

    @staticmethod
    def _commit(repo: Path, message: str) -> str:
        git(repo, "add", "-A")
        env = {
            "GIT_AUTHOR_NAME": "Fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        }
        return git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--quiet", "-m", message, env=env).decode().strip()

    def prepare(self, name: str = "worker") -> Path:
        workspace, revision = prepare_clone(str(self.source), self.base, str(self.staging / name), self.settings)
        self.assertEqual(revision, self.base)
        return workspace

    def freeze(self, workspace: Path, *, paths: list[str] | None = None, settings: Settings | None = None):
        write_paths = paths if paths is not None else ["src", "docs", "assets"]
        request = {
            "v": 1,
            "request_id": "freeze-fixture",
            "op": "artifacts.freeze",
            "job_id": "fixture-job",
            "workspace": str(workspace),
            "payload": {"base_revision": self.base, "write_paths": write_paths},
            "context": {
                "source_revision": self.base,
                "write_paths": write_paths,
                "project_id": "fixture-project",
                "output_root": str(self.artifacts),
            },
        }
        return freeze_candidate(request, settings or self.settings)

    def changed_workspace(self) -> Path:
        workspace = self.prepare()
        (workspace / "src/edit.txt").write_bytes(b"after\n")
        (workspace / "src/delete.txt").unlink()
        (workspace / "src/new.txt").write_bytes(b"new file\n")
        (workspace / "docs/old-name.txt").rename(workspace / "docs/new-name.txt")
        (workspace / "docs/new-name.txt").chmod(0o755)
        (workspace / "assets/icon.bin").write_bytes(b"\x00changed\xfe")
        return workspace


class GitInspectionAndFreezeTests(GitFixture):
    def test_freeze_rejects_hardlinked_git_config_without_touching_external_file(self) -> None:
        workspace = self.prepare("hardlinked-config")
        outside = self.root / "outside-config"
        outside.write_bytes(b"external sentinel must remain unchanged\n")
        config = workspace / ".git" / "config"
        config.unlink()
        os.link(outside, config)
        before = outside.read_bytes()

        with self.assertRaises(AdapterError) as caught:
            self.freeze(workspace)

        self.assertEqual(caught.exception.code, "POLICY_DENIED")
        self.assertEqual(outside.read_bytes(), before)
        self.assertEqual(config.read_bytes(), before)
        self.assertEqual(os.stat(config).st_nlink, 2)

    def test_freeze_rejects_hardlinks_anywhere_in_git_metadata(self) -> None:
        workspace = self.prepare("hardlinked-ref")
        outside = self.root / "outside-ref"
        outside.write_bytes(b"external ref sentinel\n")
        ref = workspace / ".git" / "refs" / "heads" / "sidequest-base"
        ref.unlink()
        os.link(outside, ref)
        before = outside.read_bytes()

        with self.assertRaises(AdapterError) as caught:
            self.freeze(workspace)

        self.assertEqual(caught.exception.code, "POLICY_DENIED")
        self.assertEqual(outside.read_bytes(), before)
        self.assertEqual(ref.read_bytes(), before)

    def test_prepare_is_independent_and_does_not_change_source(self) -> None:
        before_refs = git(self.source, "for-each-ref", "--format=%(refname) %(objectname)")
        before_bytes = {p.relative_to(self.source).as_posix(): p.read_bytes() for p in self.source.rglob("*") if p.is_file() and ".git" not in p.parts}
        workspace = self.prepare()
        after_refs = git(self.source, "for-each-ref", "--format=%(refname) %(objectname)")
        after_bytes = {p.relative_to(self.source).as_posix(): p.read_bytes() for p in self.source.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.assertEqual(before_refs, after_refs)
        self.assertEqual(before_bytes, after_bytes)
        self.assertEqual(git(self.source, "status", "--porcelain"), b"")
        self.assertEqual(git(workspace, "status", "--porcelain"), b"")
        self.assertFalse((workspace / ".git/objects/info/alternates").exists())
        self.assertNotIn("[remote", (workspace / ".git/config").read_text())
        source_objects = {p.relative_to(self.source / ".git/objects").as_posix(): p for p in (self.source / ".git/objects").rglob("*") if p.is_file()}
        clone_objects = {p.relative_to(workspace / ".git/objects").as_posix(): p for p in (workspace / ".git/objects").rglob("*") if p.is_file()}
        common = set(source_objects) & set(clone_objects)
        self.assertTrue(common)
        for relative in common:
            self.assertNotEqual(source_objects[relative].stat().st_ino, clone_objects[relative].stat().st_ino)
        (workspace / "src/edit.txt").write_bytes(b"worker change\n")
        GitFixture._commit(workspace, "worker-only")
        self.assertEqual(git(self.source, "rev-parse", "HEAD").decode().strip(), self.base)

    def test_prepare_rejects_dirty_source_and_symlink_tree(self) -> None:
        (self.source / "untracked.txt").write_text("untracked\n")
        with self.assertRaisesRegex(AdapterError, "clean at the requested revision"):
            self.prepare("dirty")
        (self.source / "untracked.txt").unlink()

        symlink_repo = self.repos / "symlink-source"
        shutil.copytree(self.source, symlink_repo, ignore=shutil.ignore_patterns(".git"))
        self._init_repo(symlink_repo)
        external = self.root / "outside.txt"
        external.write_text("outside\n")
        (symlink_repo / "src/link.txt").symlink_to(external)
        self._commit(symlink_repo, "symlink")
        revision = git(symlink_repo, "rev-parse", "HEAD").decode().strip()
        with self.assertRaisesRegex(AdapterError, "symlink|unsupported file mode"):
            prepare_clone(str(symlink_repo), revision, str(self.staging / "symlink-clone"), self.settings)

        alternates = self.source / ".git/objects/info/alternates"
        alternates.parent.mkdir(parents=True, exist_ok=True)
        alternates.write_text(str(self.root / "outside-object-store") + "\n")
        with self.assertRaisesRegex(AdapterError, "alternate object stores"):
            self.prepare("alternate-source")

    def test_host_cli_inspect_returns_protocol_envelope_without_git_output(self) -> None:
        request = {
            "v": 1,
            "request_id": "inspect-cli-fixture",
            "op": "repo.inspect",
            "job_id": "fixture-job",
            "workspace": str(self.staging / "unused-workspace"),
            "payload": {"repo_path": str(self.source), "revision": self.base},
        }
        env = dict(os.environ)
        env.update({
            "SIDEQUEST_ALLOWED_REPO_ROOTS": str(self.repos),
            "SIDEQUEST_STAGING_ROOTS": str(self.staging),
            "SIDEQUEST_ARTIFACT_ROOTS": str(self.artifacts),
            "SIDEQUEST_DELIVERY_ROOTS": str(self.delivery),
            "SIDEQUEST_DELIVERY_APPROVAL_ROOT": str(self.approvals),
            "SIDEQUEST_DELIVERY_STATE_ROOT": str(self.state),
            "GIT_DIR": "/tmp/ignored-git-dir",
            "GIT_WORK_TREE": "/tmp/ignored-git-worktree",
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.hooksPath",
            "GIT_CONFIG_VALUE_0": "/tmp/ignored-hooks",
        })
        result = subprocess.run(
            [sys.executable, "-m", "services.tools.main"],
            cwd=TOOLS_ROOT.parents[1],
            input=json.dumps(request, separators=(",", ":")).encode() + b"\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count(b"\n"), 1)
        response = json.loads(result.stdout)
        self.assertTrue(response["ok"], result.stderr.decode())
        self.assertEqual(response["request_id"], request["request_id"])
        self.assertTrue(response["data"]["clean"])
        self.assertEqual(response["data"]["revision"], self.base)
        self.assertIn("src/edit.txt", response["data"]["files"])

    def test_environment_and_repository_filters_hooks_and_textconv_are_ignored(self) -> None:
        filtered = self.repos / "filter-source"
        filtered.mkdir()
        self._init_repo(filtered)
        self._write(filtered, ".gitattributes", b"*.txt filter=fixture diff=fixture\n")
        self._write(filtered, "file.txt", b"before\n")
        self._commit(filtered, "filtered base")
        sentinel = self.root / "external-command-ran"
        hostile = f"touch {sentinel}"
        git(filtered, "config", "filter.fixture.clean", hostile)
        git(filtered, "config", "filter.fixture.smudge", hostile)
        git(filtered, "config", "diff.fixture.textconv", hostile)
        git(filtered, "config", "diff.external", hostile)
        hooks = self.root / "hostile-hooks"
        hooks.mkdir()
        hook = hooks / "pre-commit"
        hook.write_text(f"#!/bin/sh\ntouch {sentinel}\n")
        hook.chmod(0o755)
        git(filtered, "config", "core.hooksPath", str(hooks))
        revision = git(filtered, "rev-parse", "HEAD").decode().strip()
        workspace, _ = prepare_clone(str(filtered), revision, str(self.staging / "filter-workspace"), self.settings)
        (workspace / "file.txt").write_text("after\n")
        request = {
            "v": 1,
            "request_id": "filter-freeze",
            "op": "artifacts.freeze",
            "job_id": "fixture-job",
            "workspace": str(workspace),
            "payload": {"base_revision": revision, "write_paths": ["file.txt"]},
            "context": {"source_revision": revision, "write_paths": ["file.txt"], "output_root": str(self.artifacts)},
        }
        freeze_candidate(request, self.settings)
        self.assertFalse(sentinel.exists())

    def test_git_environment_overrides_cannot_redirect_repository(self) -> None:
        prior = {key: os.environ.get(key) for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0")}
        try:
            os.environ.update({
                "GIT_DIR": "/tmp/not-the-fixture-repo",
                "GIT_WORK_TREE": "/tmp/not-the-fixture-tree",
                "GIT_INDEX_FILE": "/tmp/not-the-fixture-index",
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "core.hooksPath",
                "GIT_CONFIG_VALUE_0": "/tmp/not-the-fixture-hooks",
            })
            self.assertEqual(resolve_commit(self.source, self.base, self.settings), self.base)
        finally:
            for key, value in prior.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_freeze_captures_add_edit_delete_rename_binary_and_modes(self) -> None:
        workspace = self.changed_workspace()
        source_head_before = git(self.source, "rev-parse", "HEAD").decode().strip()
        data, artifacts = self.freeze(workspace)
        by_kind = {artifact["kind"]: artifact for artifact in artifacts}
        manifest_bytes = (self.artifacts / by_kind["file_manifest"]["relative_path"]).read_bytes()
        patch_bytes = (self.artifacts / by_kind["patch"]["relative_path"]).read_bytes()
        diff_bytes = (self.artifacts / by_kind["diff"]["relative_path"]).read_bytes()
        manifest = json.loads(manifest_bytes)
        rows = {item["path"]: item for item in manifest["files"]}
        self.assertEqual(manifest["v"], 1)
        self.assertEqual(manifest["candidate"], data["candidate"])
        self.assertEqual(rows["src/edit.txt"]["status"], "modified")
        self.assertEqual(rows["src/new.txt"]["status"], "added")
        self.assertEqual(rows["src/delete.txt"]["status"], "deleted")
        self.assertEqual(rows["docs/new-name.txt"]["status"], "renamed")
        self.assertEqual(rows["docs/new-name.txt"]["old_path"], "docs/old-name.txt")
        self.assertEqual(rows["docs/new-name.txt"]["mode"], "100755")
        self.assertTrue(rows["assets/icon.bin"]["binary"])
        self.assertIn("README.md", rows)
        self.assertEqual(rows["README.md"]["status"], "unchanged")
        self.assertIn(b"GIT binary patch", patch_bytes)
        self.assertTrue(diff_bytes.startswith(b"diff --git "))
        self.assertEqual(hashlib.sha256(patch_bytes).hexdigest(), data["candidate"]["patch_sha256"])
        self.assertEqual(hashlib.sha256(manifest_bytes).hexdigest(), by_kind["file_manifest"]["sha256"])
        self.assertEqual(tree_digest(manifest["files"]), data["candidate"]["tree_sha256"])
        self.assertEqual(resolve_commit(workspace, data["candidate"]["candidate_revision"], self.settings), data["candidate"]["candidate_revision"])
        snapshot = Path(data["snapshot_root"])
        self.assertFalse(snapshot.stat().st_mode & stat.S_IWUSR)
        self.assertFalse((snapshot / "src/edit.txt").stat().st_mode & stat.S_IWUSR)
        self.assertEqual(source_head_before, git(self.source, "rev-parse", "HEAD").decode().strip())
        self.assertEqual(git(self.source, "status", "--porcelain"), b"")

    def test_nul_machine_formats_preserve_newline_and_tab_filenames(self) -> None:
        workspace = self.prepare("odd-paths")
        weird = "src/line\nbreak\tname.txt"
        self._write(workspace, weird, b"safe text\n")
        data, artifacts = self.freeze(workspace, paths=["src"])
        manifest_artifact = next(item for item in artifacts if item["kind"] == "file_manifest")
        manifest = json.loads((self.artifacts / manifest_artifact["relative_path"]).read_bytes())
        row = next(item for item in manifest["files"] if item["path"] == weird)
        self.assertEqual(row["status"], "added")
        self.assertTrue(row["file_id"].startswith("f_"))
        snapshot = Path(data["snapshot_root"])
        self.assertEqual(snapshot.joinpath(*weird.split("/")).read_bytes(), b"safe text\n")

    def test_token_budget_docs_and_environment_lookup_code_are_not_credentials(self) -> None:
        workspace = self.prepare("token-budget-docs")
        (workspace / "docs/LOW_TOKEN_EXECUTION.md").write_text(
            "The worker has a 30,000 token budget and a bounded execution window.\n"
        )
        (workspace / "src/auth_config.py").write_text(
            "import os\n"
            "token = os.environ.get('API_TOKEN')\n"
            "secret = load_secret()\n"
        )
        data, artifacts = self.freeze(workspace, paths=["docs", "src"])
        self.assertEqual(data["candidate"]["base_revision"], self.base)
        self.assertEqual(len(artifacts), 3)

    def test_literal_credential_assignment_and_secret_named_data_file_remain_blocked(self) -> None:
        workspace = self.prepare("literal-secret-assignment")
        assignment_name = "API_" + "TOKEN"
        sample_value = "fixture" + "-secret-value-long-enough"
        (workspace / "src/config.py").write_text(assignment_name + ' = "' + sample_value + '"\n')
        with self.assertRaisesRegex(AdapterError, "Credential-like"):
            self.freeze(workspace)

    def test_unquoted_plaintext_config_credentials_are_blocked_but_references_pass(self) -> None:
        assignment_name = "API_" + "TOKEN"
        sample_value = "fixture_plaintext_" + "secret_" + "9a8b7c6d"
        workspace = self.prepare("unquoted-credential-config")
        (workspace / "src/settings.conf").write_text(assignment_name + "=" + sample_value + "\n")
        with self.assertRaisesRegex(AdapterError, "Credential-like"):
            self.freeze(workspace)

        for index, reference in enumerate(("${HOST_" + assignment_name + "}", "$HOST_" + assignment_name)):
            workspace = self.prepare(f"config-env-reference-{index}")
            (workspace / "src/settings.conf").write_text(assignment_name + "=" + reference + "\n")
            data, artifacts = self.freeze(workspace, paths=["src"])
            self.assertEqual(data["candidate"]["base_revision"], self.base)
            self.assertEqual(len(artifacts), 3)

        workspace = self.prepare("secret-token-file")
        (workspace / "src/token.json").write_text(synthetic_secret_json("token", "live" + "_example_value"))
        with self.assertRaisesRegex(AdapterError, "Credential-like"):
            self.freeze(workspace)

    def test_freeze_rejects_symlink_traversal_scope_oversize_and_credentials(self) -> None:
        workspace = self.prepare("symlink-workspace")
        external = self.root / "external.txt"
        external.write_text("do not follow\n")
        (workspace / "src/link.txt").symlink_to(external)
        with self.assertRaisesRegex(AdapterError, "Symlink"):
            self.freeze(workspace)

        workspace = self.prepare("scope-workspace")
        (workspace / "src/new.txt").write_text("out of scope\n")
        with self.assertRaisesRegex(AdapterError, "write scope"):
            self.freeze(workspace, paths=["docs"])

        workspace = self.prepare("traversal-workspace")
        with self.assertRaisesRegex(AdapterError, "Unsafe repository path|Traversal"):
            self.freeze(workspace, paths=["../escape"])

        workspace = self.prepare("oversize-workspace")
        (workspace / "src/edit.txt").write_bytes(b"x" * 200)
        small_limits = Settings(**{**self.settings.__dict__, "max_total_bytes": 100, "max_file_bytes": 1024})
        with self.assertRaisesRegex(AdapterError, "100 MiB|size limit"):
            self.freeze(workspace, settings=small_limits)

        workspace = self.prepare("credential-path")
        (workspace / ".env").write_text("TOKEN=example-secret\n")
        with self.assertRaisesRegex(AdapterError, "Credential-like"):
            self.freeze(workspace)

        workspace = self.prepare("artifact-root-link")
        external_output = self.root / "external-artifact-output"
        external_output.mkdir()
        linked_output = self.artifacts / "redirect"
        linked_output.symlink_to(external_output, target_is_directory=True)
        request = {
            "v": 1,
            "request_id": "bad-output-root",
            "op": "artifacts.freeze",
            "job_id": "fixture-job",
            "workspace": str(workspace),
            "payload": {"base_revision": self.base, "write_paths": ["src"]},
            "context": {"source_revision": self.base, "write_paths": ["src"], "output_root": str(linked_output)},
        }
        with self.assertRaisesRegex(AdapterError, "Symlink paths"):
            freeze_candidate(request, self.settings)

        workspace = self.prepare("credential-content")
        (workspace / "config/serviceAccountKey.json").parent.mkdir(parents=True)
        private_key_sample = synthetic_private_key_header() + "abc"
        (workspace / "config/serviceAccountKey.json").write_text(synthetic_secret_json("private_key", private_key_sample))
        with self.assertRaisesRegex(AdapterError, "Credential-like"):
            self.freeze(workspace)

        workspace = self.prepare("generic-token")
        (workspace / "src/token.json").write_text(synthetic_secret_json("token", "live" + "_example_value"))
        with self.assertRaisesRegex(AdapterError, "Credential-like"):
            self.freeze(workspace)


class LocalDeliveryTests(GitFixture):
    def _delivery_request(self):
        workspace = self.prepare("delivery-candidate-" + uuid.uuid4().hex)
        (workspace / "src/edit.txt").write_text("approved change\n")
        candidate_data, artifacts = self.freeze(workspace)
        artifact_by_kind = {item["kind"]: item for item in artifacts}
        patch_record = artifact_by_kind["patch"]
        manifest_record = artifact_by_kind["file_manifest"]
        destination = self.delivery / ("target-" + uuid.uuid4().hex)
        subprocess.run(["git", "clone", "--no-hardlinks", "--quiet", str(self.source), str(destination)], check=True)
        delivery_id = "fixture-delivery-001"
        approval_id = "approval-fixture-001"
        approval_record = {
            "v": 1,
            "id": approval_id,
            "state": "approved",
            "action": "local_deliver",
            "action_id": delivery_id,
            "delivery_id": delivery_id,
            "candidate_id": candidate_data["candidate"]["id"],
            "candidate_revision": candidate_data["candidate"]["candidate_revision"],
            "candidate_tree_sha256": candidate_data["candidate"]["tree_sha256"],
            "patch_sha256": candidate_data["candidate"]["patch_sha256"],
            "source_revision": self.base,
            "destination": str(destination),
            "manifest_artifact_id": manifest_record["id"],
        }
        approval_path = self.approvals / "approval.json"
        approval_bytes = json.dumps(approval_record, sort_keys=True, separators=(",", ":")).encode()
        approval_path.write_bytes(approval_bytes)
        approval_ref = {
            "id": approval_id,
            "sha256": hashlib.sha256(approval_bytes).hexdigest(),
            "staged_path": str(approval_path),
        }
        patch_path = self.artifacts / patch_record["relative_path"]
        manifest_path = self.artifacts / manifest_record["relative_path"]
        request = {
            "v": 1,
            "request_id": "deliver-fixture",
            "op": "repo.deliver",
            "job_id": "fixture-job",
            "workspace": str(workspace),
            "payload": {
                "patch_artifact_id": patch_record["id"],
                "artifact_sha256": patch_record["sha256"],
                "source_revision": self.base,
                "destination": str(destination),
                "approval": {
                    "id": approval_id,
                    "candidate_id": candidate_data["candidate"]["id"],
                    "candidate_revision": candidate_data["candidate"]["candidate_revision"],
                    "candidate_tree_sha256": candidate_data["candidate"]["tree_sha256"],
                    "source_revision": self.base,
                    "action": "local_deliver",
                    "destination": str(destination),
                },
            },
            "context": {
                "delivery_id": delivery_id,
                "action_id": delivery_id,
                "approval_record": approval_ref,
                "artifact_inputs": [
                    {"id": patch_record["id"], "sha256": patch_record["sha256"], "staged_path": str(patch_path)},
                    {"id": manifest_record["id"], "sha256": manifest_record["sha256"], "staged_path": str(manifest_path)},
                ],
                "write_paths": ["src"],
            },
        }
        return request, destination

    def test_host_approval_delivers_once_and_reconciles_repeat(self) -> None:
        request, destination = self._delivery_request()
        data, artifacts = deliver_candidate(request, self.settings)
        self.assertEqual(data, {"status": "delivered", "delivery_id": "fixture-delivery-001"})
        self.assertEqual(artifacts, [])
        self.assertEqual((destination / "src/edit.txt").read_text(), "approved change\n")
        self.assertEqual(git(destination, "rev-parse", "HEAD").decode().strip(), self.base)
        repeated, _ = deliver_candidate(request, self.settings)
        self.assertEqual(repeated, data)
        state_path = self.state / (hashlib.sha256(b"fixture-delivery-001").hexdigest() + ".json")
        state = json.loads(state_path.read_text())
        state["status"] = "started"
        state_path.write_text(json.dumps(state, sort_keys=True, separators=(",", ":")))
        with self.assertRaisesRegex(AdapterError, "uncertain outcome"):
            deliver_candidate(request, self.settings)

    def test_payload_approval_alone_and_stale_identity_are_rejected(self) -> None:
        request, _ = self._delivery_request()
        request["context"].pop("approval_record")
        with self.assertRaisesRegex(AdapterError, "host-staged approval"):
            deliver_candidate(request, self.settings)

        request, _ = self._delivery_request()
        request["context"]["approval_record"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(AdapterError, "digest"):
            deliver_candidate(request, self.settings)

        request, _ = self._delivery_request()
        request["context"]["action_id"] = "different-action"
        with self.assertRaisesRegex(AdapterError, "must match"):
            deliver_candidate(request, self.settings)

    def test_delivery_blocks_changed_destination_and_uncertain_retries(self) -> None:
        request, destination = self._delivery_request()
        (destination / "src/edit.txt").write_text("someone changed this\n")
        with self.assertRaisesRegex(AdapterError, "clean before delivery"):
            deliver_candidate(request, self.settings)

        request, destination = self._delivery_request()
        state_path = self.state / (hashlib.sha256(b"fixture-delivery-001").hexdigest() + ".json")
        state_path.write_text('{"fingerprint":"anything","status":"started"}')
        with self.assertRaisesRegex(AdapterError, "different action|uncertain"):
            deliver_candidate(request, self.settings)

    def test_delivery_scope_and_destination_identity_are_exact(self) -> None:
        request, destination = self._delivery_request()
        request["context"]["write_paths"] = ["docs"]
        with self.assertRaisesRegex(AdapterError, "write scope"):
            deliver_candidate(request, self.settings)

        request, _ = self._delivery_request()
        other_destination = self.delivery / "other-target"
        subprocess.run(["git", "clone", "--no-hardlinks", "--quiet", str(self.source), str(other_destination)], check=True)
        request["payload"]["destination"] = str(other_destination)
        with self.assertRaisesRegex(AdapterError, "does not match destination"):
            deliver_candidate(request, self.settings)


if __name__ == "__main__":
    unittest.main()
