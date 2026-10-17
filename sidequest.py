#!/usr/bin/env python3
"""Install and run the local Sidequest office; no provider login or model calls."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import http.client
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
DESKTOP = ROOT / "desktop"
PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


class SetupError(Exception):
    pass


def command(argv: list[str], **kwargs) -> subprocess.CompletedProcess:
    kwargs.setdefault("cwd", ROOT)
    return subprocess.run(argv, check=True, **kwargs)


def prerequisites() -> None:
    if sys.version_info < (3, 12):
        raise SetupError("Python 3.12 or newer is required.")
    for name in ("git", "node", "npm"):
        if not shutil.which(name):
            raise SetupError(f"Install {name} and reopen your terminal, then run setup again.")
    version = command(["node", "--version"], capture_output=True, text=True).stdout.strip()
    if not version.startswith("v24."):
        raise SetupError("Use Node.js 24 LTS (with npm), then run setup again.")
    if os.name == "nt":
        raise SetupError("The Python runtime currently requires Linux or macOS; native Windows is not supported.")


def electron_executable() -> Path:
    try:
        result = command(["node", "-e", "process.stdout.write(require('electron'))"],
                         cwd=DESKTOP, capture_output=True, text=True)
        executable = Path(result.stdout)
        if executable.is_file():
            return executable
    except (OSError, subprocess.CalledProcessError):
        pass
    raise SetupError("Electron is not installed. Run python3 sidequest.py setup.")


def build_fingerprint() -> str:
    digest = hashlib.sha256()
    paths = [DESKTOP / name for name in ("package.json", "package-lock.json", "index.html", "tsconfig.json", "vite.config.ts")]
    paths += sorted((DESKTOP / "src").rglob("*"))
    for path in paths:
        if path.is_file():
            digest.update(str(path.relative_to(DESKTOP)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def ensure_build() -> None:
    marker = DESKTOP / "dist" / ".sidequest-build"
    fingerprint = build_fingerprint()
    if not (DESKTOP / "dist/index.html").is_file() or not marker.is_file() or marker.read_text() != fingerprint:
        command(["npm", "--prefix", str(DESKTOP), "run", "build"])
        marker.write_text(fingerprint)


def setup(browser: bool) -> None:
    prerequisites()
    cache = ROOT / ".sidequest" / "cache"
    env = {**os.environ,
           "PIP_CACHE_DIR": os.environ.get("PIP_CACHE_DIR", str(cache / "pip")),
           "npm_config_cache": os.environ.get("npm_config_cache", str(cache / "npm")),
           "electron_config_cache": os.environ.get("electron_config_cache", str(cache / "electron"))}
    command([sys.executable, "-m", "venv", str(ROOT / ".venv")])
    command([str(PYTHON), "-m", "pip", "install", "-r", "services/runtime/requirements.lock",
             "-r", "services/workshops/requirements.lock"], env=env)
    command(["npm", "--prefix", str(DESKTOP), "ci"], env=env)
    if not browser:
        command(["npm", "--prefix", str(DESKTOP), "run", "install:electron"], env=env)
    ensure_build()
    print("Setup complete. Start with: python3 sidequest.py run --repo /path/to/your/project" +
          (" --browser" if browser else ""), flush=True)


def git(repo: Path, *args: str) -> str:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_OPTIONAL_LOCKS="0",
               GIT_TERMINAL_PROMPT="0", GIT_NO_REPLACE_OBJECTS="1")
    try:
        return command(["git", "-c", f"core.hooksPath={os.devnull}", "-c", "core.fsmonitor=false",
                        "-C", str(repo), *args], env=env, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        raise SetupError("Choose a local Git repository with at least one commit and a valid --base revision.") from None


def project(repo: Path, base: str | None) -> tuple[Path, str]:
    repo = repo.expanduser().resolve()
    root = Path(git(repo, "rev-parse", "--show-toplevel"))
    git(root, "rev-parse", "--verify", "HEAD^{commit}")
    if base is None:
        try:
            base = git(root, "rev-parse", "--verify", "HEAD~1^{commit}")
        except SetupError:
            base = "HEAD"  # A new one-commit repository has a valid empty comparison.
    if not base or base.startswith("-") or len(base) > 256:
        raise SetupError("--base must name a Git commit.")
    return root, git(root, "rev-parse", "--verify", "--end-of-options", base + "^{commit}")


def default_state() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/Sidequest"
    return Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "sidequest"


def state_directory(value: Path) -> Path:
    value = value.expanduser().resolve()
    if value in {Path("/"), Path("/tmp"), Path("/var/tmp"), Path("/workspace"), Path.home().resolve()}:
        raise SetupError("--state-dir must be a dedicated directory outside Git repositories.")
    for parent in (value, *value.parents):
        marker = parent / ".git"
        if marker.is_file() or (marker / "HEAD").is_file():
            raise SetupError("--state-dir must be outside Git repositories.")
    return value


@contextmanager
def state_lock(state: Path):
    import fcntl
    import stat
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(state / "launcher.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_mode & 0o077:
            raise SetupError("The launcher lock must be a private, single-link regular file.")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SetupError("Sidequest is already running with this state directory. Close it first or choose another --state-dir.") from None
        yield
    finally:
        os.close(fd)


def runtime_environment(state: Path, repo: Path, base: str, port: int, token: str) -> dict[str, str]:
    # Scope this supervised runtime ourselves. Inherited adapter/auth overrides must
    # not silently change its authority or persist the ephemeral local API token.
    env = {key: value for key, value in os.environ.items() if not key.startswith("SIDEQUEST_")}
    env.update(SIDEQUEST_API_TOKEN=token, SIDEQUEST_RUNTIME_TOKEN=token,
               SIDEQUEST_RUNTIME_URL=f"http://127.0.0.1:{port}",
               SIDEQUEST_REPO=str(repo), SIDEQUEST_BASE=base, SIDEQUEST_PROJECT_BASE="HEAD",
               SIDEQUEST_DATA_DIR=str(state / "data"), SIDEQUEST_CONFIG_DIR=str(state / "config"),
               SIDEQUEST_RUNTIME_DIR=str(state / "runtime"), SIDEQUEST_CODEX_ENABLED="false",
               SIDEQUEST_CODEX_CONSENT="false", PYTHONUNBUFFERED="1")
    # Metadata-only executable locators are useful to Settings; they grant no execution.
    for key, value in os.environ.items():
        if key.startswith("SIDEQUEST_") and key.endswith("_EXECUTABLE"):
            env[key] = value
    return env


def wait_for_runtime(child: subprocess.Popen, port: int, token: str, timeout: float = 20) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if child.poll() is not None:
            raise SetupError("The local runtime stopped during startup. Review the error above and run doctor.")
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=0.5)
        try:
            connection.request("GET", "/v1/capabilities", headers={"Authorization": f"Bearer {token}"})
            response = connection.getresponse()
            payload = json.loads(response.read(1024 * 1024))
            if response.status == 200 and payload.get("v") == 1 and payload.get("features", {}).get("local_git_inspection") is True:
                return
        except (OSError, ValueError, http.client.HTTPException):
            pass
        finally:
            connection.close()
        time.sleep(0.1)
    raise SetupError("The local runtime did not become ready within 20 seconds. Review its startup error above.")


def stop(child: subprocess.Popen | None) -> None:
    if child is None:
        return
    # The launcher owns these process groups, including Vite/npm and check workers.
    try:
        os.killpg(child.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        child.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    child.wait()


def doctor(browser: bool) -> bool:
    checks = []
    try:
        prerequisites()
        checks.append((True, "Python, Node 24, npm and Git"))
    except SetupError as error:
        checks.append((False, str(error)))
    installed = PYTHON.is_file() and subprocess.run(
        [str(PYTHON), "-c", "import fastapi, uvicorn, httpx, playwright"],
        capture_output=True, cwd=ROOT).returncode == 0
    checks.append((bool(installed), "Python dependencies (repair: python3 sidequest.py setup)"))
    checks.append(((DESKTOP / "node_modules/vite/package.json").is_file(), "Desktop dependencies (repair: setup)"))
    checks.append(((DESKTOP / "public/office/office.glb").is_file(), "Original office assets"))
    if not browser:
        try:
            electron_executable()
            checks.append((True, "Electron executable installed; sandbox availability requires a native launch"))
        except SetupError as error:
            checks.append((False, str(error)))
        checks.append((sys.platform != "linux" or bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")),
                       "Desktop display (headless hosts can use run --browser)"))
    for ok, message in checks:
        print(f"{'OK' if ok else 'MISSING'}  {message}")
    print("Agent execution: unavailable until the provider can enforce the required spending ceiling. "
          "Installed CLIs do not establish a connected session.")
    return all(ok for ok, _ in checks)


def run(args: argparse.Namespace) -> int:
    prerequisites()
    if not PYTHON.is_file() or not (DESKTOP / "node_modules/vite/package.json").is_file():
        raise SetupError("Dependencies are missing. Run python3 sidequest.py setup first.")
    repo, base = project(args.repo, args.base)
    state = state_directory(args.state_dir or default_state())
    if not args.browser and sys.platform == "linux" and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        raise SetupError("No desktop display is available. Run on your desktop, or add --browser for the local browser UI.")
    if args.browser:
        ui_argv = ["npm", "--prefix", str(DESKTOP), "run", "dev"]
    else:
        executable = electron_executable()
        ensure_build()
        ui_argv = [str(executable), str(DESKTOP)]
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    env = runtime_environment(state, repo, base, port, secrets.token_urlsafe(48))
    runtime = ui = None
    def interrupted(_signum, _frame):
        raise KeyboardInterrupt
    old_handlers = {sig: signal.signal(sig, interrupted) for sig in (signal.SIGINT, signal.SIGTERM)}
    lock = state_lock(state)
    locked = False
    try:
        lock.__enter__()
        locked = True
        runtime = subprocess.Popen([str(PYTHON), "-m", "services.runtime.main", "--allowed-root", str(repo),
                                    "--port", str(port)], cwd=ROOT, env=env, start_new_session=True)
        wait_for_runtime(runtime, port, env["SIDEQUEST_API_TOKEN"])
        print("Local runtime ready. Git inspection, saved sessions and artifacts are connected. "
              "Coding is disabled; no provider turn will start.", flush=True)
        ui = subprocess.Popen(ui_argv, cwd=DESKTOP, env=env, start_new_session=True)
        if args.browser:
            print("Open http://127.0.0.1:5173 after Vite reports ready. Press Ctrl+C to stop both services.", flush=True)
        while ui.poll() is None:
            if runtime.poll() is not None:
                raise SetupError("The local runtime stopped. The office has been closed; review the runtime error above.")
            time.sleep(0.2)
        code = ui.returncode
        if code:
            raise SetupError("The office could not run. Review the error above; run doctor. "
                             "Electron needs a supported desktop sandbox. Do not disable it; use --browser on headless hosts.")
        return 0
    except KeyboardInterrupt:
        return 130
    finally:
        # Do not interrupt cleanup a second time and leave a service behind.
        for sig in old_handlers:
            signal.signal(sig, signal.SIG_IGN)
        stop(ui)
        stop(runtime)
        if locked:
            lock.__exit__(None, None, None)
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("setup", "doctor", "run"):
        sub = commands.add_parser(name)
        sub.add_argument("--browser", action="store_true", help="use the loopback browser UI; no Electron/display required")
        if name == "run":
            sub.add_argument("--repo", type=Path, required=True, help="trusted local Git project with at least one commit")
            sub.add_argument("--base", help="comparison commit; defaults to the previous commit, or HEAD for a new repo")
            sub.add_argument("--state-dir", type=Path, help="dedicated private data directory outside Git")
    args = parser.parse_args(argv)
    try:
        if args.command == "setup":
            setup(args.browser)
            return 0
        if args.command == "doctor":
            return 0 if doctor(args.browser) else 1
        return run(args)
    except (SetupError, OSError, subprocess.CalledProcessError) as error:
        # Child command stderr is already displayed. Never dump its environment.
        message = str(error) if isinstance(error, SetupError) else "A setup/start command failed. Review its output above; run python3 sidequest.py doctor."
        print(f"Sidequest: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
