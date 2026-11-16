import shutil

from helpers import FIXTURES, BlocksCase, block, plan, task, valid_plan

class ValidateTests(BlocksCase):
    def rejected(self, plan_obj, *needles):
        r = self.validate(plan_obj)
        self.assertEqual(r.returncode, 1)
        for needle in needles:
            self.assertIn(needle, r.stderr)

    def test_valid_plan_passes(self):
        r = self.validate(valid_plan())
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_unique_ids(self):
        self.rejected(plan(block("B01", ["T001", "T002", "T003"]), block("B01", ["T004", "T004", "T005"])),
                      "duplicate block id B01", "duplicate task id T004")

    def test_all_tasks_assigned(self):
        self.rejected(plan(block("B01", ["T001", "T002", "T099"])), "unassigned tasks: T003, T004, T005", "unknown tasks: T099")
        shutil.copy(FIXTURES / "tasks-b.md", self.repo / "specs/001-skeleton/tasks.md")
        self.assertEqual(self.validate(plan(block("B01", ["T001", "T002", "T1000"]))).returncode, 0)

    def test_checklist_line_without_id_rejected(self):
        self.write("specs/001-skeleton/tasks.md", "- [ ] T001 ok\n- [ ] Create model without id\n")
        self.rejected(plan(block("B01", ["T001"])), "tasks.md:2: checklist item without task id")

    def test_task_in_other_format_rejected(self):
        self.write("specs/001-skeleton/tasks.md",
                   "- [ ] T001 ok\n* [ ] T003 star bullet\n1. [ ] T005 numbered\nT007 [US1] no checkbox\n")
        self.rejected(plan(block("B01", ["T001"])), "tasks.md:2: task id in unsupported format",
                      "tasks.md:3: task id in unsupported format", "tasks.md:4: task id in unsupported format")

    def test_empty_plan_rejected(self):
        self.write("specs/001-skeleton/tasks.md", "# Tasks\n\nNothing parseable here.\n")
        self.rejected(plan(), "no tasks found in specs/001-skeleton/tasks.md")
        (self.repo / "specs/001-skeleton/tasks.md").unlink()
        self.rejected(plan(), "tasks file not found: specs/001-skeleton/tasks.md")

    def test_plan_of_another_slice_rejected(self):
        p = valid_plan()
        p["slice"] = "000-old"
        self.rejected(p, 'blocks.json is for slice "000-old", current slice is "001-skeleton"')
        p = valid_plan()
        p["tasks_file"] = "specs/000-old/tasks.md"
        self.rejected(p, "tasks_file must be specs/001-skeleton/tasks.md")

    def test_gate_pass_specs_requires_slice_and_tasks(self):
        self.set_phase("specs")
        self.assertEqual(self.cli("gate", "pass", "specs").returncode, 1)            # sin rebanada
        self.set_phase("specs", slice="001-skeleton")
        self.assertEqual(self.cli("gate", "pass", "specs").returncode, 0)            # BlocksCase ya escribió tasks.md
        self.assertEqual(self.state()["phase"], "blocks")

    def test_score_range(self):
        bad = valid_plan()
        bad["blocks"][0]["tasks"][0]["score"]["risk"] = 3
        del bad["blocks"][0]["tasks"][1]["score"]["testing"]
        self.rejected(bad, "T001: score.risk must be 0, 1 or 2", "T002: missing score.testing")

    def test_tier_not_below_computed(self):                  # T001 suma 4 → T2
        self.rejected(plan(block("B01", [task("T001", novelty=2, scope=2), "T002", "T003", "T004", "T005"])),
                      "B01: tier T1 is below computed T2")

    def test_risk_two_forces_t2(self):                       # T001 suma 2, pero risk = 2
        self.rejected(plan(block("B01", [task("T001", risk=2), "T002", "T003", "T004", "T005"])),
                      "B01: tier T1 is below computed T2")

    def test_tier_above_needs_override(self):
        p = plan(block("B01", ["T001"], tier="T2"), block("B02", ["T002", "T003", "T004", "T005"]))
        self.rejected(p, "B01: tier T2 above computed T1 needs tier_override")
        p["blocks"][0]["tier_override"] = "touches the payment contract"
        self.assertEqual(self.validate(p).returncode, 0)

    def test_max_tasks_per_tier(self):                       # T2 admite 4
        self.rejected(plan(block("B01", ["T001", "T002", "T003", "T004", "T005"], tier="T2", tier_override="x")),
                      "B01: 5 tasks exceeds max_tasks 4 for T2")

    def test_dependencies(self):
        p = valid_plan()
        p["blocks"][0]["depends_on"] = ["B09"]
        self.rejected(p, "B01: unknown dependency B09")
        p["blocks"][0]["depends_on"] = ["B03"]               # B01 → B03 → B02 → B01
        self.rejected(p, "dependency cycle")

    def test_status_and_tier_values(self):
        p = valid_plan()
        p["blocks"][0]["status"] = "wip"
        p["blocks"][1]["tier"] = "T9"
        self.rejected(p, 'B01: invalid status "wip"', "B02: unknown tier T9")

    def test_gate_pass_blocks_requires_valid_plan(self):
        self.assertEqual(self.cli("gate", "pass", "blocks").returncode, 1)       # aún no hay blocks.json
        self.write_json(".drydock/blocks.json", valid_plan())
        self.assertEqual(self.cli("gate", "pass", "blocks").returncode, 0)
        self.assertEqual(self.state()["phase"], "build")
