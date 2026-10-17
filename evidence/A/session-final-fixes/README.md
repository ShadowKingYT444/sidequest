# Final transport review repairs

Read-only review of frozen80598b4 identified two independently reproducible defects. `red-review.log` preserves failure to restore a directory replaced by a file and a receipt stranded queued after readiness expired before claim.

Restoration now validates every path/scope first, applies verified deletions before writes, and prunes only empty directories inside scope. Nonempty unverified contents and symlinks remain rejected. `red-nested-directory.log` preserves the nested empty-directory case before that additional correction.

Known undispatched intents become rejected after pre-claim failure, restore the exact previous verifying/accepted parent state, preserve recorded input/attachments, and allow explicit new intent after fresh readiness. Dispatching/uncertain messages remain protected from replay. Migration006 retains previous jobstate and supports upgrades from005; the schema-version assertion moves to6 accordingly.

`runtime-green.log`:65/65 runtime tests pass. Command: `/workspace/sidequest/.venv/bin/python -m unittest discover -s services/runtime/tests -p 'test_*.py' -v`; targeted regressions run before repair; `git diff --check` passes. Protocol/store/filesystem fakes only, no live model/provider calls. The root frozen browser run was untouched while these fixes were developed in an isolated worktree.
