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
- (b) It reads `phases/1-requirements.md` and `adapters/claude.md`, and no other phase file.
- (c) It prints the State line and stops.

## Log

| Date | Case | Result | Notes |
|---|---|---|---|
