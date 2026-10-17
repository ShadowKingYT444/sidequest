"""Sidequest local runtime entry point."""

from __future__ import annotations

import argparse
from dataclasses import replace
import os
from pathlib import Path
import secrets
import stat
import sys

import uvicorn

from .api import create_app
from .config import RuntimeConfig, runtime_config_from_env


def _is_git_metadata(path: Path) -> bool:
    marker = path / ".git"
    if marker.is_dir():
        return (marker / "HEAD").is_file() and (marker / "objects").is_dir()
    if marker.is_file():
        try:
            return marker.read_text(encoding="utf-8", errors="strict").startswith("gitdir: ")
        except (OSError, UnicodeDecodeError):
            return False
    return False


def _secure_directory(path: Path) -> Path:
    path = path.expanduser()
    resolved = path.resolve(strict=False)
    home = Path.home().resolve()
    if resolved in {Path("/"), Path("/tmp"), Path("/var/tmp"), Path("/workspace"), home}:
        raise RuntimeError(f"runtime data path must be a dedicated private directory: {path}")
    cursor = resolved
    while cursor != cursor.parent:
        if _is_git_metadata(cursor):
            raise RuntimeError("runtime data and token files must stay outside Git repositories")
        cursor = cursor.parent
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink() or not path.is_dir():
        raise RuntimeError(f"runtime directory is not a regular directory: {path}")
    os.chmod(path, 0o700)
    return path.resolve(strict=True)


def _read_token_file(path: Path) -> str:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 512 or info.st_mode & 0o077:
            raise RuntimeError("local session token file must be a private, single-link regular file")
        chunks = bytearray()
        while len(chunks) <= 512:
            part = os.read(fd, 513 - len(chunks))
            if not part:
                break
            chunks.extend(part)
        if len(chunks) > 512:
            raise RuntimeError("local session token file exceeds 512 bytes")
    finally:
        os.close(fd)
    try:
        token = bytes(chunks).decode("ascii", "strict").strip()
    except UnicodeDecodeError:
        raise RuntimeError("local session token must be ASCII") from None
    if not 32 <= len(token) <= 512 or any(ch in token for ch in "\r\n\x00"):
        raise RuntimeError("local session token must contain 32 to 512 safe characters")
    return token


def load_or_create_token(config: RuntimeConfig, environ: dict[str, str] | None = None) -> tuple[str, Path | None]:
    env = os.environ if environ is None else environ
    token = env.get("SIDEQUEST_API_TOKEN")
    if token is not None:
        if not 32 <= len(token) <= 512 or any(ch in token for ch in "\r\n\x00"):
            raise RuntimeError("SIDEQUEST_API_TOKEN must contain 32 to 512 safe characters")
        return token, None
    token_path = config.token_file or (config.config_dir / "session.token")
    token_parent = token_path.parent.expanduser()
    token_parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if token_parent.is_symlink() or not token_parent.is_dir() or token_parent.stat().st_mode & 0o077:
        raise RuntimeError("local session token directory must be private and cannot be a symlink")
    cursor = token_parent.resolve(strict=True)
    while cursor != cursor.parent:
        if _is_git_metadata(cursor):
            raise RuntimeError("runtime data and token files must stay outside Git repositories")
        cursor = cursor.parent
    try:
        return _read_token_file(token_path), token_path
    except FileNotFoundError:
        pass
    except OSError:
        raise RuntimeError("local session token file could not be opened safely") from None
    token = secrets.token_urlsafe(48)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(token_path, flags, 0o600)
    except FileExistsError:
        try:
            return _read_token_file(token_path), token_path
        except OSError:
            raise RuntimeError("local session token file could not be opened safely") from None
    try:
        with os.fdopen(fd, "w", encoding="ascii") as stream:
            stream.write(token + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            token_path.unlink()
        except OSError:
            pass
        raise
    os.chmod(token_path, 0o600, follow_symlinks=False)
    return token, token_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m services.runtime.main",
        description="Run the authenticated Sidequest runtime on loopback.",
    )
    parser.add_argument("--data-dir", type=Path, help="private runtime data directory (or SIDEQUEST_DATA_DIR)")
    parser.add_argument("--config-dir", type=Path, help="private configuration directory (or SIDEQUEST_CONFIG_DIR)")
    parser.add_argument("--runtime-dir", type=Path, help="private temporary runtime directory (or SIDEQUEST_RUNTIME_DIR)")
    parser.add_argument("--token-file", type=Path, help="private local API token file")
    parser.add_argument("--allowed-root", action="append", type=Path, help="approved repository root; repeat as needed")
    parser.add_argument("--port", type=int, help="loopback HTTP port (or SIDEQUEST_PORT)")
    parser.add_argument("--max-parallel", type=int, help="worker limit from 1 to 4 (or SIDEQUEST_MAX_PARALLEL)")
    parser.add_argument("--b-argv", help="JSON argv array for the B adapter (or SIDEQUEST_B_ARGV)")
    parser.add_argument("--d-argv", help="JSON argv array for the D adapter (or SIDEQUEST_D_ARGV)")
    parser.add_argument("--adapter-timeout-seconds", type=float, help="B/D adapter timeout")
    return parser


def _resolved_config(args: argparse.Namespace) -> RuntimeConfig:
    config = runtime_config_from_env()
    changes: dict[str, object] = {}
    for arg, field in (
        ("data_dir", "data_dir"),
        ("config_dir", "config_dir"),
        ("runtime_dir", "runtime_dir"),
        ("token_file", "token_file"),
        ("port", "bind_port"),
        ("max_parallel", "max_parallel"),
        ("adapter_timeout_seconds", "adapter_timeout_seconds"),
    ):
        value = getattr(args, arg)
        if value is not None:
            changes[field] = value
    if args.allowed_root is not None:
        changes["allowed_roots"] = tuple(args.allowed_root)
    if args.config_dir is not None and args.token_file is None and not os.environ.get("SIDEQUEST_API_TOKEN_FILE"):
        changes["token_file"] = args.config_dir.expanduser() / "session.token"
    if args.b_argv is not None:
        import json
        value = json.loads(args.b_argv)
        if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
            raise ValueError("--b-argv must be a JSON string array")
        changes["b_argv"] = tuple(value)
    if args.d_argv is not None:
        import json
        value = json.loads(args.d_argv)
        if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
            raise ValueError("--d-argv must be a JSON string array")
        changes["d_argv"] = tuple(value)
    return replace(config, **changes)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = _resolved_config(args)
    _secure_directory(config.data_dir)
    _secure_directory(config.runtime_dir)
    _secure_directory(config.config_dir)
    token, _token_path = load_or_create_token(config)
    app = create_app(config, token=token)
    try:
        os.chmod(config.database_path, 0o600, follow_symlinks=False)
    except FileNotFoundError:
        pass
    uvicorn.run(
        app,
        host=config.bind_host,
        port=config.bind_port,
        access_log=False,
        log_level="info",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
