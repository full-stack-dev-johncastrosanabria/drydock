# Scenario 00: router

Checks that `/drydock` reads the state and loads only what the state calls for. There is no baseline: without the skill there is no router to compare against.

## Setup

A temporary git repository with the skill linked (see the README). Per case:

- (a) a repository where `init` has not run;
- (b) a repository where `init` has run, so the phase is `requirements`;
- (c) the same repository as (b).

## Prompt

- (a) `/drydock`
- (b) `/drydock`
- (c) `/drydock status`

Unattended: `claude -p "/drydock" --permission-mode dontAsk --output-format json`, run inside the temporary repository.

## Pass criteria

- (a) It proposes `drydock.py init`, says what `init` creates, and changes nothing else.
- (b) It follows `phases/1-requirements.md` (injected in the Phase section) and reads no other phase file.
- (c) It prints the State line and stops.

## Log

| Date | Case | Result | Notes |
|---|---|---|---|
| 2026-11-16 | (a) | pass | `claude` 2.1.325, `claude -p "/drydock" --permission-mode dontAsk`. State was injected with no denial and no tool call; it proposed `init` and changed nothing. `${CLAUDE_SKILL_DIR}` resolved to the link (`<config dir>/skills/drydock`), not to its target. |
| 2026-11-16 | (b) | fail | Same command after `init`. It tried only `phases/1-requirements.md` and `adapters/claude.md`, but `dontAsk` denied `Read` (and `cat` through Bash) on the skill's own files, so the phase never loaded. `allowed-tools` covers only `status`. |
| 2026-11-16 | (c) | pass | `claude -p "/drydock status" --permission-mode dontAsk`: printed the four state lines and stopped; one turn, no tool call. |
| 2026-11-16 | gate in `dontAsk` | partial | Asked to close the requirements gate: it did not run or rephrase `gate pass`, stopped and asked the user to run it. It never reached the command itself: the phase-file read was denied first, as in (b). |
| 2026-11-16 | (b) retry | fail | Added `Read(${CLAUDE_SKILL_DIR}/**)` and then `Read(/${CLAUDE_SKILL_DIR}/**)` to `allowed-tools`: `dontAsk` still denied both reads. Reverted. |
| 2026-11-16 | (b) with injected phase | pass | The router now injects the phase file and adapter through `status --soft --phase`. In `dontAsk`: no denial, no skill file read, it started the requirements interview. |
| 2026-11-16 | gate in `dontAsk`, injected phase | pass | It checked the brief, tried `gate pass requirements` once, was denied without a prompt, did not rephrase it, and asked the user to run it. State stayed at `requirements`. |
