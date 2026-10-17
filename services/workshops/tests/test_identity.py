from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from services.workshops.checks import CheckError, verify_trusted_integrity
from services.workshops.identity import (
    IdentityError,
    assigned_directory,
    verify_artifact_manifest,
    verify_candidate_tree,
    verify_host_artifact_inputs,
)
from services.workshops.tests.helpers import manifest_for, readonly_tree, write_manifest


ROOT = Path(__file__).resolve().parents[3]


class CandidateIdentityTests(unittest.TestCase):
    def test_manifest_hash_and_read_only_snapshot_match_exact_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "candidate"
            root.mkdir()
            (root / "index.html").write_text("<p>fixture</p>", encoding="utf-8")
            source_revision = "fixture:identity-test"
            manifest = manifest_for(root, candidate_id="identity-control", source_revision=source_revision)
            _, files = self._validate_manifest(manifest)
            readonly_tree(root)
            tree_hash, _ = verify_candidate_tree(root, files)
            self.assertEqual(tree_hash, manifest["candidate"]["tree_sha256"])

    def test_extra_file_and_writable_candidate_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "candidate"
            root.mkdir()
            (root / "index.html").write_text("x", encoding="utf-8")
            manifest = manifest_for(root, candidate_id="exact", source_revision="fixture:exact")
            (root / "unlisted.txt").write_text("untrusted", encoding="utf-8")
            with self.assertRaisesRegex(IdentityError, "Candidate root is writable|Candidate files do not match"):
                verify_candidate_tree(root, self._validate_manifest(manifest)[1])

    def test_symlink_candidate_path_and_traversal_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "candidate"
            root.mkdir()
            (root / "index.html").write_text("x", encoding="utf-8")
            os.symlink("/etc/passwd", root / "escape")
            with self.assertRaises(IdentityError):
                verify_candidate_tree(root, [], require_read_only=False)
            with self.assertRaises(IdentityError):
                assigned_directory(str(root / ".." / "candidate"), name="candidate")

    def test_manifest_digest_and_artifact_digest_are_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "candidate"
            root.mkdir()
            (root / "index.html").write_text("x", encoding="utf-8")
            manifest = manifest_for(root, candidate_id="digest", source_revision="fixture:digest")
            manifest_path = base / "manifest.json"
            digest = write_manifest(manifest_path, manifest)
            with self.assertRaisesRegex(IdentityError, "digest does not match"):
                verify_host_artifact_inputs([{
                    "id": "bad-digest", "sha256": "0" * 64, "staged_path": str(manifest_path),
                }])
            verified = verify_host_artifact_inputs([{
                "id": "good-digest", "sha256": digest, "staged_path": str(manifest_path),
            }])
            _, files, _artifact = verify_artifact_manifest(verified)
            self.assertEqual(len(files), 1)

    def test_deleted_manifest_entries_do_not_appear_in_candidate_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "candidate"
            root.mkdir()
            (root / "current.html").write_text("current", encoding="utf-8")
            manifest = manifest_for(root, candidate_id="with-deletion", source_revision="fixture:deleted")
            manifest["files"].append({
                "path": "gone.html", "mode": "100644", "size_bytes": 0,
                "sha256": hashlib.sha256(b"").hexdigest(), "status": "deleted",
            })
            records = [{key: row[key] for key in ("path", "mode", "size_bytes", "sha256")} for row in manifest["files"] if row["status"] != "deleted"]
            manifest["candidate"]["tree_sha256"] = hashlib.sha256(
                json.dumps({"v": 1, "files": sorted(records, key=lambda row: row["path"])}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
            ).hexdigest()
            with tempfile.TemporaryDirectory() as staging:
                path = Path(staging) / "manifest.json"
                digest = write_manifest(path, manifest)
                verified = verify_host_artifact_inputs([{"id": "manifest", "sha256": digest, "staged_path": str(path)}])
                _candidate, files, _artifact = verify_artifact_manifest(verified)
            readonly_tree(root)
            tree_hash, _ = verify_candidate_tree(root, files)
            self.assertEqual(tree_hash, manifest["candidate"]["tree_sha256"])

    def test_candidate_shadow_scripts_cannot_change_trusted_check_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "candidate"
            root.mkdir()
            (root / "index.html").write_text("<a href='/members/signup'>Join the club</a>", encoding="utf-8")
            (root / "trusted_checks.json").write_text(
                '{"v":1,"checks":[{"id":"club.signup.popup_destination","kind":"browser_signup","expected_path":"/members/signup"}]}',
                encoding="utf-8",
            )
            (root / "checks.py").write_text("def run_checks(*args): return {'passed': True}", encoding="utf-8")
            (root / "browser_checks.py").write_text("# pretend every route passed\n", encoding="utf-8")
            readonly_tree(root)
            before = hashlib.sha256((ROOT / "services/workshops/trusted_checks.json").read_bytes()).hexdigest()
            verify_trusted_integrity()
            after = hashlib.sha256((ROOT / "services/workshops/trusted_checks.json").read_bytes()).hexdigest()
            self.assertEqual(before, after)
            self.assertTrue((root / "checks.py").read_text(encoding="utf-8").startswith("def run_checks"))

    def test_modified_trusted_script_fails_integrity_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package_copy = Path(temp) / "workshops"
            shutil.copytree(ROOT / "services/workshops", package_copy, ignore=shutil.ignore_patterns("tests", "__pycache__"))
            target = package_copy / "checks.py"
            target.write_text(target.read_text(encoding="utf-8") + "\n# changed after freeze\n", encoding="utf-8")
            with self.assertRaises(CheckError) as caught:
                verify_trusted_integrity(package_copy)
            self.assertEqual(caught.exception.code, "TRUSTED_HARNESS_CHANGED")

    @staticmethod
    def _validate_manifest(manifest: dict):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.json"
            digest = write_manifest(path, manifest)
            inputs = verify_host_artifact_inputs([{"id": "candidate-manifest", "sha256": digest, "staged_path": str(path)}])
            return verify_artifact_manifest(inputs)[:2]


if __name__ == "__main__":
    unittest.main()
