import json, sys, tempfile

from helpers import CLI, PHASES, ROOT, TEMPLATES, TS, RepoCase, run


class StateTests(RepoCase):
    def test_init_creates_state(self):
        r = self.cli("init")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.state(), {"version": 1, "phase": "requirements", "gates": {p: None for p in PHASES},
                                        "slice": None, "slices_done": [], "current_block": None})
        self.assertEqual(list(self.state()["gates"]), PHASES)
        self.assertIn(".drydock/local/", (self.repo / ".gitignore").read_text().splitlines())
        self.assertEqual(self.read_json(".drydock/routing.json"), json.loads((TEMPLATES / "routing.json").read_text()))
        self.assertIn("- Phase: requirements", (self.repo / "PROJECT_STATE.md").read_text())

    def test_init_twice_fails(self):
        self.cli("init")
        before = self.snapshot()
        self.assertEqual(self.cli("init").returncode, 1)
        self.assertEqual(self.snapshot(), before)

    def test_init_outside_git_fails(self):
        with tempfile.TemporaryDirectory() as d:
            r = run([sys.executable, CLI, "init"], d)
            self.assertEqual(r.returncode, 2)
            self.assertIn("not a git repository", r.stderr)      # sin esto pasa en vacío: python sale 2 si el script no existe

    def test_status(self):
        r = self.cli("status")
        self.assertEqual(r.returncode, 2)
        self.assertIn("not initialized", r.stderr)
        self.cli("init")
        lines = self.cli("status").stdout.splitlines()
        self.assertEqual(lines[:3], ["phase: requirements", "slice: -", "block: -"])
        self.assertTrue(lines[3].startswith("next: "))
        self.assertIn("gate pass requirements", lines[3])
        self.write(".drydock/state.json", '{"phase": "build"}')          # objeto con fase válida y sin las demás claves
        r = self.cli("status")
        self.assertEqual(r.returncode, 2)
        self.assertIn("state unreadable", r.stderr)

    def test_status_soft_never_fails(self):
        r = self.cli("status", "--soft")
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "drydock: not initialized"))
        self.cli("init")
        self.write(".drydock/state.json", "{broken")
        r = self.cli("status", "--soft")
        self.assertEqual(r.returncode, 0)
        self.assertIn("drydock: state unreadable", r.stdout)
        self.write(".drydock/state.json", "[]")                       # JSON válido con forma incorrecta
        r = self.cli("status", "--soft")
        self.assertEqual(r.returncode, 0)
        self.assertIn("drydock:", r.stdout)
        with tempfile.TemporaryDirectory() as d:
            r = run([sys.executable, CLI, "status", "--soft"], d)
            self.assertEqual((r.returncode, r.stdout.strip()), (0, "drydock: not a git repository"))

    def test_gate_pass_advances(self):
        self.cli("init")
        r = self.cli("gate", "pass", "requirements", "--note", "brief v1")
        self.assertEqual(r.returncode, 0, r.stderr)
        s = self.state()
        self.assertEqual(s["phase"], "architecture")
        self.assertRegex(s["gates"]["requirements"]["passed_at"], TS)
        self.assertEqual(s["gates"]["requirements"]["note"], "brief v1")
        self.assertIn("- Phase: architecture", (self.repo / "PROJECT_STATE.md").read_text())

    def test_gate_pass_wrong_phase_rejected(self):
        self.cli("init")
        before = self.snapshot()
        self.assertEqual(self.cli("gate", "pass", "specs").returncode, 1)
        self.assertEqual(self.cli("gate", "pass", "requirements", "--next", "specs").returncode, 1)   # --next solo en build
        self.assertEqual(self.snapshot(), before)

    def test_build_requires_next(self):
        self.set_phase("build")                                          # sin rebanada no se cierra build
        before = self.snapshot()
        self.assertEqual(self.cli("gate", "pass", "build", "--next", "specs").returncode, 1)
        self.assertEqual(self.snapshot(), before)
        self.set_phase("build", slice="001-skeleton")
        self.write_json(".drydock/blocks.json", {"version": 1, "slice": "001-skeleton",
                                                 "tasks_file": "specs/001-skeleton/tasks.md", "blocks": []})
        self.assertEqual(self.cli("gate", "pass", "build").returncode, 1)
        self.assertEqual(self.cli("gate", "pass", "build", "--next", "specs").returncode, 0)
        s = self.state()
        self.assertEqual((s["phase"], s["slice"], s["slices_done"]), ("specs", None, ["001-skeleton"]))
        self.assertEqual([s["gates"][p] for p in ("specs", "blocks", "build")], [None, None, None])
        self.assertIsNotNone(s["gates"]["prepare"])
        self.set_phase("build", slice="002-users")
        self.write_json(".drydock/blocks.json", {"version": 1, "slice": "002-users",
                                                 "tasks_file": "specs/002-users/tasks.md", "blocks": []})
        self.assertEqual(self.cli("gate", "pass", "build", "--next", "review").returncode, 0)
        s = self.state()
        self.assertEqual((s["phase"], s["slice"], s["slices_done"]), ("review", None, ["001-skeleton", "002-users"]))
        self.assertRegex(s["gates"]["build"]["passed_at"], TS)

    def test_slice_set_only_in_specs(self):
        self.cli("init")
        self.assertEqual(self.cli("slice", "set", "001-skeleton").returncode, 1)
        self.set_phase("specs")
        self.assertEqual(self.cli("slice", "set", "001-skeleton").returncode, 1)     # specs/001-skeleton/ no existe
        self.write("specs/001-skeleton/spec.md", "# spec\n")
        self.assertEqual(self.cli("slice", "set", "001-skeleton").returncode, 0)
        self.assertEqual(self.state()["slice"], "001-skeleton")

    def test_review_closes(self):
        self.set_phase("review")
        self.assertEqual(self.cli("gate", "pass", "review").returncode, 0)
        self.assertEqual(self.state()["phase"], "closed")
        self.assertEqual(self.cli("gate", "pass", "review").returncode, 1)

    def test_render_state_idempotent(self):
        self.cli("init")
        self.assertEqual(self.cli("render-state").returncode, 0)      # sin esto pasa aunque render-state no exista
        first = (self.repo / "PROJECT_STATE.md").read_bytes()
        self.cli("render-state")
        self.assertEqual((self.repo / "PROJECT_STATE.md").read_bytes(), first)

    def test_status_phase_prints_phase_file_and_adapter(self):
        self.cli("init")
        r = self.cli("status", "--soft", "--phase")
        self.assertEqual(r.returncode, 0, r.stderr)
        expected = (ROOT / "phases" / "1-requirements.md").read_text() + "\n" + (ROOT / "adapters" / "claude.md").read_text()
        self.assertEqual(r.stdout, expected)
        self.set_phase("review")
        self.cli("gate", "pass", "review")
        self.assertEqual(self.cli("status", "--soft", "--phase").stdout, "")     # closed: no phase file
