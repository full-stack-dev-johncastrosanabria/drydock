# Learnings

| Date | Observed failure | Change made |
|---|---|---|
| 2026-11-16 | H0 acceptance: in `dontAsk`, Claude Code denied `Read` (and `cat` through Bash) on the skill's own files, so the phase file never loaded. Adding `Read(${CLAUDE_SKILL_DIR}/**)` to `allowed-tools` did not help. | The router injects the phase file and the adapter through `status --soft --phase`; rule 2 of `SKILL.md` reads them by hand only if the injection did not run. |
