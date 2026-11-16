# Revisión adversaria: revisor «executor» (2026-11-15)

Informe tal cual lo devolvió el revisor. Leyó el plan hasta T6B; T6C, T7 y T8 quedaron sin leer.

La herramienta `StructuredOutput` no existe en esta sesión (no está en la lista de herramientas ni en las diferidas), así que entrego los hallazgos como texto. Revisión parcial: leí el plan hasta la línea 1805 (fin de la Tarea 6B) de 2316; las Tareas 6C, 7 y 8 quedaron sin leer. Todo sale de lectura y razonamiento: no ejecuté nada y no comparé contra el v0.

## Hallazgos (más grave primero)

**1. Alta — B0 / T1 Paso 5 / Cierre de H1: `__pycache__` se versiona y ensucia el árbol**
- Cita: T1 Paso 4 corre `python3 -m unittest discover -s tests -p "test_state.py" -v` y el Paso 5 hace `git add templates tests && git commit -m "test(T1): state and base CLI"`. B0 no crea `.gitignore`. El cierre de H1 pone `"run": "python3 -m unittest discover -s tests"` como paso de verify, y A5 dice "`dirty` se calcula al final con `git status --porcelain`" y "Evidencia válida para PR: … `dirty = false`".
- Problema: la corrida de tests escribe `tests/__pycache__/*.pyc`, y `git add tests` (igual que los `git add -A` de T2, T5 y T6B) los versiona. Con el arnés propio instalado, el paso `unit` regenera esos `.pyc`, la evidencia queda con `dirty = true` y `pr_gate.py` niega todo `gh pr create` en el repo de astillero.
- Arreglo: añadir a B0, antes del primer commit: "Crear `.gitignore` con las líneas `__pycache__/` y `.astillero/local/`".
- Sin verificar: no busqué `__pycache__` en las líneas 1805–2316.

**2. Media — T1 Paso 4: `test_init_outside_git_fails` pasa antes de implementar**
- Cita: `self.assertEqual(run([sys.executable, CLI, "init"], d).returncode, 2)` y "Esperado: 11 fallos (`bin/astillero.py` no existe)".
- Problema: `python3 <archivo inexistente>` sale con código 2, así que este test pasa en vacío. El resultado real es 10 fallos y 1 éxito, y el rojo no prueba nada.
- Arreglo: reemplazar por
  ```python
  r = run([sys.executable, CLI, "init"], d)
  self.assertEqual(r.returncode, 2)
  self.assertIn("not a git repository", r.stderr)
  ```

**3. Media — T6B `block_step` contra T4 `pr_gate.py`: SHA abreviado contra SHA completo**
- Cita: `f"dispatch the reviewer, then astillero.py review record {block_id} --sha {head[:12]}"`; el gate busca `.astillero/local/reviews/<block>-<head>.md` con `head = git rev-parse HEAD`.
- Problema: si `review record` nombra el archivo con el `--sha` recibido tal cual (12 caracteres), el hook y `review_verdict` no lo encuentran y el PR queda negado.
- Arreglo: imprimir `{head}` completo en `block_step`, o fijar en T8 que `review record` normaliza con `git rev-parse --verify <sha>^{commit}`.
- Sin verificar: T8 no leída; puede que ya normalice.

**4. Media — T3 `red_first`: `KeyError` con una configuración que el contrato admite**
- Cita: A5 dice "`base_branch` (por defecto `main`), `src_globs`, `test_globs` y `red` opcionales"; el código usa `config["test_globs"]` y `config["src_globs"]`.
- Problema: un `verify.json` con `red` y sin globs revienta con traza, sale 1 sin evidencia y parece un paso fallido. Ningún test lo cubre.
- Arreglo: en `load_config`, salir 2 con `verify: config error: "red" requires src_globs and test_globs`, o usar `config.get("test_globs", [])` y `config.get("src_globs", [])`.

**5. Media — T5 Paso 5 y T6B: mensajes de `doctor` y del gate `build` sin fijar**
- Cita: los tests exigen `"pr_gate"`, `"onFailure"`, `"gh pr merge"` y `".astillero/local"` en stdout, y `"B01"` en stderr. El plan solo describe en español: "no hay hook `PreToolUse` que nombre `pr_gate.py` · ese hook no lleva `"onFailure": "block"` · falta alguna de las tres reglas `ask`…" y "falta blocks.json, hay bloque en curso o alguno no está done".
- Problema: dos implementadores escriben textos distintos y los tests fallan por subcadena.
- Arreglo: fijar una tabla como la de B3:
  - `error: no PreToolUse hook runs .astillero/bin/pr_gate.py`
  - `error: the pr_gate.py hook lacks "onFailure": "block"`
  - `error: missing permissions.ask rule <regla>`
  - `error: .astillero/local is tracked by git`
  - `error: block <id> is <status>`
  - `error: block <id> is still in progress`

