import json, os, sys

from helpers import RepoCase, TEMPLATES, run

OWNED = (".drydock/bin/verify.py", ".drydock/bin/pr_gate.py", "verify.sh")

class HarnessTests(RepoCase):
    def install(self, *extra):
        return self.cli("harness", "install", "--stack", "dotnet", *extra)

    def template(self, name):
        return json.loads((TEMPLATES / name).read_text())

    def test_install_copies_files(self):                 # sin init: los gates sirven en cualquier repo
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        for rel in (*OWNED, ".drydock/verify.json", ".github/workflows/verify.yml"):
            self.assertTrue((self.repo / rel).is_file(), rel)
        self.assertTrue(os.access(self.repo / "verify.sh", os.X_OK))
        self.assertEqual(self.read_json(".drydock/verify.json"), self.template("verify-steps/dotnet.json"))
        self.assertEqual(self.read_json(".claude/settings.json"), self.template("settings.json"))
        self.assertIn(".drydock/local/", (self.repo / ".gitignore").read_text().splitlines())

    def test_install_idempotent(self):
        self.install()
        before = self.snapshot()
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_install_preserves_existing_settings(self):
        mine = {"env": {"A": "1"}, "permissions": {"allow": ["Bash(ls*)"], "ask": ["Bash(rm*)"]},
                "hooks": {"PreToolUse": [{"matcher": "Write", "hooks": [{"type": "command", "command": "echo hi"}]}]}}
        self.write_json(".claude/settings.json", mine)
        self.install()
        s, t = self.read_json(".claude/settings.json"), self.template("settings.json")
        self.assertEqual(s["env"], {"A": "1"})
        self.assertEqual(s["permissions"]["allow"], ["Bash(ls*)"] + t["permissions"]["allow"])
        self.assertEqual(s["permissions"]["ask"], ["Bash(rm*)"] + t["permissions"]["ask"])
        self.assertEqual(s["permissions"]["deny"], t["permissions"]["deny"])
        self.assertEqual(s["hooks"]["PreToolUse"], mine["hooks"]["PreToolUse"] + t["hooks"]["PreToolUse"])

    def test_init_merges_permission_rules(self):         # las reglas ask existen desde el primer gate, sin arnés
        self.cli("init")
        s = self.read_json(".claude/settings.json")
        self.assertEqual(s["permissions"], self.template("settings.json")["permissions"])
        self.assertNotIn("hooks", s)

    def test_force_overwrites_owned_scripts_only(self):
        self.install()
        self.write(".drydock/bin/verify.py", "# edited\n")
        self.write_json(".drydock/verify.json", {"steps": []})
        self.install()
        self.assertEqual((self.repo / ".drydock/bin/verify.py").read_text(), "# edited\n")
        self.install("--force")
        self.assertEqual((self.repo / ".drydock/bin/verify.py").read_bytes(), (TEMPLATES / "verify.py").read_bytes())
        self.assertEqual(self.read_json(".drydock/verify.json"), {"steps": []})

    def test_unknown_stack_fails(self):
        r = self.cli("harness", "install", "--stack", "cobol")
        self.assertEqual(r.returncode, 1)
        self.assertIn("dotnet", r.stderr)

    def test_doctor_ok(self):
        self.install()
        r = self.cli("doctor")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("doctor: ok", r.stdout)

    def test_doctor_errors(self):
        self.install()
        good = self.read_json(".claude/settings.json")

        def doctor_with(mutate):
            broken = json.loads(json.dumps(good))
            mutate(broken)
            self.write_json(".claude/settings.json", broken)
            return self.cli("doctor")

        for mutate, needle in ((lambda s: s["hooks"].pop("PreToolUse"), "pr_gate"),
                               (lambda s: s["hooks"]["PreToolUse"][0]["hooks"][0].pop("onFailure"), "onFailure"),
                               (lambda s: s["permissions"]["ask"].remove("Bash(*gh pr merge*)"), "gh pr merge")):
            r = doctor_with(mutate)
            self.assertEqual(r.returncode, 1, needle)
            self.assertIn(needle, r.stdout)
        self.write_json(".claude/settings.json", good)
        os.chmod(self.repo / "verify.sh", 0o644)
        self.assertEqual(self.cli("doctor").returncode, 1)
        os.chmod(self.repo / "verify.sh", 0o755)
        self.write_json(".drydock/verify.json", {**self.read_json(".drydock/verify.json"), "base_branch": "nope"})
        r = self.cli("doctor")
        self.assertEqual(r.returncode, 1)
        self.assertIn("base_branch", r.stdout)

    def test_doctor_fails_when_local_is_tracked(self):
        self.install()
        self.write(".drydock/local/evidence/x.json", "{}")
        self.git("add", "-f", ".drydock/local")
        r = self.cli("doctor")
        self.assertEqual(r.returncode, 1)
        self.assertIn(".drydock/local", r.stdout)

    def test_doctor_warnings_do_not_fail(self):
        self.install()
        self.write(".drydock/bin/pr_gate.py", "# edited\n")
        r = self.cli("doctor", env={"CLAUDE_CODE_EFFORT_LEVEL": "low", "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1"})
        self.assertEqual(r.returncode, 0)
        for needle in ("warning: CLAUDE_CODE_EFFORT_LEVEL", "warning: CLAUDE_CODE_SUBAGENT_MODEL_FORCE",
                       "warning: .drydock/bin/pr_gate.py differs"):
            self.assertIn(needle, r.stdout)

    def test_gate_pass_prepare_runs_doctor(self):
        self.set_phase("prepare")
        self.assertEqual(self.cli("gate", "pass", "prepare").returncode, 1)
        self.assertEqual(self.state()["phase"], "prepare")
        self.install()
        self.assertEqual(self.cli("gate", "pass", "prepare").returncode, 0)
        self.assertEqual(self.state()["phase"], "specs")

    def test_installed_gates_work_without_the_skill(self):
        self.install()
        self.write_json(".drydock/verify.json", {"steps": [{"name": "ok", "mode": "fast", "run": "true"}]})
        self.commit("chore: harness")
        payload = json.dumps({"tool_input": {"command": "gh pr create --fill"}, "cwd": str(self.repo)})
        gate = lambda: json.loads(run([sys.executable, self.repo / ".drydock/bin/pr_gate.py"], self.repo, stdin=payload).stdout)
        self.assertEqual(gate()["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(run(["sh", "verify.sh"], self.repo).returncode, 0)
        self.assertEqual(gate(), {})
