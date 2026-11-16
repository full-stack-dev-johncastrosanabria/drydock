import sys

from helpers import RepoCase, TS, run

OK = [{"name": "ok", "mode": "fast", "run": "true"}]
RED = {"base_branch": "main", "src_globs": ["src/*"], "test_globs": ["tests/*"], "red": "sh tests/run.sh", "steps": OK}

class VerifyCase(RepoCase):
    def setUp(self):
        super().setUp()
        self.install_verify({"steps": OK})

    def verify(self, *args):
        return run([sys.executable, self.repo / ".drydock/bin/verify.py", *args], self.repo)

    def evidence(self, mode):
        return self.read_json(f".drydock/local/evidence/{self.head()}.{mode}.json")

class VerifyTests(VerifyCase):
    def test_full_pass_writes_evidence(self):
        r = self.verify()
        self.assertEqual(r.returncode, 0, r.stderr)
        ev = self.evidence("full")
        self.assertEqual((ev["sha"], ev["mode"], ev["result"], ev["dirty"], ev["tdd_exempt"]), (self.head(), "full", "pass", False, []))
        self.assertEqual([(s["name"], s["exit"]) for s in ev["steps"]], [("ok", 0)])
        self.assertRegex(ev["finished_at"], TS)

    def test_stops_at_first_failure(self):
        self.set_verify(steps=[{"name": "a", "mode": "fast", "run": "true"}, {"name": "b", "mode": "fast", "run": "false"},
                               {"name": "c", "mode": "fast", "run": "touch marker"}])
        self.assertEqual(self.verify().returncode, 1)
        self.assertFalse((self.repo / "marker").exists())
        ev = self.evidence("full")
        self.assertEqual((ev["result"], [s["name"] for s in ev["steps"]], ev["steps"][-1]["exit"]), ("fail", ["a", "b"], 1))

    def test_fast_skips_full_steps(self):
        self.set_verify(steps=[{"name": "a", "mode": "fast", "run": "true"}, {"name": "slow", "mode": "full", "run": "touch marker"}])
        self.assertEqual(self.verify("--fast").returncode, 0)
        self.assertFalse((self.repo / "marker").exists())
        names = sorted(p.name for p in (self.repo / ".drydock/local/evidence").iterdir())
        self.assertEqual(names, [f"{self.head()}.fast.json"])

    def test_dirty_tree_marks_dirty(self):
        self.write("uncommitted.txt", "x\n")
        self.assertEqual(self.verify().returncode, 0)
        self.assertIs(self.evidence("full")["dirty"], True)

    def test_dirty_is_computed_after_steps(self):
        self.set_verify(steps=[{"name": "gen", "mode": "fast", "run": "touch generated.txt"}])
        self.assertEqual(self.verify().returncode, 0)
        self.assertIs(self.evidence("full")["dirty"], True)

    def test_config_errors_exit_2(self):
        self.write_json(".drydock/verify.json", {"steps": OK, "red": "true"})      # red sin src_globs ni test_globs
        self.assertEqual(self.verify().returncode, 2)
        (self.repo / ".drydock/verify.json").write_text("{broken")
        self.assertEqual(self.verify().returncode, 2)
        (self.repo / ".drydock/verify.json").unlink()
        self.assertEqual(self.verify().returncode, 2)
        self.assertFalse((self.repo / ".drydock/local").exists())

    def test_wrapper_runs_from_subdirectory(self):
        (self.repo / "sub").mkdir()
        r = run(["sh", self.repo / "verify.sh", "--fast"], self.repo / "sub")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.repo / f".drydock/local/evidence/{self.head()}.fast.json").exists())