**6. Media — Cierre de H1 / B0: red-first no evalúa nada en el repo propio**
- Cita: B0 dice "Es el mismo ciclo que `red-first` exigirá cuando el repo se instale su propio arnés"; A5 dice "recorre los commits de `base..HEAD`"; T6A y T6B hacen commit directo (`git add tests && git commit …`) sin crear rama.
- Problema: sobre `main`, `base..HEAD` está vacío (es lo que fija `test_base_branch_itself_passes`), así que red-first pasa siempre. Además cada `git push` a `main` dispara el `ask` del hook.
- Arreglo: añadir al cierre de H1 "Desde aquí cada tarea se trabaja en `task/T<n>` y entra por PR", o decir que el repo de astillero no queda sujeto a red-first.
- Sin verificar: líneas 1805–2316.

**7. Baja — T6A: `validate_blocks` "nunca lanza" contra `load_blocks`, que sí lanza**
- Cita: `def load_blocks(root: Path) -> dict  # CliError(1, "no block plan: .astillero/blocks.json")`, `def validate_blocks(root: Path) -> list  # mensajes de B3; nunca lanza`, y `test_gate_pass_blocks_requires_valid_plan` espera 1 sin `blocks.json`.
- Problema: no dice qué devuelve `validate_blocks` sin plan, con JSON roto o sin `tasks_file`. Un implementador que deje propagar el error puede romper `gate pass`.
- Arreglo: añadir "`validate_blocks` captura `CliError`, `OSError` y `ValueError` y los devuelve como único elemento de la lista (`no block plan: …`, `tasks file not found: <ruta>`)".

**8. Baja — T1 necesita la ruta de plantillas que T5 define**
- Cita: T5 produce `def templates_dir() -> Path  # Path(__file__).resolve().parent.parent / "templates"`; el `init` de T1 ya debe copiar `routing.json` (`test_init_creates_state` lo compara con `TEMPLATES / "routing.json"`).
- Arreglo: mover `templates_dir()` al bloque Interfaces de T1 y quitarlo del de T5.

**9. Baja — `tests/helpers.py::run`: aislamiento incompleto**
- Cita: `env = {**os.environ, **(env or {}), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}`, `subprocess.run(…, input=stdin, …)`, y `doctor` "leyendo … `~/.claude/settings.json`".
- Problema:
  - `GIT_DIR`, `GIT_WORK_TREE` y `GIT_INDEX_FILE` heredados apuntarían al repo real.
  - `~/.config/git/ignore` se sigue leyendo aunque `GIT_CONFIG_GLOBAL` sea el dispositivo nulo. Sin verificar en esta máquina.
  - `doctor` lee el `~/.claude/settings.json` real.
  - Con `stdin=None` el hijo hereda el stdin del runner; un comando que lea stdin se cuelga.
- Arreglo: en `run`, quitar `GIT_DIR`, `GIT_WORK_TREE` y `GIT_INDEX_FILE` del entorno, fijar `HOME` y `XDG_CONFIG_HOME` a un directorio temporal vacío, y pasar `stdin=subprocess.DEVNULL` cuando `stdin is None`.

**10. Baja — T2 `test_budgets.py`: se rompe con archivos ajenos**
- Cita: `self.assertEqual(sorted(p.name for p in (ROOT / "phases").iterdir()), PHASE_FILES)` y `p.read_text()` sobre `(ROOT / "templates").rglob("*")`.
- Problema: un `.DS_Store` (macOS) hace fallar la lista o lanza `UnicodeDecodeError`.
- Arreglo: usar `glob("*.md")` en `phases` y `adapters`, y filtrar en templates con `not p.name.startswith(".") and "__pycache__" not in p.parts`.

**11. Baja — B1 contra T6B: la CLI toca más red que `gh`**
- Cita: B1 dice "La única red que toca la CLI es `gh` (`block merge`, y `block close` sin `--merged-sha`)"; T6B dice "`git fetch origin <base>`" y "`git pull --ff-only origin <base>`". T5 Paso 4 además pide `gh api repos/actions/checkout/releases/latest` durante la implementación.
- Arreglo: corregir B1 a "`gh` y `git fetch`/`git pull` contra `origin` en `block close`".

## Lo que revisé y no dio hallazgos

- Conteos y totales 11, 15, 33, 47, 58, 70 y 76: coinciden.
- Aserciones de subcadena de T3, T4 y T6B contra los mensajes fijados: coinciden.
- Comportamiento de git que usan T3 y T6B: no vi fallos.
- Python 3.9 y portabilidad de shell: sin problemas.

## Lo que no revisé

- Tareas 6C, 7 y 8 completas: `FakeGh`, `fake_gh.py`, el `PATH` con el gh falso, `ASTILLERO_POLL_SECONDS`, y los totales 84, 90 y 96.
- Si T7 añade chequeos de agentes a `doctor` que rompan `test_doctor_ok` o `test_gate_pass_prepare_runs_doctor`.
- Las expresiones `SEP`, `PR_RE` y `PUSH_RE`: las repasé a mano, no las ejecuté.

### Critical Files for Implementation
- /Users/johnbenjamincastrosanabria/.claude/plans/users-johnbenjamincastrosanabria-downlo-smooth-church.md
- /Users/johnbenjamincastrosanabria/Developer/astillero/tests/helpers.py (por crear)
- /Users/johnbenjamincastrosanabria/Developer/astillero/bin/astillero.py (por crear)
- /Users/johnbenjamincastrosanabria/Developer/astillero/templates/verify.py (por crear)
- /Users/johnbenjamincastrosanabria/Developer/astillero/templates/pr_gate.py (por crear)
