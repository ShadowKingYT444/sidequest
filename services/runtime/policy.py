"""Typed policy checks shared by project, task and approval persistence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import CandidateIdentity, HEX_256_RE


class ErrorCode:
    INVALID_INPUT = "INVALID_INPUT"
    NOT_FOUND = "NOT_FOUND"
    VERSION_CONFLICT = "VERSION_CONFLICT"
    POLICY_DENIED = "POLICY_DENIED"
    BUDGET_LIMIT = "BUDGET_LIMIT"
    DEPENDENCY_FAILED = "DEPENDENCY_FAILED"
    UNAVAILABLE = "UNAVAILABLE"
    INTERNAL = "INTERNAL"


@dataclass(eq=False)
class RuntimeFault(Exception):
    code: str
    message: str
    retryable: bool = False

    def __str__(self) -> str:
        return self.message


class PolicyEngine:
    """Enforces local roots, action grants and exact approval identity."""

    @staticmethod
    def canonical_project_root(repo_path: str | Path, allowed_roots: tuple[Path, ...] | list[Path]) -> Path:
        try:
            supplied = Path(repo_path).expanduser()
            if not supplied.exists() or not supplied.is_dir():
                raise RuntimeFault(ErrorCode.INVALID_INPUT, "project path must be an existing directory")
            canonical = supplied.resolve(strict=True)
            allowed = [Path(root).expanduser().resolve(strict=True) for root in allowed_roots]
        except RuntimeFault:
            raise
        except (OSError, RuntimeError, ValueError):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "project path cannot be resolved") from None
        for root in allowed:
            try:
                canonical.relative_to(root)
                return canonical
            except ValueError:
                continue
        raise RuntimeFault(ErrorCode.POLICY_DENIED, "project path is outside configured roots")

    @staticmethod
    def assert_action_allowed(action: str, project_policy: dict[str, Any], job_actions: list[str]) -> None:
        if action not in project_policy.get("allowed_actions", []):
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "project policy does not allow this action")
        if action not in job_actions:
            raise RuntimeFault(ErrorCode.POLICY_DENIED, "job does not allow this action")

    @staticmethod
    def assert_candidate_current(
        requested: CandidateIdentity,
        *,
        expected_candidate_id: str | None,
        project_revision: str,
        candidate_base_revision: str,
        candidate_tree_sha256: str,
        candidate_patch_sha256: str,
    ) -> None:
        if not HEX_256_RE.fullmatch(candidate_tree_sha256) or not HEX_256_RE.fullmatch(candidate_patch_sha256):
            raise RuntimeFault(ErrorCode.INVALID_INPUT, "candidate identity is malformed")
        if (
            expected_candidate_id is None
            or requested.candidate_id != expected_candidate_id
            or requested.source_revision != project_revision
            or requested.source_revision != candidate_base_revision
            or requested.tree_sha256 != candidate_tree_sha256
            or requested.patch_sha256 != candidate_patch_sha256
        ):
            raise RuntimeFault(ErrorCode.VERSION_CONFLICT, "approval candidate identity is stale")

    @staticmethod
    def scopes_overlap(left: list[str], right: list[str]) -> bool:
        # An omitted scope is deliberately conservative: it serializes work.
        if not left or not right:
            return True
        for left_scope in left:
            for right_scope in right:
                if (
                    left_scope == right_scope
                    or left_scope.startswith(right_scope + "/")
                    or right_scope.startswith(left_scope + "/")
                ):
                    return True
        return False
