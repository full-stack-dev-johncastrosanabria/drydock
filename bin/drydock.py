#!/usr/bin/env python3
"""drydock: keeps a product's workflow state in .drydock/ and enforces phase gates."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

PHASES = ("requirements", "architecture", "audit", "prepare", "specs", "blocks", "build", "review")
CLOSED = "closed"
STATE_PATHS = (".drydock/state.json", ".drydock/blocks.json", ".drydock/metrics.jsonl", "PROJECT_STATE.md")
GATE_CHECKS = {}                                     # phase -> function(root) returning a list of errors
TIERS = ("T1", "T2", "T3")
DIMENSIONS = ("novelty", "scope", "risk", "testing", "ambiguity")
TASK_RE = re.compile(r"^\s*-\s\[(?P<done>[ xX])\]\s+(?P<id>T\d{3,})\b(?P<text>.*)$")
CHECKBOX_RE = re.compile(r"^\s*-\s\[[ xX]\]\s")
UNSUPPORTED_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)?\s*(?:\[[ xX]\]\s*)?\**T\d{3,}\b")   # un id fuera del formato de Spec Kit

NEXT = {
    "requirements": "Write docs/drydock/brief.md with the user, then run: drydock.py gate pass requirements",
    "architecture": "Write docs/drydock/stack.md and the ADRs with the user, then run: drydock.py gate pass architecture",
    "audit": "Audit the stack into docs/drydock/audit.md, resolve blockers with the user, then run: drydock.py gate pass audit",
    "prepare": "Install the harness and render the agents, then run: drydock.py gate pass prepare",
    "specs": "Run the Spec Kit chain for the next slice and drydock.py slice set <id>, then run: drydock.py gate pass specs",
    "blocks": "Write .drydock/blocks.json and run drydock.py blocks validate, then run: drydock.py gate pass blocks",
    "build": "Start the next pending block: drydock.py block start <id>",
    "review": "Run the final review and drydock.py clean-clone, then run: drydock.py gate pass review",
    "closed": "Nothing: the project is closed",
}


class CliError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def git(root: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True)
    if r.returncode != 0:
        raise CliError(1, r.stderr.strip())
    return r.stdout.rstrip()


def templates_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "templates"


def repo_root(cwd: Path) -> Path:
    try:
        return Path(git(cwd, "rev-parse", "--show-toplevel"))
    except CliError:
        raise CliError(2, "not a git repository")


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_state(root: Path) -> dict:
    path = root / ".drydock" / "state.json"
    if not path.exists():
        raise CliError(2, "not initialized")
    try:
        state = json.loads(path.read_text())
    except (OSError, ValueError) as e:
        raise CliError(2, "state unreadable: %s" % e)
    keys = ("gates", "slice", "slices_done", "current_block")
    if not isinstance(state, dict) or state.get("phase") not in NEXT or any(k not in state for k in keys):
        raise CliError(2, "state unreadable: unexpected structure")
    return state


def save_state(root: Path, state: dict) -> None:
    (root / ".drydock").mkdir(exist_ok=True)
    (root / ".drydock" / "state.json").write_text(json.dumps(state, indent=2) + "\n")
    render_state(root)


def next_action(root: Path, state: dict, live: bool) -> str:
    if state["phase"] != "build":
        return NEXT[state["phase"]]
    plan_data = load_blocks(root)
    if state["current_block"]:
        where = "Continue block %s on branch block/%s" % (state["current_block"], state["current_block"])
        return where + (": " + block_step(root, state["current_block"]) if live
                        else " (run drydock.py status for the exact step)")
    done = {b.get("id") for b in plan_data["blocks"] if b.get("status") == "done"}
    pending = [b for b in plan_data["blocks"] if b.get("status", "pending") != "done"
               and all(dep in done for dep in b.get("depends_on") or [])]
    if pending:
        return "Start the next pending block: drydock.py block start %s" % pending[0].get("id")
    if plan_data["blocks"]:
        return "All blocks are done: drydock.py gate pass build --next specs|review"
    return "Write .drydock/blocks.json and run drydock.py blocks validate, then run: drydock.py gate pass blocks"


def render_state(root: Path) -> None:
    state = load_state(root)
    closed = ", ".join(p for p in PHASES if state["gates"].get(p)) or "-"
    done = ", ".join(state["slices_done"]) or "-"
    plan_data = load_json(root / ".drydock" / "blocks.json", None)
    blocks_line = ""
    if isinstance(plan_data, dict) and isinstance(plan_data.get("blocks"), list):
        total = len(plan_data["blocks"])
        finished = sum(1 for b in plan_data["blocks"] if b.get("status") == "done")
        blocks_line = "- Blocks: %d/%d done\n" % (finished, total)
    (root / "PROJECT_STATE.md").write_text(
        "<!-- Generated by drydock.py. Do not edit. -->\n"
        "# Project state\n\n"
        "- Phase: %s\n- Slice: %s\n- Block: %s\n- Gates closed: %s\n- Slices done: %s\n%s\n"
        "## Next\n\n%s\n"
        % (state["phase"], state["slice"] or "-", state["current_block"] or "-", closed, done, blocks_line,
           next_action(root, state, live=False))
    )


def ensure_gitignore(root: Path) -> None:
    path = root / ".gitignore"
    text = path.read_text() if path.exists() else ""
    if ".drydock/local/" not in text.splitlines():
        path.write_text(text + ("" if not text or text.endswith("\n") else "\n") + ".drydock/local/\n")


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def merge_settings(existing: dict, template: dict) -> dict:
    merged = json.loads(json.dumps(existing)) if existing else {}
    permissions = merged.setdefault("permissions", {})
    for kind in ("allow", "ask", "deny"):
        current = permissions.setdefault(kind, [])
        for rule in template.get("permissions", {}).get(kind, []):
            if rule not in current:
                current.append(rule)
    for entry in template.get("hooks", {}).get("PreToolUse", []):
        hooks = merged.setdefault("hooks", {}).setdefault("PreToolUse", [])
        if not any("pr_gate.py" in json.dumps(hook) for e in hooks for hook in e.get("hooks", [])):
            hooks.append(entry)
    return merged


def resolves(root: Path, base: str) -> bool:
    return any(subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
                              capture_output=True).returncode == 0
               for ref in (f"refs/remotes/origin/{base}", f"refs/heads/{base}"))


def doctor_report(root: Path) -> tuple:
    errors, warnings = [], []
    if not (root / "verify.sh").is_file() or not os.access(str(root / "verify.sh"), os.X_OK):
        errors.append("verify.sh is missing or not executable")
    for rel in (".drydock/bin/verify.py", ".drydock/bin/pr_gate.py"):
        if not (root / rel).is_file():
            errors.append("%s is missing" % rel)
    config = load_json(root / ".drydock" / "verify.json", None)
    if not isinstance(config, dict) or not isinstance(config.get("steps"), list) or not config["steps"]:
        errors.append(".drydock/verify.json is missing, not JSON or has no steps")
    elif not resolves(root, config.get("base_branch", "main")):
        errors.append('base_branch "%s" does not resolve to a local or origin branch' % config.get("base_branch", "main"))
    settings = load_json(root / ".claude" / "settings.json", {})
    hooks = [hook for entry in settings.get("hooks", {}).get("PreToolUse", []) for hook in entry.get("hooks", [])
             if "pr_gate.py" in json.dumps(hook)]
    if not hooks:
        errors.append("no PreToolUse hook runs .drydock/bin/pr_gate.py")
    elif hooks[0].get("onFailure") != "block":
        errors.append('the pr_gate.py hook lacks "onFailure": "block"')
    template = load_json(templates_dir() / "settings.json", {})
    for rule in template.get("permissions", {}).get("ask", []):
        if rule not in settings.get("permissions", {}).get("ask", []):
            errors.append("missing permissions.ask rule %s" % rule)
    gitignore = root / ".gitignore"
    if ".drydock/local/" not in (gitignore.read_text().splitlines() if gitignore.is_file() else []):
        errors.append(".gitignore does not list .drydock/local/")
    if subprocess.run(["git", "-C", str(root), "ls-files", ".drydock/local"],
                      capture_output=True, text=True).stdout.strip():
        errors.append(".drydock/local is tracked by git")
    for var in ("CLAUDE_CODE_EFFORT_LEVEL", "CLAUDE_CODE_SUBAGENT_MODEL_FORCE"):
        if os.environ.get(var):
            warnings.append("warning: %s is set and overrides routing.json" % var)
    for rel, src in ((".drydock/bin/verify.py", "verify.py"), (".drydock/bin/pr_gate.py", "pr_gate.py"),
                     ("verify.sh", "verify.sh")):
        if (root / rel).is_file() and (root / rel).read_bytes() != (templates_dir() / src).read_bytes():
            warnings.append("warning: %s differs from the skill template (run harness install --force)" % rel)
    return errors, warnings


def parse_tasks(path: Path) -> tuple:
    tasks, errors = {}, []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        match = TASK_RE.match(line)
        if match:
            tasks[match.group("id")] = match.group("text").strip()
        elif CHECKBOX_RE.match(line):
            errors.append("tasks.md:%d: checklist item without task id" % number)
        elif UNSUPPORTED_RE.match(line):
            errors.append("tasks.md:%d: task id in unsupported format" % number)
    return tasks, errors


def computed_tier(score: dict) -> str:
    total = sum(score[d] for d in DIMENSIONS)
    if score["risk"] == 2 or total >= 7:
        return "T3" if total >= 7 else "T2"
    return "T2" if total >= 4 else "T1"


def load_blocks(root: Path) -> dict:
    path = root / ".drydock" / "blocks.json"
    if not path.exists():
        raise CliError(1, "no block plan: .drydock/blocks.json")
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as e:
        raise CliError(1, "blocks.json unreadable: %s" % e)
    if not isinstance(data, dict) or not isinstance(data.get("blocks"), list):
        raise CliError(1, "blocks.json must be an object with a blocks list")
    return data


def cycle_path(graph: dict) -> Optional[list]:
    seen, path = set(), []

    def walk(node):
        if node in path:
            return path[path.index(node):] + [node]
        if node in seen:
            return None
        seen.add(node)
        path.append(node)
        for dep in graph.get(node, []):
            found = walk(dep)
            if found:
                return found
        path.pop()
        return None

    for node in graph:
        found = walk(node)
        if found:
            return found
    return None


def validate_blocks(root: Path) -> list:
    try:
        return _validate_blocks(root)
    except (CliError, OSError, ValueError) as e:
        return [str(e)]


def _validate_blocks(root: Path) -> list:
    state = load_state(root)
    data = load_blocks(root)
    expected = "specs/%s/tasks.md" % state["slice"]
    if data.get("slice") != state["slice"]:
        return ['blocks.json is for slice "%s", current slice is "%s"' % (data.get("slice"), state["slice"])]
    if data.get("tasks_file") != expected:
        return ["tasks_file must be %s" % expected]
    path = root / expected
    if not path.is_file():
        return ["tasks file not found: %s" % expected]
    file_tasks, parse_errors = parse_tasks(path)
    if parse_errors:
        return parse_errors
    if not file_tasks:
        return ["no tasks found in %s" % expected]
    blocks = data["blocks"]
    tiers = load_json(root / ".drydock" / "routing.json", {}).get("tiers", {})
    errors, block_ids, task_ids = [], [], []
    for entry in blocks:
        block_id = entry.get("id", "?")
        if block_id in block_ids:
            errors.append("duplicate block id %s" % block_id)
        block_ids.append(block_id)
        for task in entry.get("tasks", []):
            task_id = task.get("id") if isinstance(task, dict) else None
            if task_id in task_ids:
                errors.append("duplicate task id %s" % task_id)
            task_ids.append(task_id)
    unknown = sorted({t for t in task_ids if t not in file_tasks})
    unassigned = sorted(t for t in file_tasks if t not in task_ids)
    if unassigned:
        errors.append("unassigned tasks: %s" % ", ".join(unassigned))
    if unknown:
        errors.append("unknown tasks: %s" % ", ".join(unknown))
    for entry in blocks:
        block_id = entry.get("id", "?")
        status = entry.get("status", "pending")
        if status not in ("pending", "in_progress", "done"):
            errors.append('%s: invalid status "%s"' % (block_id, status))
        tier = entry.get("tier")
        if tier not in tiers:
            errors.append("%s: unknown tier %s" % (block_id, tier))
            continue
        computed = "T1"
        for task in entry.get("tasks", []):
            task_id, score = task.get("id"), task.get("score", {})
            valid = True
            for dimension in DIMENSIONS:
                if dimension not in score:
                    errors.append("%s: missing score.%s" % (task_id, dimension))
                    valid = False
                elif isinstance(score[dimension], bool) or score[dimension] not in (0, 1, 2):
                    errors.append("%s: score.%s must be 0, 1 or 2" % (task_id, dimension))
                    valid = False
            if valid and TIERS.index(computed_tier(score)) > TIERS.index(computed):
                computed = computed_tier(score)
        if TIERS.index(tier) < TIERS.index(computed):
            errors.append("%s: tier %s is below computed %s" % (block_id, tier, computed))
        elif TIERS.index(tier) > TIERS.index(computed) and not entry.get("tier_override"):
            errors.append("%s: tier %s above computed %s needs tier_override" % (block_id, tier, computed))
        max_tasks = tiers[tier].get("max_tasks")
        if isinstance(max_tasks, int) and len(entry.get("tasks", [])) > max_tasks:
            errors.append("%s: %d tasks exceeds max_tasks %d for %s"
                          % (block_id, len(entry.get("tasks", [])), max_tasks, tier))
        for dependency in entry.get("depends_on") or []:
            if dependency not in block_ids:
                errors.append("%s: unknown dependency %s" % (block_id, dependency))
    graph = {entry.get("id"): [d for d in entry.get("depends_on") or [] if d in block_ids] for entry in blocks}
    found = cycle_path(graph)
    if found:
        errors.append("dependency cycle: %s" % " -> ".join(found))
    return errors


def specs_gate_errors(root: Path) -> list:
    state = load_state(root)
    if not state["slice"]:
        return ["no slice set: run drydock.py slice set <id>"]
    expected = "specs/%s/tasks.md" % state["slice"]
    return [] if (root / expected).is_file() else ["tasks file not found: %s" % expected]


SWEEP_PATHS = (".drydock/", "PROJECT_STATE.md", ".gitignore", "specs/", "docs/", ".specify/", ".claude/skills/")


def base_branch(root: Path) -> str:
    return load_json(root / ".drydock" / "verify.json", {}).get("base_branch", "main")


def find_block(plan_data: dict, block_id: str) -> dict:
    for entry in plan_data["blocks"]:
        if entry.get("id") == block_id:
            return entry
    raise CliError(1, "unknown block %s" % block_id)


def evidence(root: Path, sha: str, mode: str) -> Optional[dict]:
    data = load_json(root / ".drydock" / "local" / "evidence" / ("%s.%s.json" % (sha, mode)), None)
    return data if isinstance(data, dict) else None


def review_verdict(root: Path, block_id: str, sha: str) -> Optional[str]:
    path = root / ".drydock" / "local" / "reviews" / ("%s-%s.md" % (block_id, sha))
    try:
        first = path.read_text().splitlines()[0].strip()
    except (OSError, IndexError):
        return None
    return {"verdict: approve": "approve", "verdict: changes": "changes"}.get(first)


def block_step(root: Path, block_id: str) -> str:
    head = git(root, "rev-parse", "HEAD")
    passed = any((evidence(root, head, mode) or {}).get("result") == "pass" for mode in ("fast", "full"))
    verdict = review_verdict(root, block_id, head)
    full = evidence(root, head, "full") or {}
    if not passed:
        return "implement the next task (test commit, then feat commit) and run ./verify.sh --fast"
    if verdict is None:
        return "dispatch the reviewer, then drydock.py review record %s --sha %s" % (block_id, head[:12])
    if verdict == "changes":
        return "fix the review findings and run ./verify.sh --fast"
    if not (full.get("result") == "pass" and full.get("dirty") is False):
        return "run ./verify.sh (full) on the approved commit"
    return ("open the PR: drydock.py block pr-body %s | gh pr create --title ... --body-file - ; then T1: "
            "drydock.py block merge %s; T2/T3: the user approves gh pr merge block/%s --squash --delete-branch "
            "--match-head-commit %s, then drydock.py block close %s"
            % (block_id, block_id, block_id, head, block_id))


def has_origin(root: Path) -> bool:
    return "origin" in git(root, "remote").split()


def block_start(root: Path, block_id: str) -> None:
    state = load_state(root)
    if state["phase"] != "build":
        raise CliError(1, "block start is only valid in build, not %s" % state["phase"])
    if state["current_block"]:
        raise CliError(1, "block %s is still in progress" % state["current_block"])
    errors = validate_blocks(root)
    if errors:
        raise CliError(1, "; ".join(errors))
    plan_data = load_blocks(root)
    entry = find_block(plan_data, block_id)
    if entry.get("status", "pending") != "pending":
        raise CliError(1, "block %s is %s, not pending" % (block_id, entry.get("status")))
    done = {b.get("id") for b in plan_data["blocks"] if b.get("status") == "done"}
    for dependency in entry.get("depends_on") or []:
        if dependency not in done:
            raise CliError(1, "block %s depends on %s, which is not done" % (block_id, dependency))
    base = base_branch(root)
    if git(root, "rev-parse", "--abbrev-ref", "HEAD") != base:
        raise CliError(1, "not on the base branch %s" % base)
    pending = [line[3:] for line in git(root, "-c", "core.quotePath=false", "status", "--porcelain",
                                        "--untracked-files=all").splitlines() if line.strip()]
    unexpected = [path for path in pending if not path.startswith(SWEEP_PATHS)]
    if unexpected:
        raise CliError(1, "unexpected pending changes: %s" % ", ".join(unexpected))
    git(root, "switch", "-c", "block/%s" % block_id)
    origin_ref = "refs/remotes/origin/%s" % base
    if subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "--quiet", origin_ref],
                      capture_output=True).returncode == 0:
        ahead = subprocess.run(["git", "-C", str(root), "rev-list", "%s..%s" % (origin_ref, base)],
                               capture_output=True, text=True).stdout.strip()
        if ahead:
            git(root, "branch", "-f", base, origin_ref)
            print("moved %s back to origin/%s; its local commits travel in block/%s" % (base, base, block_id))
    entry["status"] = "in_progress"
    write_json(root / ".drydock" / "blocks.json", plan_data)
    state["current_block"] = block_id
    save_state(root, state)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "chore(drydock): start %s" % block_id)
    included = git(root, "show", "--name-only", "--format=", "HEAD").splitlines()
    print("started %s on branch block/%s" % (block_id, block_id))
    for path in included:
        print("  %s" % path)


def close_block(root: Path, block_id: str, merged_sha: str, attempts: int, findings: int) -> None:
    base = base_branch(root)
    git(root, "switch", base)
    if has_origin(root):
        git(root, "pull", "--ff-only", "origin", base)
    plan_data = load_blocks(root)
    entry = find_block(plan_data, block_id)
    entry["status"] = "done"
    write_json(root / ".drydock" / "blocks.json", plan_data)
    state = load_state(root)
    state["current_block"] = None
    metrics = root / ".drydock" / "metrics.jsonl"
    with metrics.open("a") as handle:
        handle.write(json.dumps({"block": block_id, "tier": entry.get("tier"), "attempts": attempts,
                                 "findings": findings, "merged_sha": merged_sha, "closed_at": now_utc()}) + "\n")
    save_state(root, state)
    print("closed %s on %s at %s" % (block_id, base, merged_sha[:7]))


def block_close(root: Path, args) -> None:
    state = load_state(root)
    if state["current_block"] != args.id:
        raise CliError(1, "block %s is not in progress" % args.id)
    if not args.merged_sha:
        raise CliError(1, "--merged-sha is required (block merge fills it in from T6C)")
    base = base_branch(root)
    ref = "origin/%s" % base if has_origin(root) else base
    if subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", args.merged_sha, ref],
                      capture_output=True).returncode != 0:
        raise CliError(1, "%s is not on %s" % (args.merged_sha[:7], base))
    close_block(root, args.id, args.merged_sha, args.attempts, args.findings)


def build_gate_errors(root: Path) -> list:
    state = load_state(root)
    try:
        plan_data = load_blocks(root)
    except CliError as e:
        return [e.message]
    if plan_data.get("slice") != state["slice"]:
        return ['blocks.json is for slice "%s", current slice is "%s"' % (plan_data.get("slice"), state["slice"])]
    if state["current_block"]:
        return ["block %s is still in progress" % state["current_block"]]
    return ["block %s is %s" % (b.get("id"), b.get("status", "pending"))
            for b in plan_data["blocks"] if b.get("status") != "done"]


GATE_CHECKS["prepare"] = lambda root: doctor_report(root)[0]
GATE_CHECKS["blocks"] = validate_blocks
GATE_CHECKS["specs"] = specs_gate_errors
GATE_CHECKS["build"] = build_gate_errors


def cmd_init(root: Path, args) -> None:
    if (root / ".drydock" / "state.json").exists():
        raise CliError(1, "already initialized")
    (root / ".drydock").mkdir(exist_ok=True)
    shutil.copyfile(str(templates_dir() / "routing.json"), str(root / ".drydock" / "routing.json"))
    settings = root / ".claude" / "settings.json"
    template = load_json(templates_dir() / "settings.json", {})
    write_json(settings, merge_settings(load_json(settings, {}), {"permissions": template.get("permissions", {})}))
    ensure_gitignore(root)
    save_state(root, {"version": 1, "phase": PHASES[0], "gates": {p: None for p in PHASES},
                      "slice": None, "slices_done": [], "current_block": None})


def cmd_status(root: Path, args) -> None:
    state = load_state(root)
    if args.phase:
        # dontAsk denies Read on the skill's own files, so the router injects them through this command
        skill = Path(__file__).resolve().parent.parent
        if state["phase"] in PHASES:
            name = "%d-%s.md" % (PHASES.index(state["phase"]) + 1, state["phase"])
            print((skill / "phases" / name).read_text() + "\n" + (skill / "adapters" / "claude.md").read_text(), end="")
        return
    print("phase: %s\nslice: %s\nblock: %s\nnext: %s"
          % (state["phase"], state["slice"] or "-", state["current_block"] or "-",
             next_action(root, state, live=True)))


def cmd_gate_pass(root: Path, args) -> None:
    state = load_state(root)
    phase = args.phase
    if state["phase"] != phase:
        raise CliError(1, "current phase is %s, not %s" % (state["phase"], phase))
    check = GATE_CHECKS.get(phase)
    if check:
        errors = check(root)
        if errors:
            for error in errors:
                print("error: %s" % error, file=sys.stderr)
            return 1
    if (phase == "build") != (args.next is not None):
        raise CliError(1, "--next is required in build and only valid there" if phase == "build"
                       else "--next is only valid in build")
    if phase == "build" and not state["slice"]:
        raise CliError(1, "no slice set in build")
    if phase == "build":
        new = args.next
        state["slices_done"].append(state["slice"])
        state["slice"] = None
        if new == "specs":
            for p in ("specs", "blocks", "build"):
                state["gates"][p] = None
        else:
            state["gates"][phase] = {"passed_at": now_utc(), "note": args.note}
    else:
        new = PHASES[PHASES.index(phase) + 1] if phase != "review" else CLOSED
        state["gates"][phase] = {"passed_at": now_utc(), "note": args.note}
    state["phase"] = new
    save_state(root, state)
    print("gate %s closed -> %s" % (phase, new))


def cmd_slice_set(root: Path, args) -> None:
    state = load_state(root)
    if state["phase"] != "specs":
        raise CliError(1, "slice set is only valid in specs")
    if not (root / "specs" / args.id).is_dir():
        raise CliError(1, "specs/%s/ does not exist" % args.id)
    state["slice"] = args.id
    save_state(root, state)


def cmd_render_state(root: Path, args) -> None:
    load_state(root)
    render_state(root)


def cmd_harness(root: Path, args) -> None:
    steps = templates_dir() / "verify-steps" / ("%s.json" % args.stack)
    if not steps.is_file():
        available = ", ".join(sorted(p.stem for p in (templates_dir() / "verify-steps").glob("*.json")))
        raise CliError(1, "unknown stack %s; available: %s" % (args.stack, available))
    copies = (("verify.sh", "verify.sh", True),
              (".drydock/bin/verify.py", "verify.py", True),
              (".drydock/bin/pr_gate.py", "pr_gate.py", True),
              (".drydock/verify.json", "verify-steps/%s.json" % args.stack, False),
              (".github/workflows/verify.yml", "ci/github-actions-%s.yml" % args.stack, False))
    for rel, src, owned in copies:
        dst = root / rel
        existed = dst.exists()
        if existed and not (args.force and owned):
            print("kept %s" % rel)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(templates_dir() / src), str(dst))
        if rel == "verify.sh":
            os.chmod(str(dst), 0o755)
        print("%s %s" % ("overwrote" if existed else "created", rel))
    settings = root / ".claude" / "settings.json"
    write_json(settings, merge_settings(load_json(settings, {}), load_json(templates_dir() / "settings.json", {})))
    print("merged .claude/settings.json")
    ensure_gitignore(root)


def cmd_block(root: Path, args) -> None:
    if args.sub == "start":
        block_start(root, args.id)
    else:
        block_close(root, args)


def cmd_blocks(root: Path, args) -> int:
    errors = validate_blocks(root)
    if errors:
        for error in errors:
            print("error: %s" % error, file=sys.stderr)
        return 1
    print("blocks: ok")


def cmd_doctor(root: Path, args) -> int:
    errors, warnings = doctor_report(root)
    for error in errors:
        print("error: %s" % error)
    for warning in warnings:
        print(warning)
    if errors:
        print("doctor: %d error(s)" % len(errors))
        return 1
    print("doctor: ok" + (" (%d warnings)" % len(warnings) if warnings else ""))
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="drydock.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    p = sub.add_parser("status")
    p.add_argument("--soft", action="store_true")
    p.add_argument("--phase", action="store_true")
    p.set_defaults(fn=cmd_status)
    p = sub.add_parser("gate").add_subparsers(dest="sub", required=True).add_parser("pass")
    p.add_argument("phase", choices=PHASES)
    p.add_argument("--note")
    p.add_argument("--next", choices=("specs", "review"))
    p.set_defaults(fn=cmd_gate_pass)
    p = sub.add_parser("slice").add_subparsers(dest="sub", required=True).add_parser("set")
    p.add_argument("id")
    p.set_defaults(fn=cmd_slice_set)
    sub.add_parser("render-state").set_defaults(fn=cmd_render_state)
    p = sub.add_parser("harness").add_subparsers(dest="sub", required=True).add_parser("install")
    p.add_argument("--stack", required=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_harness)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    p = sub.add_parser("blocks").add_subparsers(dest="sub", required=True).add_parser("validate")
    p.set_defaults(fn=cmd_blocks)
    block_parser = sub.add_parser("block").add_subparsers(dest="sub", required=True)
    p = block_parser.add_parser("start")
    p.add_argument("id")
    p.set_defaults(fn=cmd_block)
    p = block_parser.add_parser("close")
    p.add_argument("id")
    p.add_argument("--merged-sha")
    p.add_argument("--attempts", type=int, default=1)
    p.add_argument("--findings", type=int, default=0)
    p.set_defaults(fn=cmd_block)
    return ap


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(repo_root(Path.cwd()), args) or 0
    except Exception as e:
        # --soft must never fail: a malformed state file cannot stop the skill from loading
        if getattr(args, "soft", False):
            print("drydock: %s" % e)
            return 0
        if isinstance(e, CliError):
            print("error: %s" % e.message, file=sys.stderr)
            return e.code
        raise


if __name__ == "__main__":
    sys.exit(main())
