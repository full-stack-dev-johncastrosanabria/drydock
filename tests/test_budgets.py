import re
import unittest

from helpers import PHASES, ROOT

PHASE_FILES = [f"{i}-{p}.md" for i, p in enumerate(PHASES, 1)]
MODEL = re.compile(r"\b(opus|sonnet|haiku|fable)\b", re.I)

class BudgetTests(unittest.TestCase):
    def test_skill_md_budget(self):
        self.assertLessEqual(len((ROOT / "SKILL.md").read_text().splitlines()), 80)

    def test_phase_and_adapter_files(self):
        self.assertEqual(sorted(p.name for p in (ROOT / "phases").glob("*.md")), PHASE_FILES)   # glob: un .DS_Store no rompe el test
        for p in (ROOT / "phases").glob("*.md"):
            self.assertLessEqual(len(p.read_text().splitlines()), 120, p.name)
        for p in (ROOT / "adapters").glob("*.md"):
            self.assertLessEqual(len(p.read_text().splitlines()), 60, p.name)

    def test_no_model_names_outside_routing(self):
        scanned = [ROOT / "SKILL.md", *(ROOT / "phases").glob("*.md"), *(ROOT / "adapters").glob("*.md"), *(ROOT / "bin").glob("*.py"),
                   *(p for p in (ROOT / "templates").rglob("*") if p.is_file() and p.name != "routing.json"
                     and not p.name.startswith(".") and "__pycache__" not in p.parts)]
        for p in scanned:
            self.assertIsNone(MODEL.search(p.read_text()), p)

    def test_skill_frontmatter_matches_injection(self):
        text = (ROOT / "SKILL.md").read_text()
        front = text.split("---")[1]
        for line in ("name: drydock", "disable-model-invocation: true",
                     "allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/bin/drydock.py status*)"):
            self.assertIn(line, front.splitlines())
        self.assertRegex(front, r"(?m)^description: \S")
        self.assertIn("!`python3 ${CLAUDE_SKILL_DIR}/bin/drydock.py status --soft`", text)
