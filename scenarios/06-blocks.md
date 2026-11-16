# Scenario 06: blocks

Baseline, 2026-11-16: `claude -p` in the toy repository, without the skill. Eight billing tasks (setup, health endpoint, User model, persistence, transfer endpoint, list accounts, account detail, integration tests) and the prompt: group them into blocks with id, title, tier, dependencies and task ids.

## What the model did

- Assigned all eight tasks, each in exactly one block. No task was left out and none was invented.
- Produced seven blocks, B1 to B7, with a linear dependency chain; only the two `[P]` tasks landed together.
- Invented its own tier definition (T1 scaffolding, T2 domain logic, T3 money/concurrency) and put the transfer endpoint at T3.

## What it skipped

- The routing formula: five 0–2 dimensions, sum bands, `risk == 2` forcing T2. Its tiers were plausible but not computed from scores.
- The id format (`B01`, not `B1`) and the `blocks.json` schema.
- Parallelism: the chain serialized blocks that had no dependency between them.

## Compared with the plan's expectations

The plan expected unassigned tasks and downgraded tiers in the baseline. Unassigned tasks did not appear; tier downgrades cannot be judged without the scoring formula. T6A still enforces the schema and the computed tier; if the implementation of tier validation has to be cut for time, this baseline is the reason to question it first.
