---
name: drydock
description: Drives a software product from idea to merged, reviewed and deployed code through gated phases. Use when the user runs /drydock or $drydock, or asks to continue the drydock flow in a repository.
argument-hint: "[status]"
disable-model-invocation: true
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/bin/drydock.py status*)
---

# Drydock

State: !`python3 ${CLAUDE_SKILL_DIR}/bin/drydock.py status --soft`

If the State line still shows the command instead of its output, run it yourself:
`python3 <directory of this file>/bin/drydock.py status --soft`.

`drydock.py <command>`, here and in every phase file, means
`python3 <directory of this file>/bin/drydock.py <command>` run from inside the product repository.

## Rules

1. State says `not initialized`: explain that `drydock.py init` creates `.drydock/` and adds permission rules to `.claude/settings.json` in this repository, run it only after the user agrees, then stop.
2. Read exactly one phase file: `phases/<n>-<phase>.md` for the phase in State (1 requirements, 2 architecture, 3 audit, 4 prepare, 5 specs, 6 blocks, 7 build, 8 review). Also read `adapters/claude.md`. Never read another phase to get ahead.
3. Follow that phase file step by step. Its Gate section is the only definition of done.
4. A gate closes only with `drydock.py gate pass <phase>`, after its condition holds. The user approves that command. Never rephrase a command to avoid an approval prompt, and never edit `.drydock/state.json` or `.drydock/local/` by hand. If the command is denied without a prompt, stop and ask the user to run it themselves.
5. Argument `status`: print State and stop.
6. Phase `closed`: say the project is closed and stop.
7. When a CLI command fails, show its message and fix the cause. Do not skip the step.
