#!/usr/bin/env python3
"""PreToolUse gate: PR creation and merges need fresh full evidence (and an approving review inside a block); pushes to the base branch ask."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# shortcut: regex, not a shell parser; CI is the authority
SEP = (r"(?:^|[;&|\n(`{!]|\$\(|-\w*c\s+[\"']|\b(?:then|do|else|time|exec|command|env|nohup|eval|timeout\s+\S+)\s+[\"']?)"
       r"\s*(?:\w+=\S*\s*)*(?:\S*/)?")
PR_RE = re.compile(SEP + r"gh\b[^|;&\n]*\bpr\s+(?:create|new)\b")
MERGE_RE = re.compile(SEP + r"gh\b[^|;&\n]*\bpr\s+merge\b")
PUSH_RE = re.compile(SEP + r"git(?:\s+-[cC]\s+\S+|\s+--[\w-]+(?:=\S+)?)*\s+push\b")
LOOSE_RE = re.compile(r"\bgh\b.*\bpr\b.*\b(?:create|new|merge)\b", re.S)
LOOSE_PUSH_RE = re.compile(r"\bgit\b.*\bpush\b", re.S)


def decision(kind: str, reason: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": kind,
                                   "permissionDecisionReason": reason}}


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


def managed_root(cwd: str) -> Optional[Path]:
    try:
        root = Path(git(Path(cwd), "rev-parse", "--show-toplevel"))
    except (subprocess.CalledProcessError, OSError):
        return None
    return root if (root / ".drydock").is_dir() else None


def evidence_error(root: Path, head: str) -> Optional[str]:
    path = root / ".drydock" / "local" / "evidence" / f"{head}.full.json"
    if not path.is_file():
        return f"No full verify evidence for commit {head[:7]}. Run ./verify.sh and retry."
    ev = json.loads(path.read_text())
    if ev.get("sha") != head or ev.get("mode") != "full" or ev.get("result") != "pass" or ev.get("dirty") is not False:
        return (f"Verify evidence for {head[:7]} is not a clean full pass (result={ev.get('result')}, "
                f"dirty={ev.get('dirty')}). Commit or ignore the pending files, then run ./verify.sh.")
    return None


def review_error(root: Path, head: str, block) -> Optional[str]:
    if not block:
        return None
    review = root / ".drydock" / "local" / "reviews" / f"{block}-{head}.md"
    first = review.read_text().splitlines()[0].strip() if review.is_file() else ""
    if first != "verdict: approve":
        return (f"Block {block} has no approving review for commit {head[:7]}. "
                "Dispatch the reviewer and run drydock.py review record.")
    return None


def push_decision(root: Path, command: str) -> dict:
    base = "main"
    try:
        base = json.loads((root / ".drydock" / "verify.json").read_text()).get("base_branch", "main")
    except (OSError, ValueError, AttributeError):
        pass                                             # broken config still counts as main below
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    if branch == base or re.search(rf"(?:^|[\s:+\"']|refs/heads/){re.escape(base)}(?![\w./-])", command):
        return decision("ask", f'Direct push to the base branch "{base}". Drydock integrates through block PRs; '
                               "approve only for repository bootstrap.")
    return {}


def decide(payload: dict) -> dict:
    command = payload["tool_input"]["command"]
    is_pr, is_merge, is_push = PR_RE.search(command), MERGE_RE.search(command), PUSH_RE.search(command)
    if not (is_pr or is_merge or is_push):
        return {}
    root = managed_root(payload.get("cwd") or os.getcwd())
    if root is None:
        return {}
    try:
        head = git(root, "rev-parse", "HEAD")
    except subprocess.CalledProcessError:           # no commits: nothing can be verified
        return decision("deny", "This repository has no HEAD commit; commit before creating a PR, merging or pushing.")
    state = root / ".drydock" / "state.json"
    block = json.loads(state.read_text()).get("current_block") if state.exists() else None
    if is_pr or (is_merge and block):
        for error in (evidence_error(root, head), review_error(root, head, block)):
            if error:
                return decision("deny", error)
        if is_merge and f"--match-head-commit {head}" not in command:
            return decision("deny", f"Add --match-head-commit {head} to the merge command so it cannot include "
                                    "unreviewed commits.")
    elif is_merge:                                  # a global allow rule can override permissions.ask; a hook decision cannot
        return decision("ask", "gh pr merge outside a block. Drydock integrates blocks through their PRs; "
                               "approve only for a manual integration.")
    if is_push:
        return push_decision(root, command)
    return {}


def main() -> int:
    raw = sys.stdin.read()
    try:
        out = decide(json.loads(raw))
    except Exception as exc:                        # fail closed if the input looks like a PR, a merge or a push
        reason = f"pr_gate internal error: {exc!r}"
        out = decision("deny", reason) if LOOSE_RE.search(raw) else decision("ask", reason) if LOOSE_PUSH_RE.search(raw) else {}
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
