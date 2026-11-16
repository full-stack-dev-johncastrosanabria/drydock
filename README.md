# Drydock

Drydock is a Claude Code skill (`/drydock`) backed by a Python CLI. It drives a software product from idea to merged, reviewed and deployed code through eight gated phases: requirements, architecture, audit, prepare, specs, blocks, build and review.

## Install

Link the repository into the skills directory. The path must not contain spaces.

```
ln -s "$HOME/Developer/drydock" "$HOME/.claude/skills/drydock"
```

The CLI needs Python 3.9 or newer and nothing outside the standard library.

## Commands

Run `python3 bin/drydock.py <command>`. Exit codes: 0 ok, 1 rejected or failed check, 2 environment (not a git repository, not initialized, unreadable state). Errors go to stderr as `error: <message>`.

| Command | Effect | Exit |
|---|---|---|
| `init` | Creates `.drydock/state.json` and `routing.json`, adds `.drydock/local/` to `.gitignore`, generates `PROJECT_STATE.md`; from T5 it also merges the `permissions` rules into `.claude/settings.json` | 0 · 1 already initialized · 2 not a git repository |
| `status [--soft]` | Phase, slice, block and next action. `--soft` always exits 0 | 0 · 2 |
| `gate pass <phase> [--note T] [--next specs\|review]` | Runs the phase's automatic check if there is one, closes the gate and advances. `--next` is required in `build`; from H5, optional in `review` (`--next specs`) | 0 · 1 |
| `slice set <id>` | Sets the slice; only in `specs` and only if `specs/<id>/` exists | 0 · 1 |
| `render-state` | Regenerates `PROJECT_STATE.md` (every state-changing command does this too) | 0 |
| `harness install --stack <s> [--force]` | Copies the harness and merges `.claude/settings.json`. Does not require `init` | 0 · 1 |
| `doctor` | Harness, hook, permissions, agents, environment variables | 0 with or without warnings · 1 with errors |
| `blocks validate` | Validates `blocks.json` against `tasks.md` and `routing.json` | 0 · 1 listing all errors |
| `agents render` | Writes `.claude/agents/drydock-*.md` | 0 · 1 |
| `block start <id>` | Validates the plan, creates `block/<id>` from the base and commits pending changes that fall under `SWEEP_PATHS` | 0 · 1 |
| `block close <id> [--merged-sha S] [--attempts N] [--findings N]` | Checks that the merge is on the base, returns to it, marks the block `done`, adds metrics. `--merged-sha` only applies without an `origin` remote | 0 · 1 |
| `block merge <id> [--attempts N] [--findings N]` | T1 only: checks that the `verify` check is green, squash-merges and closes | 0 · 1 |
| `block pr-body <id>` | Prints the PR body | 0 · 1 |
| `review record <id> --sha <sha>` | Stores the reviewer text read from stdin | 0 · 1 |
| `deploy` (H5) | Verify, deploy and smoke test; writes deploy evidence | 0 · 1 · 2 |
| `clean-clone` (H5) | Clones to a temporary directory and runs `./verify.sh` | verify's exit code |

## Recovery

If every Bash call is blocked, the PR-gate hook is failing. Run `python3 .drydock/bin/pr_gate.py < /dev/null` in a terminal to see the error.
