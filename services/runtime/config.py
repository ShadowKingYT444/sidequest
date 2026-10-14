"""Local, non-secret runtime configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


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

    def __post_init__(self) -> None:
        object.__setattr__(self, "data_dir", Path(self.data_dir).expanduser())
        object.__setattr__(self, "config_dir", Path(self.config_dir).expanduser())
        object.__setattr__(self, "runtime_dir", Path(self.runtime_dir).expanduser())
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

    @property
    def database_path(self) -> Path:
        return self.data_dir / "state.db"
