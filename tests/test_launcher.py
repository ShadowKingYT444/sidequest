"""Launcher contracts: fresh Git setup, ephemeral auth, and owned-process cleanup."""
import argparse
from contextlib import contextmanager
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sidequest


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sidequest-launcher-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "project with spaces"
        self.repo.mkdir()
        self.git("init", "-q")
        (self.repo / "readme.txt").write_text("first commit\n")
        self.git("add", ".")
        self.git("-c", "user.name=Launcher Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "initial")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], text=True).strip()

    def test_new_repository_uses_head_for_valid_empty_comparison(self):
        root, base = sidequest.project(self.repo, None)
        self.assertEqual(root, self.repo)
        self.assertEqual(base, self.git("rev-parse", "HEAD"))

    def test_existing_repository_uses_previous_commit_and_allows_explicit_base(self):
        original = self.git("rev-parse", "HEAD")
        (self.repo / "readme.txt").write_text("next commit\n")
        self.git("-c", "user.name=Launcher Test", "-c", "user.email=test@example.invalid", "commit", "-qam", "next")
        self.assertEqual(sidequest.project(self.repo, None)[1], original)
        self.assertEqual(sidequest.project(self.repo, "HEAD")[1], self.git("rev-parse", "HEAD"))
        with self.assertRaises(sidequest.SetupError):
            sidequest.project(self.repo, "--help")

    def test_private_runtime_state_cannot_live_in_git_or_shared_root(self):
        for path in (self.repo / "ignored-state", self.repo, Path("/tmp")):
            with self.subTest(path=path), self.assertRaises(sidequest.SetupError):
                sidequest.state_directory(path)
        self.assertEqual(sidequest.state_directory(self.root / "state"), self.root / "state")

    def test_auth_is_process_only_and_inherited_authority_is_not_enabled(self):
        before = {"SIDEQUEST_API_TOKEN_FILE":"old-secret-file", "SIDEQUEST_CODEX_ENABLED":"true",
                  "SIDEQUEST_B_ARGV":"untrusted-adapter", "SIDEQUEST_DATA_DIR":"old-state",
                  "SIDEQUEST_CODEX_EXECUTABLE":"/usr/local/bin/codex", "CODEX_HOME":"/existing/account"}
        with patch.dict(os.environ, before):
            env = sidequest.runtime_environment(self.root / "state", self.repo, "base", 4317, "ephemeral-test-value")
        self.assertEqual(env["SIDEQUEST_API_TOKEN"], env["SIDEQUEST_RUNTIME_TOKEN"])
        self.assertNotIn("SIDEQUEST_API_TOKEN_FILE", env)
        self.assertNotIn("SIDEQUEST_B_ARGV", env)
        self.assertEqual(env["SIDEQUEST_CODEX_ENABLED"], "false")
        self.assertEqual(env["SIDEQUEST_CODEX_CONSENT"], "false")
        self.assertEqual(env["CODEX_HOME"], "/existing/account")
        self.assertEqual(env["SIDEQUEST_CODEX_EXECUTABLE"], "/usr/local/bin/codex")
        self.assertFalse((self.root / "state").exists(), "environment construction writes no credential or state")

    def test_two_launchers_cannot_recover_the_same_runtime_state_at_once(self):
        state = self.root / "state"
        with sidequest.state_lock(state):
            with self.assertRaisesRegex(sidequest.SetupError, "already running"):
                with sidequest.state_lock(state):
                    self.fail("second launcher acquired lock")
        with sidequest.state_lock(state):
            pass

    def test_dead_runtime_fails_before_ui_starts(self):
        child = subprocess.Popen([sys.executable, "-c", "raise SystemExit(9)"], start_new_session=True)
        child.wait()
        with self.assertRaisesRegex(sidequest.SetupError, "stopped during startup"):
            sidequest.wait_for_runtime(child, 1, "ephemeral-test-value", timeout=1)

    def test_stop_terminates_owned_process(self):
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], start_new_session=True)
        self.addCleanup(sidequest.stop, child)
        sidequest.stop(child)
        self.assertIsNotNone(child.poll())

    def test_native_headless_error_precedes_runtime_spawn(self):
        args = argparse.Namespace(repo=self.repo, base=None, state_dir=self.root / "state", browser=False)
        env = {key:value for key,value in os.environ.items() if key not in {"DISPLAY", "WAYLAND_DISPLAY"}}
        with patch.dict(os.environ, env, clear=True), patch.object(sys, "platform", "linux"), patch.object(sidequest, "prerequisites"), patch.object(sidequest.subprocess, "Popen") as popen:
            with patch.object(sidequest, "project", return_value=(self.repo, "HEAD")):
                with self.assertRaisesRegex(sidequest.SetupError, "No desktop display"):
                    sidequest.run(args)
            popen.assert_not_called()

    def test_ui_failure_stops_runtime_and_returns_failure(self):
        args = argparse.Namespace(repo=self.repo, base=None, state_dir=self.root / "state", browser=True)
        children = []
        real_popen = subprocess.Popen
        def spawn(_argv, **kwargs):
            program = "import time; time.sleep(60)" if not children else "raise SystemExit(7)"
            child = real_popen([sys.executable, "-c", program], **kwargs)
            children.append(child)
            return child
        with patch.object(sidequest, "prerequisites"), patch.object(sidequest, "project", return_value=(self.repo, "HEAD")), patch.object(sidequest, "wait_for_runtime"), patch.object(sidequest.subprocess, "Popen", side_effect=spawn):
            with self.assertRaisesRegex(sidequest.SetupError, "office could not run"):
                sidequest.run(args)
        self.assertEqual(len(children), 2)
        self.assertTrue(all(child.poll() is not None for child in children))


if __name__ == "__main__":
    unittest.main()
