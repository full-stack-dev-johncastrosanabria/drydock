import json, shutil, sys

from helpers import RepoCase, TEMPLATES, run

GATE = TEMPLATES / "pr_gate.py"
PR = "gh pr create --fill"

def kind(out): return out.get("hookSpecificOutput", {}).get("permissionDecision")
def reason(out): return out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")

class PrGateTests(RepoCase):
    def setUp(self):
        super().setUp()
        self.cli("init")
        self.commit("chore: init drydock")

    def gate(self, command, cwd=None, raw=None):
        payload = raw if raw is not None else json.dumps(
            {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd or self.repo)})
        r = run([sys.executable, GATE], self.repo, stdin=payload)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)                  # exactamente un objeto JSON, siempre

    def test_non_pr_command_allowed(self):
        self.assertEqual(self.gate("git status"), {})

    def test_pr_without_evidence_denied(self):
        out = self.gate(PR)
        self.assertEqual(kind(out), "deny")
        self.assertIn("./verify.sh", reason(out))

    def test_pr_with_fresh_evidence_allowed(self):
        self.write_evidence()
        self.assertEqual(self.gate(PR), {})

    def test_stale_evidence_denied(self):
        self.write_evidence()
        self.commit("feat: later", {"a.txt": "x\n"})
        self.assertEqual(kind(self.gate(PR)), "deny")

    def test_fast_failed_or_dirty_evidence_denied(self):
        for kwargs in ({"mode": "fast"}, {"result": "fail"}, {"dirty": True}):
            shutil.rmtree(self.repo / ".drydock/local", ignore_errors=True)
            self.write_evidence(**kwargs)
            self.assertEqual(kind(self.gate(PR)), "deny", kwargs)

    def test_pr_command_forms_detected(self):
        for cmd in ("cd api && gh pr create --fill", "gh -R o/r pr new --fill", "/opt/homebrew/bin/gh pr create -f",
                    "FOO=1 gh pr create", 'bash -c "gh pr create --fill"', "x=$(gh pr create --fill)", "true |gh pr create",
                    "drydock.py block pr-body B01 | gh pr create --title x --body-file -",
                    'bash -lc "gh pr create"', "if ./verify.sh; then gh pr create; fi", "time gh pr create", "env FOO=1 gh pr create",
                    "timeout 120 gh pr create", 'eval "gh pr create"', "{ gh pr create; }", "! gh pr create"):
            self.assertEqual(kind(self.gate(cmd)), "deny", cmd)

    def test_mentions_are_not_pr_commands(self):
        for cmd in ('grep -r "gh pr create" .', 'git commit -m "docs: gh pr create"', "gh pr view 3",
                    "gh auth status && echo pr create", "git stash push", 'git commit -m "push later"',
                    'echo "time to gh pr create"'):
            self.assertEqual(self.gate(cmd), {}, cmd)

    def test_merge_outside_block_asks(self):
        self.assertEqual(kind(self.gate("gh pr merge 7 --squash")), "ask")   # un allow global anula la regla ask, no el hook

    def test_cwd_subdirectory(self):
        (self.repo / "sub").mkdir()
        self.assertEqual(kind(self.gate(PR, cwd=self.repo / "sub")), "deny")
        self.write_evidence()
        self.assertEqual(self.gate(PR, cwd=self.repo / "sub"), {})

    def test_unmanaged_repo_ignored(self):
        shutil.rmtree(self.repo / ".drydock")
        self.assertEqual(self.gate(PR), {})
        self.assertEqual(self.gate("git push origin main"), {})

    def test_block_needs_approving_review(self):
        self.set_state(current_block="B01")
        self.commit("chore(drydock): start B01")
        self.write_evidence()
        out = self.gate(PR)
        self.assertEqual(kind(out), "deny")
        self.assertIn("reviewer", reason(out))
        self.write_review("B01", "changes")
        self.assertEqual(kind(self.gate(PR)), "deny")
        self.write_review("B01", "approve")
        self.assertEqual(self.gate(PR), {})

    def test_merge_in_block_needs_evidence_review_and_head(self):
        self.set_state(current_block="B01")
        self.commit("chore(drydock): start B01")
        merge = f"gh pr merge 7 --squash --delete-branch --match-head-commit {self.head()}"
        self.assertEqual(kind(self.gate(merge)), "deny")                         # sin evidencia
        self.write_evidence()
        self.write_review("B01")
        self.assertEqual(self.gate(merge), {})
        self.assertEqual(kind(self.gate("gh pr merge 7 --squash --delete-branch")), "deny")
        self.commit("fix: pushed after approval", {"a.txt": "x\n"})
        self.assertEqual(kind(self.gate(merge)), "deny")                         # el comando nombra un HEAD viejo

    def test_internal_error_fails_closed(self):
        self.write(f".drydock/local/evidence/{self.head()}.full.json", "{broken")
        self.assertEqual(kind(self.gate(PR)), "deny")

    def test_garbage_stdin(self):
        self.assertEqual(self.gate(None, raw="not json"), {})
        self.assertEqual(kind(self.gate(None, raw="not json: gh pr create")), "deny")
        self.assertEqual(kind(self.gate(None, raw="not json: git push origin main")), "ask")

    def test_push_to_base_asks(self):
        for cmd in ("git push", "git push origin main", "cd . && git push -u origin main", "git -C . push"):
            self.assertEqual(kind(self.gate(cmd)), "ask", cmd)               # la rama actual es main
        self.git("switch", "-q", "-c", "block/B01")
        for cmd in ("git push", "git push -u origin block/B01", "git push origin main-fix"):
            self.assertEqual(self.gate(cmd), {}, cmd)
        for cmd in ("git push origin HEAD:main", "git push origin main; echo done", 'git push origin "main"',
                    "git push origin 'HEAD:main'", "git push origin refs/heads/main"):
            self.assertEqual(kind(self.gate(cmd)), "ask", cmd)

    def test_settings_template(self):
        t = json.loads((TEMPLATES / "settings.json").read_text())
        (entry,) = t["hooks"]["PreToolUse"]
        (hook,) = entry["hooks"]
        self.assertEqual(entry["matcher"], "Bash")
        self.assertEqual(hook, {"type": "command", "command": "python3", "args": ["${CLAUDE_PROJECT_DIR}/.drydock/bin/pr_gate.py"],
                                "onFailure": "block", "timeout": 30})
        self.assertEqual(t["permissions"], {
            "allow": ["Bash(python3 *drydock.py *)", "Bash(./verify.sh*)"],
            "ask": ["Bash(*drydock.py gate pass*)", "Bash(*drydock.py deploy*)", "Bash(*gh pr merge*)"],
            "deny": ["Skill(speckit-implement)"]})
