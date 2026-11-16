# Claude Code adapter

## CLI

Run the CLI as `python3 ${CLAUDE_SKILL_DIR}/bin/drydock.py <command>`.

## Approvals

Approvals arrive as permission prompts: `gate pass`, `deploy`, `gh pr merge` and a push to the base branch. Wait for the prompt and never rephrase the command to avoid it. If the permission mode denies a command without asking, ask the user to run that command.

## Subagents

Subagent dispatch: see Task 8.
