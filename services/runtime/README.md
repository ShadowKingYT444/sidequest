# Sidequest runtime

The local runtime owns SQLite state and serves the computer API on `127.0.0.1:4317`. Run it from the repository root with Python 3.11 or newer:

```sh
python3 -m services.runtime.main --help
python3 -m services.runtime.main --allowed-root /absolute/path/to/approved/repos
```

The runtime creates a private data directory at `~/.local/share/sidequest`, a private configuration directory at `~/.config/sidequest`, and a temporary work directory under `$XDG_RUNTIME_DIR/sidequest` or `/tmp/sidequest-<uid>`. Paths must be dedicated directories outside Git repositories. Pass `--data-dir`, `--config-dir`, and `--runtime-dir`, or set `SIDEQUEST_DATA_DIR`, `SIDEQUEST_CONFIG_DIR`, and `SIDEQUEST_RUNTIME_DIR` to override them.

The host session token is generated once at `~/.config/sidequest/session.token` with mode `0600`. Set `SIDEQUEST_API_TOKEN_FILE` or pass `--token-file` to choose another private file. `SIDEQUEST_API_TOKEN` can supply a host-managed secret instead of a file. Keep either form in the host process or Electron main process; never place it in renderer code, Git, job text, or artifacts. All `/v1` routes require `Authorization: Bearer <token>`; `/health` is the only public route. CORS is disabled.

Set `SIDEQUEST_ALLOWED_ROOTS` to a path-separated list of approved repository roots, or repeat `--allowed-root`. The runtime advertises `features.local_git_inspection=true` only when an approved root and both adapter commands are configured. B and D default to `python -m services.tools.main` and `python -m services.workshops.main`. `SIDEQUEST_B_ARGV` and `SIDEQUEST_D_ARGV` accept JSON string arrays to override those commands; the runtime executes them without a shell and gives each a scrubbed environment. `SIDEQUEST_PORT`, `SIDEQUEST_MAX_PARALLEL` (1–4), and `SIDEQUEST_ADAPTER_TIMEOUT_SECONDS` configure the listener and bounded worker settings. The listener always binds to loopback.

The A2 worker profile is the deterministic `local_git_inspection` path. It reads a clean registered Git revision through B, imports and rechecks immutable candidate files, then asks D to verify the exact frozen manifest. It has a zero-dollar budget and reports zero inference calls. Coding, provider dispatch, external delivery, screen watching, and workshop activation are unavailable in this profile.

The computer API includes authenticated capabilities and snapshot reads; project/job commands; job, run, and event status; paginated job artifacts and frozen manifest files; bounded UTF-8 text and Git diff pages; exact artifact content as an inert attachment; and an empty watcher list. Opaque HMAC cursors are tied to their job or artifact identity. Text and diff pages are capped at 200 rows and 256 KiB. Artifacts are served only after the runtime verifies their registered digest; no route accepts an arbitrary filesystem path.
