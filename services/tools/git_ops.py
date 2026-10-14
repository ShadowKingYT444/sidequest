"""Bounded, shell-free Git operations over allowlisted local repositories."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import selectors
import shutil
import stat
import subprocess
import tempfile
import time
import uuid
from typing import Iterable

try:
    from .config import Settings
    from .protocol import AdapterError
except ImportError:  # Direct script execution by the adapter host.
    from config import Settings
    from protocol import AdapterError


_SECRET_NAME = re.compile(r"(?:^|[._-])(?:credentials?|secrets?|tokens?|passwords?|private[_-]?keys?)(?:$|[._-])", re.IGNORECASE)
_SECRET_FILE_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".conf", ".cfg", ".txt", ".env"}
_CONFIG_ASSIGNMENT_EXTENSIONS = {".cfg", ".conf", ".ini", ".properties", ".toml", ".yaml", ".yml"}
_SECRET_ASSIGNMENT = re.compile(
    rb"(?im)^\s*(?:export\s+)?[A-Z0-9_]*(?:TOKEN|SECRET|API_KEY|PASSWORD|PRIVATE_KEY|ACCESS_KEY)[A-Z0-9_]*\s*[:=]\s*(['\"])([^'\"\r\n]{12,})\1\s*(?:\#.*)?$"
)
_CONFIG_SECRET_ASSIGNMENT = re.compile(
    rb"(?im)^\s*(?:export\s+)?[A-Z0-9_]*(?:TOKEN|SECRET|API_KEY|PASSWORD|PRIVATE_KEY|ACCESS_KEY|CREDENTIALS?)[A-Z0-9_]*\s*[:=]\s*([^\s#;\"'(),]{12,})\s*(?:[;#].*)?$"
)
_CONFIG_SECRET_REFERENCE = re.compile(rb"(?:\$\{?[A-Z_][A-Z0-9_]*\}?|%[A-Z_][A-Z0-9_]*%|\{\{[A-Z0-9_.:-]{1,128}\}\})", re.IGNORECASE)
_SECRET_JSON = re.compile(
    rb"(?is)[\"'](?:private_key|client_secret|refresh_token|access_token|api_key|api_token|token|secret|password)[\"']\s*:\s*[\"'][^\"']{4,}[\"']"
)
_KNOWN_TOKEN = re.compile(
    rb"(?i)(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})"
)
_PRIVATE_KEY = re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")
_HEX_OBJECT = re.compile(r"^[0-9a-fA-F]{40,64}$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
_GIT_BINARY = next(
    (candidate for candidate in ("/usr/bin/git", "/bin/git", "/usr/local/bin/git") if os.path.isfile(candidate) and os.access(candidate, os.X_OK)),
    None,
)


@dataclass(frozen=True)
class TreeEntry:
    mode: str
    oid: str
    path: str


@dataclass(frozen=True)
class FileData:
    mode: str
    data: bytes


def _error(code: str, message: str, retryable: bool = False) -> AdapterError:
    return AdapterError(code, message, retryable)


def open_directory_beneath(path: str | Path, roots: Iterable[Path], *, create: bool = False) -> int:
    """Open an absolute directory without following any path component symlinks.

    The returned descriptor pins the checked directory even if a pathname is
    subsequently renamed. Callers should perform file operations relative to
    this descriptor rather than re-resolving a checked string path.
    """
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise _error("DEPENDENCY_FAILED", "No-follow directory access is unavailable on this platform.")
    absolute = Path(os.path.abspath(os.fspath(path)))
    matches: list[tuple[int, Path, Path]] = []
    for root in roots:
        canonical = Path(os.path.abspath(os.fspath(root)))
        try:
            relative = absolute.relative_to(canonical)
        except ValueError:
            continue
        matches.append((len(canonical.parts), canonical, relative))
    if not matches:
        raise _error("POLICY_DENIED", "Directory is outside configured host roots.")
    _, root, relative = max(matches, key=lambda item: item[0])
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(os.sep, flags)
    except OSError as exc:
        raise _error("POLICY_DENIED", "Filesystem root could not be opened safely.") from exc
    try:
        for component in (*root.parts[1:], *relative.parts):
            if component in {"", ".", ".."}:
                raise _error("POLICY_DENIED", "Directory path is not normalized.")
            try:
                try:
                    before = os.stat(component, dir_fd=fd, follow_symlinks=False)
                except FileNotFoundError:
                    if not create:
                        raise
                    try:
                        os.mkdir(component, mode=0o700, dir_fd=fd)
                    except FileExistsError:
                        pass
                    before = os.stat(component, dir_fd=fd, follow_symlinks=False)
                if not stat.S_ISDIR(before.st_mode):
                    raise _error("POLICY_DENIED", "Directory paths cannot contain symlinks or files.")
                child_fd = os.open(component, flags, dir_fd=fd)
            except AdapterError:
                raise
            except OSError as exc:
                raise _error("POLICY_DENIED", "Directory path could not be opened safely.") from exc
            after = os.fstat(child_fd)
            if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
                os.close(child_fd)
                raise _error("POLICY_DENIED", "Directory changed while it was opened.")
            os.close(fd)
            fd = child_fd
        return fd
    except Exception:
        os.close(fd)
        raise


def _open_child_directory(parent_fd: int, name: str) -> int:
    try:
        before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if not stat.S_ISDIR(before.st_mode):
            raise _error("POLICY_DENIED", "Git metadata cannot contain symlinks or special directories.")
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        fd = os.open(name, flags, dir_fd=parent_fd)
    except AdapterError:
        raise
    except OSError as exc:
        raise _error("POLICY_DENIED", "Git metadata directory could not be opened safely.") from exc
    after = os.fstat(fd)
    if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
        os.close(fd)
        raise _error("POLICY_DENIED", "Git metadata directory changed while it was opened.")
    return fd


def _canonical_under(raw: str | Path, roots: Iterable[Path], *, must_exist: bool = True) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise _error("POLICY_DENIED", "Host-assigned paths must be absolute.")
    if any(ord(char) < 0x20 or ord(char) == 0x7F for char in str(path)):
        raise _error("POLICY_DENIED", "Host-assigned paths cannot contain control characters.")
    path = Path(os.path.abspath(path))
    # Refuse symlinks in every existing component before resolving containment.
    cursor = Path(path.anchor)
    for component in path.parts[1:]:
        cursor = cursor / component
        try:
            info = cursor.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise _error("INVALID_INPUT", "Path could not be inspected safely.") from exc
        if stat.S_ISLNK(info.st_mode):
            raise _error("POLICY_DENIED", "Symlink paths are not allowed.")
    if must_exist and not path.exists():
        raise _error("NOT_FOUND", "Configured path does not exist.")
    resolved = path.resolve(strict=must_exist)
    for root in roots:
        canonical_root = root.resolve(strict=False)
        try:
            resolved.relative_to(canonical_root)
            return resolved
        except ValueError:
            pass
    raise _error("POLICY_DENIED", "Path is outside configured host roots.")


def validate_repo_path(raw: str, roots: Iterable[Path]) -> Path:
    path = _canonical_under(raw, roots, must_exist=True)
    if not path.is_dir():
        raise _error("INVALID_INPUT", "Repository path must be a directory.")
    dot_git = path / ".git"
    try:
        info = dot_git.lstat()
    except OSError as exc:
        raise _error("INVALID_INPUT", "Expected a Git worktree with a local .git directory.") from exc
    if not stat.S_ISDIR(info.st_mode):
        raise _error("POLICY_DENIED", "Git worktrees with redirected metadata are not supported.")
    return path


def validate_workspace_path(raw: str, roots: Iterable[Path], *, must_exist: bool) -> Path:
    path = _canonical_under(raw, roots, must_exist=must_exist)
    if must_exist and not path.is_dir():
        raise _error("INVALID_INPUT", "Workspace must be a directory.")
    return path


def validate_relative_path(raw: str) -> str:
    if not isinstance(raw, str) or not raw or "\x00" in raw or "\\" in raw:
        raise _error("POLICY_DENIED", "Unsafe repository path.")
    try:
        raw.encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise _error("POLICY_DENIED", "Repository path is not valid UTF-8.") from exc
    if raw.startswith("/") or re.match(r"^[A-Za-z]:", raw):
        raise _error("POLICY_DENIED", "Absolute repository paths are not allowed.")
    parts = raw.split("/")
    if any(part in {"", ".", ".."} for part in parts) or any(part.lower() == ".git" for part in parts):
        raise _error("POLICY_DENIED", "Traversal and Git metadata paths are not allowed.")
    if PurePosixPath(raw).as_posix() != raw:
        raise _error("POLICY_DENIED", "Repository path is not normalized.")
    return raw


def is_sensitive_path(path: str) -> bool:
    validated = validate_relative_path(path)
    lower = validated.lower()
    parts = lower.split("/")
    basename = parts[-1]
    if any(part in {"credentials", "credential", "secrets", "secret", ".aws", ".ssh"} for part in parts):
        return True
    if basename == ".env" or (basename.startswith(".env.") and basename not in {".env.example", ".env.sample", ".env.template"}):
        return True
    if basename in {".netrc", ".npmrc", ".pypirc", "id_rsa", "id_ed25519", "credentials.json"}:
        return True
    if basename.endswith((".pem", ".key", ".p12", ".pfx")):
        return True
    suffix = Path(basename).suffix.lower()
    stem = basename[: -len(suffix)] if suffix else basename
    return suffix in _SECRET_FILE_EXTENSIONS and bool(_SECRET_NAME.search(stem))


def contains_secret(data: bytes, path: str | None = None) -> bool:
    if _SECRET_ASSIGNMENT.search(data) or _SECRET_JSON.search(data) or _KNOWN_TOKEN.search(data) or _PRIVATE_KEY.search(data):
        return True
    if path is not None and PurePosixPath(path).suffix.lower() in _CONFIG_ASSIGNMENT_EXTENSIONS:
        return any(not _CONFIG_SECRET_REFERENCE.fullmatch(match.group(1)) for match in _CONFIG_SECRET_ASSIGNMENT.finditer(data))
    return False


def _safe_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.devnull,
        "LC_ALL": "C.UTF-8",
        "LANG": "C.UTF-8",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_COUNT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_ATTR_NOSYSTEM": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_LFS_SKIP_SMUDGE": "1",
    }
    if extra:
        env.update(extra)
    return env


def run_git(
    repo: Path,
    args: list[str],
    *,
    input_data: bytes | None = None,
    settings: Settings,
    extra_env: dict[str, str] | None = None,
    timeout: float | None = None,
    output_limit: int | None = None,
    error_code: str = "INVALID_INPUT",
) -> bytes:
    if _GIT_BINARY is None:
        raise _error("DEPENDENCY_FAILED", "Git is not installed in a trusted system path.")
    command = [
        _GIT_BINARY,
        "--no-pager",
        "-c", "core.hooksPath=/dev/null",
        "-c", "core.fsmonitor=false",
        "-c", "core.pager=cat",
        "-c", "core.autocrlf=false",
        "-c", "core.safecrlf=false",
        "-c", "commit.gpgSign=false",
        "-c", "credential.helper=",
        "-c", "diff.external=",
        "-c", "core.attributesFile=/dev/null",
        "-c", "protocol.ext.allow=never",
        *args,
    ]
    limit = output_limit if output_limit is not None else settings.max_git_output_bytes
    error_limit = 1024 * 1024
    deadline = time.monotonic() + (timeout if timeout is not None else settings.git_timeout_seconds)
    try:
        process = subprocess.Popen(
            command,
            cwd=repo,
            stdin=subprocess.PIPE if input_data is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_safe_env(extra_env),
            shell=False,
            bufsize=0,
        )
    except OSError as exc:
        raise _error("DEPENDENCY_FAILED", "Git could not be started.") from exc
    output = bytearray()
    errors = bytearray()
    selector = selectors.DefaultSelector()
    input_offset = 0
    try:
        assert process.stdout is not None and process.stderr is not None
        for stream in (process.stdout, process.stderr):
            os.set_blocking(stream.fileno(), False)
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        selector.register(process.stderr, selectors.EVENT_READ, "stderr")
        if process.stdin is not None:
            os.set_blocking(process.stdin.fileno(), False)
            if input_data:
                selector.register(process.stdin, selectors.EVENT_WRITE, "stdin")
            else:
                process.stdin.close()
                process.stdin = None
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError
            events = selector.select(min(remaining, 0.25))
            for key, mask in events:
                if key.data == "stdin":
                    try:
                        sent = os.write(key.fileobj.fileno(), input_data[input_offset:input_offset + 65536])
                        input_offset += sent
                    except BrokenPipeError:
                        input_offset = len(input_data or b"")
                    if input_offset >= len(input_data or b""):
                        selector.unregister(key.fileobj)
                        key.fileobj.close()
                        process.stdin = None
                else:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        key.fileobj.close()
                        continue
                    if key.data == "stdout":
                        output.extend(chunk)
                        if len(output) > limit:
                            raise OverflowError
                    else:
                        errors.extend(chunk)
                        if len(errors) > error_limit:
                            raise OverflowError
        return_code = process.wait(timeout=max(0.01, deadline - time.monotonic()))
    except TimeoutError as exc:
        process.kill()
        process.wait()
        raise _error("DEPENDENCY_FAILED", "Git exceeded the configured time limit.", retryable=True) from exc
    except OverflowError as exc:
        process.kill()
        process.wait()
        raise _error("DEPENDENCY_FAILED", "Git output exceeded the configured limit.") from exc
    except (OSError, subprocess.TimeoutExpired) as exc:
        process.kill()
        process.wait()
        raise _error("DEPENDENCY_FAILED", "Git subprocess could not be completed safely.") from exc
    finally:
        selector.close()
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None:
                try:
                    stream.close()
                except OSError:
                    pass
    if return_code != 0:
        # Git's stderr can contain repository paths or user-provided text; keep the wire error generic.
        raise _error(error_code, "Git operation failed; verify the repository and requested revision.")
    return bytes(output)


def _repo_root(path: Path, settings: Settings) -> None:
    _validate_git_metadata(path, settings)
    top = run_git(path, ["rev-parse", "--show-toplevel"], settings=settings, output_limit=4096).decode("utf-8", "strict").strip()
    git_dir = run_git(path, ["rev-parse", "--absolute-git-dir"], settings=settings, output_limit=4096).decode("utf-8", "strict").strip()
    if Path(top).resolve() != path.resolve() or Path(git_dir).resolve() != (path / ".git").resolve():
        raise _error("POLICY_DENIED", "Repository metadata resolves outside the selected worktree.")


def _git_roots(settings: Settings) -> tuple[Path, ...]:
    return (*settings.allowed_repo_roots, *settings.staging_roots, *settings.delivery_roots)


def _scan_git_metadata_fd(metadata_fd: int, settings: Settings) -> None:
    stack: list[tuple[int, str]] = [(os.dup(metadata_fd), "")]
    visited = 0
    try:
        while stack:
            current_fd, prefix = stack.pop()
            try:
                try:
                    names = os.listdir(current_fd)
                except OSError as exc:
                    raise _error("POLICY_DENIED", "Git metadata could not be inspected safely.") from exc
                for name in names:
                    visited += 1
                    if visited > settings.max_files * 100:
                        raise _error("POLICY_DENIED", "Git metadata contains too many entries to inspect safely.")
                    relative = f"{prefix}/{name}" if prefix else name
                    if relative == "objects/info/alternates":
                        raise _error("POLICY_DENIED", "Git alternate object stores are not allowed.")
                    try:
                        info = os.stat(name, dir_fd=current_fd, follow_symlinks=False)
                    except OSError as exc:
                        raise _error("POLICY_DENIED", "Git metadata changed while it was inspected.") from exc
                    if stat.S_ISLNK(info.st_mode):
                        raise _error("POLICY_DENIED", "Git metadata cannot contain symlinks.")
                    if stat.S_ISDIR(info.st_mode):
                        stack.append((_open_child_directory(current_fd, name), relative))
                    elif not stat.S_ISREG(info.st_mode):
                        raise _error("POLICY_DENIED", "Git metadata cannot contain special files.")
                    elif info.st_nlink != 1:
                        raise _error("POLICY_DENIED", "Hard-linked Git metadata files are not allowed.")
            finally:
                os.close(current_fd)
    finally:
        for pending_fd, _ in stack:
            os.close(pending_fd)


def _open_repo_and_metadata(repo: Path, settings: Settings) -> tuple[int, int]:
    repo_fd = open_directory_beneath(repo, _git_roots(settings))
    try:
        metadata_fd = _open_child_directory(repo_fd, ".git")
    except Exception:
        os.close(repo_fd)
        raise
    return repo_fd, metadata_fd


def _assert_pinned_metadata_path(repo: Path, settings: Settings, repo_fd: int, metadata_fd: int) -> None:
    current_repo_fd = open_directory_beneath(repo, _git_roots(settings))
    try:
        pinned_repo = os.fstat(repo_fd)
        current_repo = os.fstat(current_repo_fd)
        if (pinned_repo.st_dev, pinned_repo.st_ino) != (current_repo.st_dev, current_repo.st_ino):
            raise _error("POLICY_DENIED", "Repository directory changed while Git metadata was inspected.")
        current_metadata = os.stat(".git", dir_fd=current_repo_fd, follow_symlinks=False)
        pinned_metadata = os.fstat(metadata_fd)
        if not stat.S_ISDIR(current_metadata.st_mode) or (current_metadata.st_dev, current_metadata.st_ino) != (pinned_metadata.st_dev, pinned_metadata.st_ino):
            raise _error("POLICY_DENIED", "Git metadata directory changed while it was inspected.")
    finally:
        os.close(current_repo_fd)


def _validate_git_metadata(repo: Path, settings: Settings) -> None:
    repo_fd, metadata_fd = _open_repo_and_metadata(repo, settings)
    try:
        _scan_git_metadata_fd(metadata_fd, settings)
    finally:
        os.close(metadata_fd)
        os.close(repo_fd)


def resolve_commit(repo: Path, revision: str, settings: Settings) -> str:
    if not isinstance(revision, str) or not revision or len(revision) > 256 or any(ord(ch) < 0x20 for ch in revision):
        raise _error("INVALID_INPUT", "Revision must be a non-empty Git revision string.")
    output = run_git(
        repo,
        ["rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"],
        settings=settings,
        output_limit=4096,
    )
    commit = output.decode("ascii", "strict").strip().lower()
    if not _HEX_OBJECT.fullmatch(commit):
        raise _error("INVALID_INPUT", "Git returned an invalid commit identifier.")
    return commit


def object_format(repo: Path, settings: Settings) -> str:
    value = run_git(repo, ["rev-parse", "--show-object-format"], settings=settings, output_limit=128).decode("ascii", "strict").strip()
    if value not in {"sha1", "sha256"}:
        raise _error("DEPENDENCY_FAILED", "Repository uses an unsupported Git object format.")
    return value


def list_tree(repo: Path, commit: str, settings: Settings) -> dict[str, TreeEntry]:
    raw = run_git(repo, ["ls-tree", "-rz", "--full-tree", "-r", commit], settings=settings)
    entries: dict[str, TreeEntry] = {}
    for record in raw.split(b"\x00"):
        if not record:
            continue
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode_b, kind_b, oid_b = metadata.split(b" ", 2)
            path = raw_path.decode("utf-8", "strict")
            mode = mode_b.decode("ascii")
            kind = kind_b.decode("ascii")
            oid = oid_b.decode("ascii").lower()
        except (ValueError, UnicodeDecodeError) as exc:
            raise _error("INVALID_INPUT", "Git tree contains an invalid path record.") from exc
        validate_relative_path(path)
        if kind != "blob" or mode not in {"100644", "100755"} or not _HEX_OBJECT.fullmatch(oid):
            raise _error("POLICY_DENIED", "Git tree contains a symlink, submodule or unsupported file mode.")
        if is_sensitive_path(path):
            raise _error("POLICY_DENIED", "Git tree contains a credential-like path.")
        if path in entries:
            raise _error("INVALID_INPUT", "Git tree contains duplicate paths.")
        entries[path] = TreeEntry(mode=mode, oid=oid, path=path)
    return entries


def read_blobs(repo: Path, entries: Iterable[TreeEntry], settings: Settings) -> dict[str, bytes]:
    selected = list(entries)
    if not selected:
        return {}
    object_format_name = object_format(repo, settings)
    oid_len = 40 if object_format_name == "sha1" else 64
    request = b"".join(entry.oid.encode("ascii") + b"\n" for entry in selected)
    raw = run_git(repo, ["cat-file", "--batch"], input_data=request, settings=settings)
    cursor = 0
    output: dict[str, bytes] = {}
    total = 0
    for entry in selected:
        end = raw.find(b"\n", cursor)
        if end < 0:
            raise _error("INVALID_INPUT", "Git returned a truncated object stream.")
        header = raw[cursor:end].split(b" ")
        cursor = end + 1
        if len(header) != 3 or header[0].decode("ascii", "ignore").lower() != entry.oid or header[1] != b"blob":
            raise _error("INVALID_INPUT", "Git returned an unexpected object type.")
        try:
            size = int(header[2])
        except ValueError as exc:
            raise _error("INVALID_INPUT", "Git returned an invalid object size.") from exc
        if size < 0 or size > settings.max_file_bytes or total + size > settings.max_total_bytes:
            raise _error("POLICY_DENIED", "Repository content exceeds configured size limits.")
        body_end = cursor + size
        if body_end >= len(raw) or raw[body_end:body_end + 1] != b"\n":
            raise _error("INVALID_INPUT", "Git returned a malformed object stream.")
        content = raw[cursor:body_end]
        if contains_secret(content, entry.path):
            raise _error("POLICY_DENIED", "Credential-like content is not allowed in a candidate.")
        output[entry.path] = content
        cursor = body_end + 1
        total += size
    if cursor != len(raw):
        raise _error("INVALID_INPUT", "Git returned extra object data.")
    if oid_len not in {40, 64}:
        raise _error("DEPENDENCY_FAILED", "Repository object format is unsupported.")
    return output


def _read_regular(path: Path, max_bytes: int) -> tuple[os.stat_result, bytes]:
    try:
        info = path.lstat()
    except OSError as exc:
        raise _error("POLICY_DENIED", "A workspace path could not be inspected safely.") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise _error("POLICY_DENIED", "Symlink and special files are not allowed.")
    if info.st_nlink > 1:
        raise _error("POLICY_DENIED", "Hard-linked workspace files are not allowed.")
    if info.st_size > max_bytes:
        raise _error("POLICY_DENIED", "A workspace file exceeds the configured size limit.")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
        try:
            actual = os.fstat(fd)
            if not stat.S_ISREG(actual.st_mode) or actual.st_nlink > 1 or actual.st_size > max_bytes:
                raise _error("POLICY_DENIED", "A workspace file changed while it was inspected.")
            pieces: list[bytes] = []
            remaining = max_bytes + 1
            while remaining:
                chunk = os.read(fd, min(1024 * 1024, remaining))
                if not chunk:
                    break
                pieces.append(chunk)
                remaining -= len(chunk)
            data = b"".join(pieces)
            if len(data) > max_bytes or len(data) != actual.st_size:
                raise _error("POLICY_DENIED", "A workspace file changed while it was inspected.")
            return actual, data
        finally:
            os.close(fd)
    except AdapterError:
        raise
    except OSError as exc:
        raise _error("POLICY_DENIED", "A workspace file could not be read safely.") from exc


def walk_files(root: Path, settings: Settings, *, skip_git: bool = True) -> dict[str, FileData]:
    output: dict[str, FileData] = {}
    total = 0
    entries_seen = 0
    try:
        root_device = root.stat().st_dev
    except OSError as exc:
        raise _error("POLICY_DENIED", "Workspace root could not be inspected safely.") from exc
    entry_limit = settings.max_files * 100
    stack: list[tuple[Path, str]] = [(root, "")]
    while stack:
        directory, prefix = stack.pop()
        try:
            with os.scandir(directory) as iterator:
                entries = []
                for entry in iterator:
                    entries_seen += 1
                    if entries_seen > entry_limit:
                        raise _error("POLICY_DENIED", "Workspace contains too many filesystem entries to inspect safely.")
                    entries.append(entry)
        except OSError as exc:
            raise _error("POLICY_DENIED", "Workspace directories could not be scanned safely.") from exc
        entries.sort(key=lambda item: item.name)
        for item in entries:
            if not prefix and item.name == ".git" and skip_git:
                if item.is_symlink() or not item.is_dir(follow_symlinks=False):
                    raise _error("POLICY_DENIED", "Git metadata must be a real local directory.")
                continue
            relative = f"{prefix}/{item.name}" if prefix else item.name
            validate_relative_path(relative)
            try:
                info = item.stat(follow_symlinks=False)
            except OSError as exc:
                raise _error("POLICY_DENIED", "Workspace entry could not be inspected safely.") from exc
            if stat.S_ISLNK(info.st_mode):
                raise _error("POLICY_DENIED", "Symlink files are not allowed.")
            if stat.S_ISDIR(info.st_mode):
                if info.st_dev != root_device or os.path.ismount(item.path):
                    raise _error("POLICY_DENIED", "Mounted directories are not allowed inside a repository workspace.")
                stack.append((Path(item.path), relative))
                continue
            if not stat.S_ISREG(info.st_mode):
                raise _error("POLICY_DENIED", "Special files are not allowed.")
            if info.st_dev != root_device:
                raise _error("POLICY_DENIED", "Mounted files are not allowed inside a repository workspace.")
            if is_sensitive_path(relative):
                raise _error("POLICY_DENIED", "Credential-like paths are not allowed.")
            if len(output) >= settings.max_files * 20:
                raise _error("POLICY_DENIED", "Workspace contains too many files to inspect safely.")
            file_info, data = _read_regular(Path(item.path), settings.max_file_bytes)
            total += len(data)
            if total > settings.max_total_bytes:
                raise _error("POLICY_DENIED", "Workspace exceeds the 100 MiB content limit.")
            if contains_secret(data, relative):
                raise _error("POLICY_DENIED", "Credential-like content is not allowed in a candidate.")
            mode = "100755" if file_info.st_mode & 0o111 else "100644"
            output[relative] = FileData(mode=mode, data=data)
    return output


def blob_oid(data: bytes, format_name: str) -> str:
    algorithm = hashlib.sha1 if format_name == "sha1" else hashlib.sha256
    digest = algorithm(b"blob " + str(len(data)).encode("ascii") + b"\x00" + data).hexdigest()
    return digest


def inspect_worktree(repo: Path, commit: str, settings: Settings) -> tuple[dict[str, TreeEntry], dict[str, FileData], bool]:
    _repo_root(repo, settings)
    entries = list_tree(repo, commit, settings)
    if len(entries) > settings.max_files * 20:
        raise _error("POLICY_DENIED", "Repository contains too many files to inspect safely.")
    base_blobs = read_blobs(repo, entries.values(), settings)
    actual = walk_files(repo, settings)
    fmt = object_format(repo, settings)
    clean = set(actual) == set(entries)
    if clean:
        for path, entry in entries.items():
            file = actual[path]
            if file.mode != entry.mode or blob_oid(file.data, fmt) != entry.oid:
                clean = False
                break
    # read_blobs has already checked credential-like bytes in every committed file.
    # A dirty worktree can contain an additional secret, which walk_files rejects.
    return entries, actual, clean


def ensure_safe_clone(repo: Path, settings: Settings) -> None:
    repo_fd, metadata_fd = _open_repo_and_metadata(repo, settings)
    temporary = ".sidequest-config-" + uuid.uuid4().hex
    fixed = (
        "[core]\n"
        "\trepositoryformatversion = 0\n"
        "\tfilemode = true\n"
        "\tbare = false\n"
        "\tlogallrefupdates = true\n"
    )
    try:
        _scan_git_metadata_fd(metadata_fd, settings)
        _assert_pinned_metadata_path(repo, settings, repo_fd, metadata_fd)
        try:
            original = os.stat("config", dir_fd=metadata_fd, follow_symlinks=False)
        except OSError as exc:
            raise _error("POLICY_DENIED", "Git configuration is missing or changed.") from exc
        if not stat.S_ISREG(original.st_mode) or original.st_nlink != 1:
            raise _error("POLICY_DENIED", "Git configuration must be a single-link regular file.")

        # Build a fresh inode and rename it over config. Never open an
        # attacker-controlled config inode with O_TRUNC, even after lstat.
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        _assert_pinned_metadata_path(repo, settings, repo_fd, metadata_fd)
        try:
            fd = os.open(temporary, flags, 0o600, dir_fd=metadata_fd)
        except OSError as exc:
            raise _error("POLICY_DENIED", "Safe Git configuration could not be staged.") from exc
        try:
            opened = os.fstat(fd)
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                raise _error("POLICY_DENIED", "Staged Git configuration is not a private regular file.")
            view = memoryview(fixed.encode("ascii"))
            while view:
                written = os.write(fd, view)
                view = view[written:]
            os.fsync(fd)
        finally:
            os.close(fd)

        # Refuse replacement if either the metadata directory or config entry
        # changed since the scan. The final rename is descriptor-relative and
        # cannot follow a symlink planted at the config pathname.
        _assert_pinned_metadata_path(repo, settings, repo_fd, metadata_fd)
        current_metadata = os.stat(".git", dir_fd=repo_fd, follow_symlinks=False)
        pinned_metadata = os.fstat(metadata_fd)
        current_config = os.stat("config", dir_fd=metadata_fd, follow_symlinks=False)
        if (current_metadata.st_dev, current_metadata.st_ino) != (pinned_metadata.st_dev, pinned_metadata.st_ino):
            raise _error("POLICY_DENIED", "Git metadata changed while configuration was sanitized.")
        if (
            not stat.S_ISREG(current_config.st_mode)
            or current_config.st_nlink != 1
            or (current_config.st_dev, current_config.st_ino) != (original.st_dev, original.st_ino)
        ):
            raise _error("POLICY_DENIED", "Git configuration changed while it was sanitized.")
        staged = os.stat(temporary, dir_fd=metadata_fd, follow_symlinks=False)
        if not stat.S_ISREG(staged.st_mode) or staged.st_nlink != 1 or staged.st_size != len(fixed.encode("ascii")):
            raise _error("POLICY_DENIED", "Staged Git configuration changed before installation.")
        os.replace(temporary, "config", src_dir_fd=metadata_fd, dst_dir_fd=metadata_fd)
        installed = os.stat("config", dir_fd=metadata_fd, follow_symlinks=False)
        if (
            not stat.S_ISREG(installed.st_mode)
            or installed.st_nlink != 1
            or installed.st_size != len(fixed.encode("ascii"))
            or (installed.st_dev, installed.st_ino) != (staged.st_dev, staged.st_ino)
        ):
            raise _error("POLICY_DENIED", "Sanitized Git configuration could not be verified.")
        os.fsync(metadata_fd)
    finally:
        try:
            os.unlink(temporary, dir_fd=metadata_fd)
        except OSError:
            pass
        finally:
            os.close(metadata_fd)
            os.close(repo_fd)
    _repo_root(repo, settings)


def prepare_clone(repo_path: str, revision: str, workspace_raw: str, settings: Settings) -> tuple[Path, str]:
    source = validate_repo_path(repo_path, settings.allowed_repo_roots)
    _repo_root(source, settings)
    workspace = validate_workspace_path(workspace_raw, settings.staging_roots, must_exist=False)
    try:
        workspace.relative_to(source)
        raise _error("POLICY_DENIED", "Workspace cannot be inside the source repository.")
    except ValueError:
        pass
    if workspace.exists():
        try:
            next(workspace.iterdir())
        except StopIteration:
            raise _error("POLICY_DENIED", "Workspace destination must not already exist.")
        except OSError as exc:
            raise _error("POLICY_DENIED", "Workspace destination could not be inspected safely.") from exc
        raise _error("POLICY_DENIED", "Workspace destination must not already exist.")
    commit = resolve_commit(source, revision, settings)
    head = run_git(source, ["rev-parse", "--verify", "HEAD^{commit}"], settings=settings, output_limit=4096).decode("ascii").strip().lower()
    entries, actual, clean = inspect_worktree(source, commit, settings)
    if not clean or head != commit:
        raise _error("POLICY_DENIED", "Source repository must be clean at the requested revision.")
    if sum(len(file.data) for file in actual.values()) > settings.max_total_bytes:
        raise _error("POLICY_DENIED", "Source repository exceeds the configured clone limit.")
    if workspace.name in {"", ".", ".."}:
        raise _error("POLICY_DENIED", "Workspace destination must be a named directory under staging.")
    parent_fd = open_directory_beneath(workspace.parent, settings.staging_roots, create=True)
    try:
        try:
            os.mkdir(workspace.name, mode=0o700, dir_fd=parent_fd)
        except FileExistsError as exc:
            raise _error("POLICY_DENIED", "Workspace destination must not already exist.") from exc
        except OSError as exc:
            raise _error("POLICY_DENIED", "Workspace destination could not be created safely.") from exc
        workspace_fd = _open_child_directory(parent_fd, workspace.name)
        try:
            created_workspace = os.fstat(workspace_fd)
        finally:
            os.close(workspace_fd)
    finally:
        os.close(parent_fd)
    workspace = validate_workspace_path(str(workspace), settings.staging_roots, must_exist=True)
    template = tempfile.TemporaryDirectory(prefix="sidequest-git-template-")
    try:
        clone_args = [
            "clone", "--no-hardlinks", "--local", "--no-checkout",
            "--template", template.name, "--", str(source), str(workspace),
        ]
        run_git(source, clone_args, settings=settings, timeout=max(settings.git_timeout_seconds, 60), output_limit=1024 * 1024)
        ensure_safe_clone(workspace, settings)
        # A local clone carries no useful remote for the worker. Repoint HEAD at the
        # selected immutable commit and create the index without running checkout filters.
        refs = run_git(workspace, ["for-each-ref", "--format=%(refname)"], settings=settings, output_limit=1024 * 1024).decode("ascii", "strict").splitlines()
        for ref in refs:
            if ref:
                run_git(workspace, ["update-ref", "--no-deref", "-d", ref], settings=settings, output_limit=4096)
        run_git(workspace, ["update-ref", "refs/heads/sidequest-base", commit], settings=settings, output_limit=4096)
        run_git(workspace, ["symbolic-ref", "HEAD", "refs/heads/sidequest-base"], settings=settings, output_limit=4096)
        run_git(workspace, ["read-tree", commit], settings=settings, output_limit=4096)
        for path, entry in entries.items():
            content = run_git(workspace, ["cat-file", "blob", entry.oid], settings=settings, output_limit=settings.max_file_bytes)
            target = workspace.joinpath(*path.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            fd = os.open(target, flags, 0o600)
            try:
                view = memoryview(content)
                while view:
                    written = os.write(fd, view)
                    view = view[written:]
            finally:
                os.close(fd)
            os.chmod(target, 0o755 if entry.mode == "100755" else 0o644, follow_symlinks=False)
        # Remove the clone's tracking configuration by replacing it with a fixed file.
        ensure_safe_clone(workspace, settings)
        return workspace, commit
    except Exception:
        try:
            parent_fd = open_directory_beneath(workspace.parent, settings.staging_roots)
            try:
                current = os.stat(workspace.name, dir_fd=parent_fd, follow_symlinks=False)
                if (
                    stat.S_ISDIR(current.st_mode)
                    and (current.st_dev, current.st_ino) == (created_workspace.st_dev, created_workspace.st_ino)
                ):
                    shutil.rmtree(workspace.name, ignore_errors=True, dir_fd=parent_fd)
            finally:
                os.close(parent_fd)
        except Exception:
            # An unexpected path change means cleanup is unsafe; leave the partial
            # host staging directory for explicit reconciliation.
            pass
        raise
    finally:
        template.cleanup()


def candidate_tree(
    repo: Path,
    base_commit: str,
    files: dict[str, FileData],
    settings: Settings,
) -> tuple[str, dict[str, str]]:
    ensure_safe_clone(repo, settings)
    index_path = repo / ".git" / f"sidequest-index-{uuid.uuid4().hex}"
    index_env = {"GIT_INDEX_FILE": str(index_path)}
    try:
        run_git(repo, ["read-tree", base_commit], settings=settings, extra_env=index_env, output_limit=4096)
        updates: list[bytes] = []
        object_ids: dict[str, str] = {}
        fmt = object_format(repo, settings)
        zero_oid = "0" * (40 if fmt == "sha1" else 64)
        base_entries = list_tree(repo, base_commit, settings)
        for deleted_path in sorted(set(base_entries) - set(files)):
            updates.append(b"0 " + zero_oid.encode("ascii") + b"\t" + deleted_path.encode("utf-8") + b"\x00")
        for path in sorted(files):
            file = files[path]
            oid = run_git(
                repo,
                ["hash-object", "--no-filters", "-w", "--stdin"],
                input_data=file.data,
                settings=settings,
                output_limit=256,
            ).decode("ascii", "strict").strip().lower()
            if not _HEX_OBJECT.fullmatch(oid):
                raise _error("DEPENDENCY_FAILED", "Git returned an invalid blob identifier.")
            object_ids[path] = oid
            updates.append(file.mode.encode("ascii") + b" " + oid.encode("ascii") + b"\t" + path.encode("utf-8") + b"\x00")
        run_git(repo, ["update-index", "-z", "--index-info"], input_data=b"".join(updates), settings=settings, extra_env=index_env)
        tree = run_git(repo, ["write-tree"], settings=settings, extra_env=index_env, output_limit=256).decode("ascii", "strict").strip().lower()
        if not _HEX_OBJECT.fullmatch(tree):
            raise _error("DEPENDENCY_FAILED", "Git returned an invalid tree identifier.")
        return tree, object_ids
    finally:
        try:
            index_path.unlink()
        except FileNotFoundError:
            pass


def create_candidate_commit(repo: Path, tree: str, base_commit: str, settings: Settings) -> str:
    env = {
        "GIT_AUTHOR_NAME": "Sidequest Candidate",
        "GIT_AUTHOR_EMAIL": "sidequest-local@invalid",
        "GIT_COMMITTER_NAME": "Sidequest Candidate",
        "GIT_COMMITTER_EMAIL": "sidequest-local@invalid",
        "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+0000",
        "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+0000",
    }
    commit = run_git(
        repo,
        ["commit-tree", tree, "-p", base_commit],
        input_data=b"Sidequest frozen candidate\n",
        settings=settings,
        extra_env=env,
        output_limit=256,
    ).decode("ascii", "strict").strip().lower()
    if not _HEX_OBJECT.fullmatch(commit):
        raise _error("DEPENDENCY_FAILED", "Git returned an invalid candidate identifier.")
    ref = f"refs/sidequest/candidates/{uuid.uuid4().hex}"
    run_git(repo, ["update-ref", ref, commit], settings=settings, output_limit=4096)
    return commit


def git_diff(repo: Path, base_commit: str, candidate_commit: str, settings: Settings, *, binary: bool) -> bytes:
    args = ["diff", "--patch", "--no-ext-diff", "--no-textconv", "--no-color", "--find-renames", "--full-index"]
    if binary:
        args.append("--binary")
    args.extend([base_commit, candidate_commit, "--"])
    return run_git(repo, args, settings=settings)


def changed_names(repo: Path, base_commit: str, candidate_commit: str, settings: Settings) -> list[tuple[str, str, str | None]]:
    raw = run_git(repo, ["diff", "--name-status", "-z", "--find-renames", base_commit, candidate_commit, "--"], settings=settings)
    parts = raw.split(b"\x00")
    if parts and parts[-1] == b"":
        parts.pop()
    result: list[tuple[str, str, str | None]] = []
    index = 0
    while index < len(parts):
        try:
            status = parts[index].decode("ascii")
            index += 1
            if status.startswith("R") or status.startswith("C"):
                old = parts[index].decode("utf-8", "strict")
                new = parts[index + 1].decode("utf-8", "strict")
                index += 2
                result.append((status[0], new, old))
            else:
                path = parts[index].decode("utf-8", "strict")
                index += 1
                result.append((status[0], path, None))
        except (IndexError, UnicodeDecodeError, ValueError) as exc:
            raise _error("INVALID_INPUT", "Git returned malformed changed-path data.") from exc
    for kind, path, old in result:
        validate_relative_path(path)
        if old is not None:
            validate_relative_path(old)
    return result


def numstat(repo: Path, base_commit: str, candidate_commit: str, settings: Settings) -> dict[str, tuple[int, int]]:
    raw = run_git(repo, ["diff", "--numstat", "-z", "--find-renames", base_commit, candidate_commit, "--"], settings=settings)
    parts = raw.split(b"\x00")
    if parts and parts[-1] == b"":
        parts.pop()
    result: dict[str, tuple[int, int]] = {}
    index = 0
    while index < len(parts):
        fields = parts[index].split(b"\t", 2)
        index += 1
        if len(fields) != 3:
            raise _error("INVALID_INPUT", "Git returned malformed diff statistics.")
        added = 0 if fields[0] == b"-" else int(fields[0])
        deleted = 0 if fields[1] == b"-" else int(fields[1])
        if fields[2]:
            path = fields[2].decode("utf-8", "strict")
        else:
            if index + 1 >= len(parts):
                raise _error("INVALID_INPUT", "Git returned malformed rename statistics.")
            _old = parts[index].decode("utf-8", "strict")
            path = parts[index + 1].decode("utf-8", "strict")
            index += 2
        result[path] = (added, deleted)
    return result
