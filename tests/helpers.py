import json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "bin" / "drydock.py"
TEMPLATES = ROOT / "templates"
FIXTURES = ROOT / "tests" / "fixtures"
PHASES = ["requirements", "architecture", "audit", "prepare", "specs", "blocks", "build", "review"]
TS = r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$"

def run(cmd, cwd, stdin=None, env=None):
    env = {**os.environ, **(env or {}), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
           "XDG_CONFIG_HOME": os.devnull}            # sin el ~/.config/git/ignore del usuario
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(name, None)
    return subprocess.run([str(c) for c in cmd], cwd=str(cwd), input=stdin or "", capture_output=True, text=True, env=env)

class RepoCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()          # macOS: /var es un enlace a /private/var
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        for key, value in (("user.email", "t@example.invalid"), ("user.name", "T"), ("commit.gpgsign", "false")):
            self.git("config", key, value)
        self.commit("chore: seed", {"README.md": "seed\n"})

    def git(self, *args):
        r = run(["git", *args], self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def cli(self, *args, stdin=None, env=None):
        return run([sys.executable, CLI, *args], self.repo, stdin, env)

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def write_json(self, rel, obj): return self.write(rel, json.dumps(obj, indent=2) + "\n")
    def read_json(self, rel): return json.loads((self.repo / rel).read_text())
    def head(self): return self.git("rev-parse", "HEAD")
    def state(self): return self.read_json(".drydock/state.json")
    def set_state(self, **changes): self.write_json(".drydock/state.json", {**self.state(), **changes})

    def commit(self, message, files=None):
        for rel, text in (files or {}).items():
            self.write(rel, text)
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.head()

    def install_verify(self, config):                # copia los dos archivos, escribe verify.json y .gitignore, hace commit
        for src, dst in ((TEMPLATES / "verify.py", ".drydock/bin/verify.py"), (TEMPLATES / "verify.sh", "verify.sh")):
            (self.repo / dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, self.repo / dst)
        os.chmod(self.repo / "verify.sh", 0o755)
        self.write(".gitignore", ".drydock/local/\n")
        self.write_json(".drydock/verify.json", config)
        return self.commit("chore: harness")

    def set_verify(self, **changes):                 # mezcla claves en verify.json y hace commit
        self.write_json(".drydock/verify.json", {**self.read_json(".drydock/verify.json"), **changes})
        return self.commit("chore: verify config")

    def set_phase(self, phase, slice=None):          # salta a una fase: init si hace falta, gates anteriores cerrados
        if not (self.repo / ".drydock/state.json").exists():
            self.cli("init")
        closed = {"passed_at": "2026-01-01T00:00:00Z", "note": None}
        gates = {p: (dict(closed) if PHASES.index(p) < PHASES.index(phase) else None) for p in PHASES}
        self.set_state(phase=phase, gates=gates, slice=slice)

    def snapshot(self):                              # {ruta relativa: bytes} de todo lo que no es .git
        files = (p for p in sorted(self.repo.rglob("*")) if p.is_file())
        return {str(p.relative_to(self.repo)): p.read_bytes() for p in files if ".git" not in p.relative_to(self.repo).parts}
