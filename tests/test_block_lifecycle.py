import json

from helpers import TS, BlocksCase, block, plan, run, valid_plan

class BlockLifecycleTests(BlocksCase):
    def setUp(self):
        super().setUp()
        self.write_json(".drydock/blocks.json", valid_plan())
        self.set_phase("build", slice="001-skeleton")            # nada confirmado todavía: lo barre block start

    def status(self):
        return self.cli("status").stdout

    def merge_locally(self, block_id):                           # hace de merge del PR: squash sobre main
        self.git("switch", "-q", "main")
        self.git("merge", "-q", "--squash", f"block/{block_id}")
        return self.commit(f"feat: {block_id} (squash)")

    def test_block_start_creates_branch_and_commits_pending_state(self):
        self.assertIn("block start B01", self.status())
        r = self.cli("block", "start", "B01")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), "block/B01")
        self.assertEqual(self.git("log", "-1", "--format=%s"), "chore(drydock): start B01")
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual((self.state()["current_block"], self.block_of("B01")["status"]), ("B01", "in_progress"))
        self.assertIn("specs/001-skeleton/tasks.md", self.git("show", "--name-only", "--format=", "HEAD").splitlines())

    def test_block_start_preconditions(self):
        self.write_json(".drydock/blocks.json", plan(block("B01", ["T001"])))
        self.assertEqual(self.cli("block", "start", "B01").returncode, 1)        # plan inválido: tareas sin asignar
        self.write_json(".drydock/blocks.json", valid_plan())
        self.set_phase("blocks", slice="001-skeleton")
        self.assertEqual(self.cli("block", "start", "B01").returncode, 1)        # fase incorrecta
        self.set_phase("build", slice="001-skeleton")
        self.assertEqual(self.cli("block", "start", "B02").returncode, 1)        # depende de B01
        self.assertEqual(self.cli("block", "start", "B99").returncode, 1)        # no existe
        self.git("switch", "-q", "-c", "other")
        self.assertEqual(self.cli("block", "start", "B01").returncode, 1)        # no está en la rama base
        self.git("switch", "-q", "main")
        self.assertEqual(self.cli("block", "start", "B01").returncode, 0)
        self.assertEqual(self.cli("block", "start", "B01").returncode, 1)        # ya hay un bloque en curso

    def test_block_start_refuses_unexpected_pending_paths(self):
        self.write(".env", "SECRET=1\n")
        r = self.cli("block", "start", "B01")
        self.assertEqual(r.returncode, 1)
        self.assertIn("unexpected pending changes: .env", r.stderr)
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), "main")
        self.assertIsNone(self.state()["current_block"])

    def test_block_start_realigns_local_base(self):
        remote = self.tmp / "remote.git"
        run(["git", "init", "-q", "--bare", "-b", "main", remote], self.tmp)
        self.git("remote", "add", "origin", str(remote))
        self.git("push", "-q", "-u", "origin", "main")
        pushed = self.head()
        self.commit("docs: spec committed on the base by mistake")
        self.assertEqual(self.cli("block", "start", "B01").returncode, 0)
        self.assertEqual(self.git("rev-parse", "main"), pushed)
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), "block/B01")

    def test_block_close_marks_done_and_appends_metrics(self):
        self.cli("block", "start", "B01")
        self.commit("feat(B01/T001): x", {"src/x.txt": "x\n"})
        sha = self.merge_locally("B01")
        r = self.cli("block", "close", "B01", "--merged-sha", sha, "--attempts", "2", "--findings", "3")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.state()["current_block"], self.block_of("B01")["status"]), (None, "done"))
        line = json.loads((self.repo / ".drydock/metrics.jsonl").read_text().splitlines()[-1])
        self.assertEqual({k: line[k] for k in ("block", "tier", "attempts", "findings", "merged_sha")},
                         {"block": "B01", "tier": "T1", "attempts": 2, "findings": 3, "merged_sha": sha})
        self.assertRegex(line["closed_at"], TS)
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), "main")
        self.assertEqual(self.cli("block", "start", "B02").returncode, 0)        # el cierre viaja en el siguiente start

    def test_block_close_rejects_sha_not_on_base(self):
        self.cli("block", "start", "B01")
        sha = self.commit("feat(B01/T001): x", {"src/x.txt": "x\n"})             # nunca se integró
        self.assertEqual(self.cli("block", "close", "B01", "--merged-sha", sha).returncode, 1)
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), "block/B01")
        self.assertEqual(self.block_of("B01")["status"], "in_progress")

    def test_status_mid_block_shows_next_action(self):
        self.cli("block", "start", "B01")
        self.assertIn("block: B01", self.status())
        self.assertIn("block/B01", self.status())
        self.assertIn("./verify.sh --fast", self.status())
        self.write_evidence(mode="fast")
        self.assertIn("review record B01", self.status())
        self.write_review("B01", "changes")
        self.assertIn("fix the review findings", self.status())
        self.write_review("B01", "approve")
        self.assertIn("run ./verify.sh (full)", self.status())
        self.write_evidence(mode="full")
        self.assertIn("block pr-body B01", self.status())
        self.assertIn("block/B01", (self.repo / "PROJECT_STATE.md").read_text())
        self.write(".drydock/blocks.json", "{broken")
        r = self.cli("status", "--soft")
        self.assertEqual((r.returncode, r.stdout.startswith("drydock:")), (0, True))

    def test_gate_pass_build_requires_all_blocks_done(self):
        r = self.cli("gate", "pass", "build", "--next", "review")
        self.assertEqual(r.returncode, 1)
        self.assertIn("B01", r.stderr)
        done = valid_plan()
        for b in done["blocks"]:
            b["status"] = "done"
        self.write_json(".drydock/blocks.json", done)
        self.assertIn("gate pass build", self.status())
        self.assertEqual(self.cli("gate", "pass", "build", "--next", "review").returncode, 0)
