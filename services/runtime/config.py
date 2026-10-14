"""Local, non-secret runtime configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

from .models import canonical_sha256


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


def _bool_setting(name: str, value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    lowered = value.lower()
    if lowered in {"1", "true", "yes"}:
        return True
    if lowered in {"0", "false", "no", ""}:
        return False
    raise ValueError(f"{name} must be true or false")


def _bounded_integer(name: str, value: str | None, default: int, minimum: int, maximum: int) -> int:
    if value is None:
        return default
    if not re.fullmatch(r"[0-9]+", value):
        raise ValueError(f"{name} must be an integer")
    parsed = int(value)
    if not minimum <= parsed <= maximum:
        raise ValueError(f"{name} is outside its supported range")
    return parsed


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
    codex_enabled: bool = False
    codex_consent: bool = False
    codex_executable: Path | None = None
    codex_model: str | None = None
    codex_effort: str | None = None
    codex_max_seconds: int = 1200
    codex_token_budget: int = 30000
    codex_state_dir: Path | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "data_dir", Path(self.data_dir).expanduser())
        object.__setattr__(self, "config_dir", Path(self.config_dir).expanduser())
        object.__setattr__(self, "runtime_dir", Path(self.runtime_dir).expanduser())
        if self.token_file is not None:
            object.__setattr__(self, "token_file", Path(self.token_file).expanduser())
        if self.codex_executable is not None:
            object.__setattr__(self, "codex_executable", Path(self.codex_executable).expanduser())
        if self.codex_state_dir is not None:
            object.__setattr__(self, "codex_state_dir", Path(self.codex_state_dir).expanduser())
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
        if not isinstance(self.codex_enabled, bool) or not isinstance(self.codex_consent, bool):
            raise ValueError("Codex enabled and consent settings must be booleans")
        if not 1 <= self.codex_max_seconds <= 1200:
            raise ValueError("codex_max_seconds must be between 1 and 1200")
        if not 1 <= self.codex_token_budget <= 30000:
            raise ValueError("codex_token_budget must be between 1 and 30000")
        if self.codex_executable is not None and not self.codex_executable.is_absolute():
            raise ValueError("codex_executable must be an absolute host path")
        if self.codex_state_dir is not None and not self.codex_state_dir.is_absolute():
            raise ValueError("codex_state_dir must be an absolute host path")
        if self.codex_model is not None and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", self.codex_model):
            raise ValueError("codex_model contains unsupported characters")
        if self.codex_effort is not None and not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,31}", self.codex_effort):
            raise ValueError("codex_effort contains unsupported characters")
        if self.codex_enabled and (
            self.codex_executable is None
            or self.codex_model is None
            or self.codex_effort is None
            or self.codex_state_dir is None
        ):
            raise ValueError("enabled Codex requires host executable, model, effort and state directory settings")

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
        codex_enabled=_bool_setting("SIDEQUEST_CODEX_ENABLED", env.get("SIDEQUEST_CODEX_ENABLED")),
        codex_consent=_bool_setting("SIDEQUEST_CODEX_CONSENT", env.get("SIDEQUEST_CODEX_CONSENT")),
        codex_executable=Path(env["SIDEQUEST_CODEX_EXECUTABLE"]).expanduser()
        if env.get("SIDEQUEST_CODEX_EXECUTABLE")
        else None,
        codex_model=env.get("SIDEQUEST_CODEX_MODEL") or None,
        codex_effort=env.get("SIDEQUEST_CODEX_EFFORT") or None,
        codex_max_seconds=_bounded_integer("SIDEQUEST_CODEX_MAX_SECONDS", env.get("SIDEQUEST_CODEX_MAX_SECONDS"), 1200, 1, 1200),
        codex_token_budget=_bounded_integer("SIDEQUEST_CODEX_TOKEN_BUDGET", env.get("SIDEQUEST_CODEX_TOKEN_BUDGET"), 30000, 1, 30000),
        codex_state_dir=Path(env["SIDEQUEST_CODEX_STATE_DIR"]).expanduser()
        if env.get("SIDEQUEST_CODEX_STATE_DIR")
        else None,
        token_file=Path(env["SIDEQUEST_API_TOKEN_FILE"]).expanduser()
        if env.get("SIDEQUEST_API_TOKEN_FILE")
        else config_dir / "session.token",
    )


CODEX_READINESS_TTL_SECONDS = 600


def codex_configuration_fingerprint(
    config: RuntimeConfig,
    environ: dict[str, str] | None = None,
) -> str:
    """Hash only non-secret settings that affect the read-only readiness result."""
    env = os.environ if environ is None else environ
    return canonical_sha256({
        "enabled": config.codex_enabled,
        "b_argv": list(config.b_argv),
        "executable": str(config.codex_executable) if config.codex_executable else None,
        "model": config.codex_model,
        "effort": config.codex_effort,
        "state_dir": str(config.codex_state_dir) if config.codex_state_dir else None,
        "home": env.get("HOME"),
        "codex_home": env.get("CODEX_HOME"),
    })


def codex_readiness_is_fresh(
    config: RuntimeConfig,
    record: dict[str, object] | None,
    *,
    now: datetime | None = None,
    environ: dict[str, str] | None = None,
) -> bool:
    if not config.codex_enabled or not isinstance(record, dict):
        return False
    if record.get("config_sha256") != codex_configuration_fingerprint(config, environ):
        return False
    capability = record.get("capability")
    refreshed_at = record.get("refreshed_at")
    if not isinstance(capability, dict) or not isinstance(refreshed_at, str):
        return False
    try:
        parsed = datetime.fromisoformat(refreshed_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    # An unqualified local wall clock cannot be compared to UTC readiness TTL.
    # Treat it as stale instead of letting aware/naive subtraction raise 500.
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return False
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        return False
    age = (current - parsed).total_seconds()
    model = capability.get("model")
    effort = capability.get("effort")
    return (
        0 <= age <= CODEX_READINESS_TTL_SECONDS
        and capability.get("state") == "available"
        and capability.get("provider") == "codex-app-server"
        and capability.get("account_type") == "chatgpt"
        and capability.get("usd_cost_enforced") is True
        and capability.get("reason") is None
        and isinstance(model, dict)
        and model.get("id") == config.codex_model
        and model.get("verified") is True
        and isinstance(effort, dict)
        and effort.get("id") == config.codex_effort
        and effort.get("verified") is True
    )


def codex_execution_enabled(
    config: RuntimeConfig,
    record: dict[str, object] | None,
    *,
    now: datetime | None = None,
    environ: dict[str, str] | None = None,
) -> bool:
    return config.codex_consent and codex_readiness_is_fresh(config, record, now=now, environ=environ)
