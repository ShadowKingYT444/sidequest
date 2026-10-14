"""Host-owned path and size settings for the B adapter."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


class ConfigurationError(ValueError):
    pass


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

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Settings":
        source = os.environ if env is None else env
        repos = _paths("SIDEQUEST_ALLOWED_REPO_ROOTS", source.get("SIDEQUEST_ALLOWED_REPO_ROOTS"))
        staging = _paths("SIDEQUEST_STAGING_ROOTS", source.get("SIDEQUEST_STAGING_ROOTS"))
        artifacts = _paths("SIDEQUEST_ARTIFACT_ROOTS", source.get("SIDEQUEST_ARTIFACT_ROOTS"))
        delivery = _paths("SIDEQUEST_DELIVERY_ROOTS", source.get("SIDEQUEST_DELIVERY_ROOTS"))
        approval_values = _paths("SIDEQUEST_DELIVERY_APPROVAL_ROOT", source.get("SIDEQUEST_DELIVERY_APPROVAL_ROOT"))
        state_values = _paths("SIDEQUEST_DELIVERY_STATE_ROOT", source.get("SIDEQUEST_DELIVERY_STATE_ROOT"))
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
        )
