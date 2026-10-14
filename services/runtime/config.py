"""Local, non-secret runtime configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
import json
from pathlib import Path
import sys


def default_data_dir(environ: dict[str, str] | None = None) -> Path:
    env = os.environ if environ is None else environ
    xdg_data_home = env.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home).expanduser() / "sidequest"
    return Path.home() / ".local" / "share" / "sidequest"


def default_config_dir(environ: dict[str, str] | None = None) -> Path:
    env = os.environ if environ is None else environ
    xdg_config_home = env.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        return Path(xdg_config_home).expanduser() / "sidequest"
    return Path.home() / ".config" / "sidequest"


def default_runtime_dir(environ: dict[str, str] | None = None) -> Path:
    env = os.environ if environ is None else environ
    xdg_runtime_dir = env.get("XDG_RUNTIME_DIR")
    if xdg_runtime_dir:
        return Path(xdg_runtime_dir).expanduser() / "sidequest"
    return Path(f"/tmp/sidequest-{os.getuid()}")


@dataclass(frozen=True)
class RuntimeConfig:
    """Resolved local paths and safe concurrency defaults for one runtime."""

    data_dir: Path = field(default_factory=default_data_dir)
    config_dir: Path = field(default_factory=default_config_dir)
    runtime_dir: Path = field(default_factory=default_runtime_dir)
    allowed_roots: tuple[Path, ...] = ()
    max_parallel: int = 2
    max_tasks_per_plan: int = 4
    sqlite_busy_timeout_ms: int = 5000
    service_token: str | None = field(default=None, repr=False)
    token_file: Path | None = None
    bind_host: str = "127.0.0.1"
    bind_port: int = 4317
    b_argv: tuple[str, ...] = ()
    d_argv: tuple[str, ...] = ()
    adapter_timeout_seconds: float = 120.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "data_dir", Path(self.data_dir).expanduser())
        object.__setattr__(self, "config_dir", Path(self.config_dir).expanduser())
        object.__setattr__(self, "runtime_dir", Path(self.runtime_dir).expanduser())
        if self.token_file is not None:
            object.__setattr__(self, "token_file", Path(self.token_file).expanduser())
        object.__setattr__(
            self,
            "allowed_roots",
            tuple(Path(path).expanduser() for path in self.allowed_roots),
        )
        if not 1 <= self.max_parallel <= 4:
            raise ValueError("max_parallel must be between 1 and 4")
        if not 1 <= self.max_tasks_per_plan <= 4:
            raise ValueError("max_tasks_per_plan must be between 1 and 4")
        if self.sqlite_busy_timeout_ms < 1:
            raise ValueError("sqlite_busy_timeout_ms must be positive")
        if self.bind_host != "127.0.0.1":
            raise ValueError("the local runtime must bind to 127.0.0.1")
        if not 1 <= self.bind_port <= 65535:
            raise ValueError("bind_port must be between 1 and 65535")
        if self.adapter_timeout_seconds <= 0:
            raise ValueError("adapter_timeout_seconds must be positive")

    @property
    def workspaces_dir(self) -> Path:
        return self.data_dir / "workspaces"

    @property
    def adapter_output_dir(self) -> Path:
        return self.data_dir / "adapter-output"

    @property
    def adapter_input_dir(self) -> Path:
        return self.data_dir / "adapter-inputs"

    @property
    def artifacts_dir(self) -> Path:
        return self.data_dir / "artifacts"

    @property
    def delivery_disabled_dir(self) -> Path:
        return self.data_dir / "delivery-disabled"

    @property
    def database_path(self) -> Path:
        return self.data_dir / "state.db"


def _argv_setting(name: str, raw: str | None, default: tuple[str, ...]) -> tuple[str, ...]:
    if not raw:
        return default
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"{name} must be a JSON string array") from None
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{name} must be a non-empty JSON string array")
    return tuple(value)


def runtime_config_from_env(environ: dict[str, str] | None = None) -> RuntimeConfig:
    """Resolve host-owned service settings. The token value is read separately by main."""
    env = os.environ if environ is None else environ
    data_dir = Path(env.get("SIDEQUEST_DATA_DIR", str(default_data_dir(env)))).expanduser()
    config_dir = Path(env.get("SIDEQUEST_CONFIG_DIR", str(default_config_dir(env)))).expanduser()
    runtime_dir = Path(env.get("SIDEQUEST_RUNTIME_DIR", str(default_runtime_dir(env)))).expanduser()
    raw_roots = env.get("SIDEQUEST_ALLOWED_ROOTS", "")
    roots = tuple(Path(item).expanduser() for item in raw_roots.split(os.pathsep) if item)
    try:
        max_parallel = int(env.get("SIDEQUEST_MAX_PARALLEL", "2"))
        port = int(env.get("SIDEQUEST_PORT", "4317"))
        timeout = float(env.get("SIDEQUEST_ADAPTER_TIMEOUT_SECONDS", "120"))
    except ValueError:
        raise ValueError("runtime numeric environment settings are invalid") from None
    b_default = (sys.executable, "-m", "services.tools.main")
    d_default = (sys.executable, "-m", "services.workshops.main")
    return RuntimeConfig(
        data_dir=data_dir,
        config_dir=config_dir,
        runtime_dir=runtime_dir,
        allowed_roots=roots,
        max_parallel=max_parallel,
        bind_host=env.get("SIDEQUEST_HOST", "127.0.0.1"),
        bind_port=port,
        b_argv=_argv_setting("SIDEQUEST_B_ARGV", env.get("SIDEQUEST_B_ARGV"), b_default),
        d_argv=_argv_setting("SIDEQUEST_D_ARGV", env.get("SIDEQUEST_D_ARGV"), d_default),
        adapter_timeout_seconds=timeout,
        token_file=Path(env["SIDEQUEST_API_TOKEN_FILE"]).expanduser()
        if env.get("SIDEQUEST_API_TOKEN_FILE")
        else config_dir / "session.token",
    )
