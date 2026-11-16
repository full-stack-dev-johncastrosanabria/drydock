#!/usr/bin/env python3
"""Standalone verification gate: runs .drydock/verify.json, enforces red-first, writes evidence."""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

TRAILER_RE = re.compile(r"^TDD-Exempt:\s*(\S.*)$", re.M)
SCOPE_RE = re.compile(r"^\w+\(([^)]+)\)!?:")             # "test(B01/T003): ..." -> "B01/T003"


def config_error(message: str) -> None:
    print(f"verify: config error: {message}", file=sys.stderr)
    sys.exit(2)


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def git(root: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True)
    return r.stdout.strip()


def repo_root() -> Path:
    try:
        return Path(git(Path.cwd(), "rev-parse", "--show-toplevel"))
    except (subprocess.CalledProcessError, OSError):
        config_error("not a git repository")


def load_config(root: Path) -> dict:
    path = root / ".drydock" / "verify.json"
    try:
        config = json.loads(path.read_text())
    except OSError:
        config_error(f"cannot read {path}")
    except ValueError as e:
        config_error(f"{path} is not valid JSON ({e})")
    if not isinstance(config, dict):
        config_error("verify.json must be a JSON object")
    steps = config.get("steps")
    if not isinstance(steps, list) or not all(
            isinstance(s, dict) and isinstance(s.get("name"), str) and s.get("mode") in ("fast", "full")
            and isinstance(s.get("run"), str) for s in steps):
        config_error('"steps" must be a list of {name, mode: "fast"|"full", run}')
    if "red" in config:
        globs = (config.get("src_globs"), config.get("test_globs"))
        if not isinstance(config["red"], str) or not all(
                isinstance(g, list) and all(isinstance(x, str) for x in g) for g in globs):
            config_error('"red" requires src_globs and test_globs')
    return config


def run_step(root: Path, name: str, command: str) -> dict:
    print(f"== {name} ==", flush=True)
    start = time.monotonic()
    code = subprocess.run(["sh", "-c", command], cwd=str(root)).returncode
    return {"name": name, "exit": code, "seconds": round(time.monotonic() - start, 2)}


def matches(path: str, globs: list) -> bool:
    return any(fnmatch.fnmatchcase(path, g) for g in globs)


def resolve_base(root: Path, base: str) -> str:
    for ref in (f"refs/remotes/origin/{base}", f"refs/heads/{base}"):
        try:
            git(root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
            return ref
        except subprocess.CalledProcessError:
            pass
    config_error(f'unknown base branch "{base}" (no refs/remotes/origin/{base} or refs/heads/{base})')


def is_red(root: Path, sha: str, command: str) -> bool:
    cache = root / ".drydock" / "local" / "evidence" / f"{sha}.red.json"
    if cache.exists():
        return json.loads(cache.read_text())["exit"] != 0
    tmp = tempfile.mkdtemp(prefix="drydock-red-")
    start = time.monotonic()
    try:
        git(root, "worktree", "add", "--detach", tmp, sha)
        # shortcut: "red" means non-zero exit in a clean worktree; add a green-at-base probe if a stack's test command can fail for missing dependencies
        code = subprocess.run(["sh", "-c", command], cwd=tmp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    finally:
        subprocess.run(["git", "-C", str(root), "worktree", "remove", "--force", tmp], capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"sha": sha, "exit": code, "seconds": round(time.monotonic() - start, 2)}, indent=2) + "\n")
    return code != 0


def red_first(root: Path, config: dict) -> tuple:
    base = resolve_base(root, config.get("base_branch", "main"))
    armed, exempt = set(), []                       # scopes with a failing test; None is a commit without scope
    for sha in git(root, "rev-list", "--reverse", "--no-merges", f"{base}..HEAD").split():
        files = git(root, "-c", "core.quotePath=false", "diff-tree", "--no-commit-id", "--name-only", "-r", sha).splitlines()
        message = git(root, "log", "-1", "--format=%B", sha)
        scope = (SCOPE_RE.match(message) or [None, None])[1]
        touches_test = any(matches(f, config["test_globs"]) for f in files)
        touches_src = any(matches(f, config["src_globs"]) and not matches(f, config["test_globs"]) for f in files)
        if touches_src:
            trailer = TRAILER_RE.search(message)
            if trailer:
                exempt.append({"sha": sha, "reason": trailer.group(1).strip()})
            elif scope in armed:
                if scope is None:
                    armed.discard(None)             # without scope, a test arms a single commit
            else:
                print(f"red-first: {sha[:7]} changes source with no failing test commit before it. "
                      "Commit the test first, or add a 'TDD-Exempt: <reason>' trailer.")
                return 1, exempt
        elif touches_test and is_red(root, sha, config["red"]):
            armed.add(scope)
    return 0, exempt


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(prog="verify", description="Run the repo's verification gate.")
    parser.add_argument("--fast", action="store_true", help="skip steps marked full")
    mode = "fast" if parser.parse_args(argv).fast else "full"
    root = repo_root()
    config = load_config(root)
    steps, exempt, failed = [], [], None
    for step in config["steps"]:
        if mode == "fast" and step["mode"] == "full":
            continue
        steps.append(run_step(root, step["name"], step["run"]))
        if steps[-1]["exit"] != 0:
            failed = step["name"]
            break
    if failed is None and "red" in config:
        start = time.monotonic()
        code, exempt = red_first(root, config)
        steps.append({"name": "red-first", "exit": code, "seconds": round(time.monotonic() - start, 2)})
        failed = "red-first" if code else None
    sha = git(root, "rev-parse", "HEAD")
    evidence = {"sha": sha, "mode": mode, "result": "fail" if failed else "pass",
                "dirty": bool(git(root, "status", "--porcelain")), "steps": steps,
                "tdd_exempt": exempt, "finished_at": now()}
    path = root / ".drydock" / "local" / "evidence" / f"{sha}.{mode}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"verify {mode}: fail ({failed})" if failed else f"verify {mode}: pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
