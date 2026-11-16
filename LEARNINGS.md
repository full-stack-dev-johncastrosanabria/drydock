# Learnings

| Date | Observed failure | Change made |
|---|---|---|
| 2026-11-16 | H0 acceptance: in `dontAsk`, Claude Code denied `Read` (and `cat` through Bash) on the skill's own files, so the phase file never loaded. Adding `Read(${CLAUDE_SKILL_DIR}/**)` to `allowed-tools` did not help. | The router injects the phase file and the adapter through `status --soft --phase`; rule 2 of `SKILL.md` reads them by hand only if the injection did not run. |
| 2026-11-16 | Interactive H0 acceptance: in `dontAsk` the agent cannot run `drydock.py init` (no allow rule exists before `init` runs) and cannot write phase artifacts (`Write` is denied). | None yet. The user runs `init` once per repository, and phases that write files need `default` or `acceptEdits`. Step 0 of H1 rechecks it. |
| 2026-11-16 | Opening a session in the test repository created an untracked `.serena/` (the user's Serena plugin). `block start` would refuse it as an unexpected pending path. | None yet. Decide before H2: a global gitignore, or a line added by `init`. |
| 2026-11-16 | `red-first` failed open on non-ASCII paths: `git diff-tree --name-only` C-quotes them (`"src/caf\303\251.cs"`), so neither `src_globs` nor `test_globs` matched. The bug was in the plan's algorithm, not the implementer. | `-c core.quotePath=false` on every git path listing that feeds a match (`verify.py` now, plus `block start` and `block merge` in the plan). |