class RedFirstTests(VerifyCase):
    def setUp(self):
        super().setUp()
        self.set_verify(**RED)
        self.git("switch", "-q", "-c", "block/B01")

    def red_test(self):
        return self.commit("test(B01/T001): feature exists", {"tests/run.sh": "test -f src/feature.txt\n"})

    def impl(self, message="feat(B01/T001): add feature", path="src/feature.txt"):
        return self.commit(message, {path: "x\n"})

    def test_test_then_impl_passes(self):
        t = self.red_test()
        self.impl()
        r = self.verify("--fast")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        ev = self.evidence("fast")
        self.assertEqual((ev["steps"][-1]["name"], ev["steps"][-1]["exit"], ev["tdd_exempt"]), ("red-first", 0, []))
        self.assertNotEqual(self.read_json(f".drydock/local/evidence/{t}.red.json")["exit"], 0)

    def test_impl_without_red_test_fails(self):
        sha = self.impl()
        r = self.verify("--fast")
        self.assertEqual(r.returncode, 1)
        self.assertIn(sha[:7], r.stdout + r.stderr)
        self.assertIn("TDD-Exempt", r.stdout + r.stderr)
        ev = self.evidence("fast")
        self.assertEqual((ev["result"], ev["steps"][-1]["name"]), ("fail", "red-first"))

    def test_non_ascii_source_path_is_seen(self):
        self.impl(path="src/caf\u00e9.txt")                      # git entrecomilla rutas no ASCII si no se le pide lo contrario
        self.assertEqual(self.verify("--fast").returncode, 1)

    def test_green_test_does_not_arm(self):
        self.commit("test(B01/T001): always green", {"tests/run.sh": "true\n"})
        self.impl()
        self.assertEqual(self.verify("--fast").returncode, 1)

    def test_unarmed_mixed_commit_fails(self):
        self.commit("feat(B01/T001): both", {"tests/run.sh": "test -f src/feature.txt\n", "src/feature.txt": "x\n"})
        self.assertEqual(self.verify("--fast").returncode, 1)

    def test_red_test_arms_only_its_task(self):
        self.red_test()
        self.impl()
        self.impl("feat(B01/T002): more", "src/more.txt")
        self.assertEqual(self.verify("--fast").returncode, 1)

    def test_same_task_commits_stay_armed(self):
        self.red_test()
        self.impl()
        self.impl("fix(B01/T001): format", "src/fmt.txt")
        self.assertEqual(self.verify("--fast").returncode, 0)
        self.assertEqual(self.evidence("fast")["tdd_exempt"], [])

    def test_unscoped_red_test_arms_one_commit(self):
        self.commit("test: feature exists", {"tests/run.sh": "test -f src/feature.txt\n"})
        self.impl("feat: add feature")
        self.assertEqual(self.verify("--fast").returncode, 0)
        self.impl("feat: more", "src/more.txt")
        self.assertEqual(self.verify("--fast").returncode, 1)

    def test_exempt_trailer_is_recorded(self):
        sha = self.commit("refactor(B01): rename\n\nTDD-Exempt: pure rename", {"src/a.txt": "x\n"})
        self.assertEqual(self.verify("--fast").returncode, 0)
        self.assertEqual(self.evidence("fast")["tdd_exempt"], [{"sha": sha, "reason": "pure rename"}])

    def test_cache_is_used(self):
        t = self.commit("test(B01/T001): green, cached as red", {"tests/run.sh": "true\n"})
        self.impl()
        self.write_json(f".drydock/local/evidence/{t}.red.json", {"sha": t, "exit": 1, "seconds": 0.0})
        self.assertEqual(self.verify("--fast").returncode, 0)

    def test_skipped_without_red_key(self):
        self.git("switch", "-q", "main")
        self.write_json(".drydock/verify.json", {k: v for k, v in RED.items() if k != "red"})
        self.commit("chore: no red")
        self.git("switch", "-q", "-c", "block/B02")
        self.impl()
        self.assertEqual(self.verify("--fast").returncode, 0)
        self.assertNotIn("red-first", [s["name"] for s in self.evidence("fast")["steps"]])

    def test_base_branch_itself_passes(self):
        self.git("switch", "-q", "main")
        self.assertEqual(self.verify("--fast").returncode, 0)

    def test_unknown_base_exits_2(self):
        self.set_verify(base_branch="nope")
        self.assertEqual(self.verify("--fast").returncode, 2)

    def test_leaves_no_worktree_behind(self):
        self.red_test()
        self.impl()
        self.verify("--fast")
        self.assertEqual(len(self.git("worktree", "list").splitlines()), 1)
