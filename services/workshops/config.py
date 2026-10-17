"""Small, explicit configuration surface for the D verification adapter."""

from __future__ import annotations

import os
from pathlib import Path

PROTOCOL_VERSION = 1
MAX_REQUEST_BYTES = 4 * 1024 * 1024
MAX_ARTIFACT_INPUT_BYTES = 16 * 1024 * 1024
MAX_REPORT_BYTES = 2 * 1024 * 1024
MAX_SCREENSHOT_BYTES = 8 * 1024 * 1024
MAX_CANDIDATE_FILES = 1_000
MAX_CANDIDATE_BYTES = 100 * 1024 * 1024
MAX_HTML_BYTES = 1024 * 1024
MAX_BROWSER_REQUESTS = 256
BROWSER_TIMEOUT_MS = 5_000
BROWSER_TOTAL_TIMEOUT_SECONDS = 20
TRUSTED_CHECKS_PATH = Path(__file__).with_name("trusted_checks.json")
TRUST_LOCK_PATH = Path(__file__).with_name("trust.lock.json")


def chromium_path() -> Path:
    """Resolve the host-configured Chromium executable without downloading one."""
    configured = os.environ.get("CHROMIUM_PATH")
    if configured:
        return Path(configured)
    return Path("/usr/bin/chromium")
