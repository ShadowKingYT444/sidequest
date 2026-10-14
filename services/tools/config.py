"""Host-owned path and size settings for the B adapter."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re


class ConfigurationError(ValueError):
    pass


_CODEX_MODEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_CODEX_EFFORT = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,31}$")


def _bool_setting(name: str, value: str | None) -> bool:
    if value is None:
        return False
    if value.lower() in {"1", "true", "yes"}:
        return True
    if value.lower() in {"0", "false", "no", ""}:
        return False
    raise ConfigurationError(f"{name} must be true or false.")


def _bounded_integer(name: str, value: str | None, default: int, minimum: int, maximum: int) -> int:
    if value is None:
        return default
    if not re.fullmatch(r"[0-9]+", value):
        raise ConfigurationError(f"{name} must be an integer.")
    parsed = int(value)
    if parsed < minimum or parsed > maximum:
        raise ConfigurationError(f"{name} is outside its supported range.")
    return parsed


def _codex_executable(value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        raise ConfigurationError("SIDEQUEST_CODEX_EXECUTABLE must be an absolute host path.")
    resolved = path.resolve(strict=False)
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise ConfigurationError("SIDEQUEST_CODEX_EXECUTABLE must resolve to an executable file.")
    return resolved


def _codex_state_dir(value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        raise ConfigurationError("SIDEQUEST_CODEX_STATE_DIR must be an absolute host path.")
    # Do not canonicalize through symlinks. The bridge rechecks this path before
    # use and requires it to remain outside every mutable project/workspace root.
    return Path(os.path.abspath(path))


def _paths(name: str, value: str | None) -> tuple[Path, ...]:
    if not value:
        return ()
    result: list[Path] = []
    for raw in value.split(os.pathsep):
        if not raw:
            continue
        path = Path(raw).expanduser()
        if not path.is_absolute():
            raise ConfigurationError(f"{name} entries must be absolute host paths.")
        result.append(path.resolve(strict=False))
    return tuple(result)


@dataclass(frozen=True)
class Settings:
    allowed_repo_roots: tuple[Path, ...]
    staging_roots: tuple[Path, ...]
    artifact_roots: tuple[Path, ...]
    delivery_roots: tuple[Path, ...]
    approval_root: Path
    delivery_state_root: Path
    max_files: int = 1000
    max_total_bytes: int = 100 * 1024 * 1024
    max_file_bytes: int = 100 * 1024 * 1024
    git_timeout_seconds: float = 30.0
    max_git_output_bytes: int = 120 * 1024 * 1024
    codex_enabled: bool = False
    codex_consent: bool = False
    codex_executable: Path | None = None
    codex_model: str | None = None
    codex_effort: str | None = None
    codex_max_seconds: int = 1200
    codex_token_budget: int = 30000
    codex_state_dir: Path | None = None

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Settings":
        source = os.environ if env is None else env
        repos = _paths("SIDEQUEST_ALLOWED_REPO_ROOTS", source.get("SIDEQUEST_ALLOWED_REPO_ROOTS"))
        staging = _paths("SIDEQUEST_STAGING_ROOTS", source.get("SIDEQUEST_STAGING_ROOTS"))
        artifacts = _paths("SIDEQUEST_ARTIFACT_ROOTS", source.get("SIDEQUEST_ARTIFACT_ROOTS"))
        delivery = _paths("SIDEQUEST_DELIVERY_ROOTS", source.get("SIDEQUEST_DELIVERY_ROOTS"))
        approval_values = _paths("SIDEQUEST_DELIVERY_APPROVAL_ROOT", source.get("SIDEQUEST_DELIVERY_APPROVAL_ROOT"))
        state_values = _paths("SIDEQUEST_DELIVERY_STATE_ROOT", source.get("SIDEQUEST_DELIVERY_STATE_ROOT"))
        codex_enabled = _bool_setting("SIDEQUEST_CODEX_ENABLED", source.get("SIDEQUEST_CODEX_ENABLED"))
        codex_consent = _bool_setting("SIDEQUEST_CODEX_CONSENT", source.get("SIDEQUEST_CODEX_CONSENT"))
        codex_executable = _codex_executable(source.get("SIDEQUEST_CODEX_EXECUTABLE"))
        codex_model = source.get("SIDEQUEST_CODEX_MODEL") or None
        codex_effort = source.get("SIDEQUEST_CODEX_EFFORT") or None
        codex_max_seconds = _bounded_integer("SIDEQUEST_CODEX_MAX_SECONDS", source.get("SIDEQUEST_CODEX_MAX_SECONDS"), 1200, 1, 1200)
        codex_token_budget = _bounded_integer("SIDEQUEST_CODEX_TOKEN_BUDGET", source.get("SIDEQUEST_CODEX_TOKEN_BUDGET"), 30000, 1, 30000)
        codex_state_dir = _codex_state_dir(source.get("SIDEQUEST_CODEX_STATE_DIR"))
        if codex_model is not None and not _CODEX_MODEL_ID.fullmatch(codex_model):
            raise ConfigurationError("SIDEQUEST_CODEX_MODEL contains unsupported characters.")
        if codex_effort is not None and not _CODEX_EFFORT.fullmatch(codex_effort):
            raise ConfigurationError("SIDEQUEST_CODEX_EFFORT contains unsupported characters.")
        if codex_enabled and (codex_executable is None or codex_model is None or codex_effort is None or codex_state_dir is None):
            raise ConfigurationError(
                "Enabled Codex execution requires host executable, model, effort and runtime state directory settings."
            )
        if not repos or not staging or not artifacts or not delivery or len(approval_values) != 1 or len(state_values) != 1:
            raise ConfigurationError(
                "Configure SIDEQUEST_ALLOWED_REPO_ROOTS, SIDEQUEST_STAGING_ROOTS, "
                "SIDEQUEST_ARTIFACT_ROOTS, SIDEQUEST_DELIVERY_ROOTS, "
                "SIDEQUEST_DELIVERY_APPROVAL_ROOT and SIDEQUEST_DELIVERY_STATE_ROOT."
            )
        return cls(
            allowed_repo_roots=repos,
            staging_roots=staging,
            artifact_roots=artifacts,
            delivery_roots=delivery,
            approval_root=approval_values[0],
            delivery_state_root=state_values[0],
            codex_enabled=codex_enabled,
            codex_consent=codex_consent,
            codex_executable=codex_executable,
            codex_model=codex_model,
            codex_effort=codex_effort,
            codex_max_seconds=codex_max_seconds,
            codex_token_budget=codex_token_budget,
            codex_state_dir=codex_state_dir,
        )
