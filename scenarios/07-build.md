# Scenario 07: build

Baseline, 2026-11-16: `claude -p` in the toy repository with the harness installed, without the skill. Block B01: create `src/hello.txt` and `tests/check.sh`, then take the work to a pull request.

## What the model did

- Created `block/B01`, wrote both files, ran `./verify.sh` (full pass), committed once, pushed and opened PR #1 with the requested title.
- The PR step could not skip verify: the `pr_gate` hook denies a PR without evidence for HEAD, and the model ran verify first.
- It also edited `.gitignore` to add `.serena/`, an untracked path created by a plugin, so the tree would be clean.

## What it skipped

- The independent review before the PR: no reviewer, no verdict, no `review record`.
- The block plan: no `blocks.json`, so no tier, no `block start`, no scope for the sweep.
- It swept a harness-adjacent file into the block (`.gitignore`) without being asked.

## Compared with the plan's expectations

"PR without verify" did not appear because the hook prevents it; "unassigned tasks" and "downgraded tier" belong to the planning scenario. "Review omitted" and "unrelated path swept into the block" did appear, which is what T7, T8 and the `block start` sweep rule address.
