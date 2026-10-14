from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path

from services.runtime.config import RuntimeConfig
from services.runtime.main import load_or_create_token


class RuntimeMainTests(unittest.TestCase):
    def test_session_token_is_created_private_then_reloaded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            token_path = root / "config" / "session.token"
            config = RuntimeConfig(data_dir=root / "data", config_dir=root / "config", runtime_dir=root / "runtime", token_file=token_path)
            first, path = load_or_create_token(config, environ={})
            self.assertEqual(path, token_path)
            self.assertGreaterEqual(len(first), 32)
            self.assertEqual(stat.S_IMODE(token_path.stat().st_mode), 0o600)
            second, same_path = load_or_create_token(config, environ={})
            self.assertEqual(second, first)
            self.assertEqual(same_path, token_path)

    def test_token_environment_does_not_create_a_file_and_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = RuntimeConfig(data_dir=root / "data", config_dir=root / "config", runtime_dir=root / "runtime", token_file=root / "config" / "session.token")
            external = root / "external"
            external.write_text("private-test-token-" + "z" * 40, encoding="ascii")
            config.token_file.parent.mkdir(mode=0o700)
            config.token_file.symlink_to(external)
            with self.assertRaises(RuntimeError):
                load_or_create_token(config, environ={})
            token, path = load_or_create_token(config, environ={"SIDEQUEST_API_TOKEN": "environment-test-token-" + "z" * 40})
            self.assertIsNone(path)
            self.assertTrue(token.startswith("environment-test-token-"))
            self.assertTrue(config.token_file.is_symlink())


if __name__ == "__main__":
    unittest.main()
