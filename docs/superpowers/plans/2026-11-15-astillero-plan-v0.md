# Astillero — Plan de implementación v0 (para refinar)

> **Para Claude Code:** esto es un borrador de trabajo. **Primero refínalo** siguiendo la sección 0 y no escribas código hasta que John apruebe el plan refinado. Para ejecutarlo después usa `superpowers:subagent-driven-development` (recomendado) o `superpowers:executing-plans`. Las tareas usan casillas (`- [ ]`).

**Objetivo:** un skill personal, `/astillero`, que lleva un producto de software de la idea al código integrado y revisado: estado en archivos, modelo y esfuerzo asignados por complejidad, y gates que se exigen con código.

**Arquitectura:** dos capas. El **skill** es un router corto que lee el estado del repo y carga solo la fase en curso; trae una CLI en Python y plantillas. El **arnés por repo** son archivos versionados dentro de cada producto (`verify.sh`, hook de PR, agentes, estado) que siguen funcionando aunque el skill no esté instalado. Spec Kit genera constitution/spec/plan/tasks sin modificarse.

**Stack:** Markdown (skill y fases) · Python 3 con solo librería estándar (CLI y gates) · JSON (estado y configuración) · `git`, `gh` · Spec Kit · Claude Code.

**Spec:** no existe documento aparte. La Parte A es el diseño v0 y viaja con el plan.

## Resumen para John

- **Qué es:** `/astillero` lee en qué fase está el repo, carga solo esa fase y no deja avanzar sin cerrar su gate.
- **Tus 10 ideas** quedaron en 8 fases (tabla en A3). Ninguna se perdió.
- **Cinco cambios respecto a tu lista**, todos discutibles (A2):
  1. Un skill con archivos de apoyo, no un plugin.
  2. Spec Kit tal cual, sin fork ni preset.
  3. Niveles T1–T3 en un archivo, en vez de nombres de modelo dentro del texto.
  4. El repo se prepara antes de las specs, y el esqueleto andante es la primera rebanada.
  5. Verify rápido antes del revisor y verify completo después.
- **Se construye primero** lo determinista (verify, evidencia, hook de PR, CI): sirve desde el primer día en cualquier repo tuyo, aunque el resto no exista.
- **Te toca decidir** lo de A8: 10 puntos, cada uno con mi recomendación.

## 0. Cómo refinar este plan (Claude Code)

1. **Lee el entorno real** antes de opinar: `claude --version`, skills y plugins instalados, `specify --help`, `python3 --version`, `gh --version`, sistema operativo.
2. **Comprueba cada `[VERIFICAR]`** (lista en B5) contra la documentación oficial vigente y corrige el plan donde difiera. Lo que aparece como verificado se consultó el 2026-11-15; reconfírmalo contra la versión instalada.
3. **Cuestiona D1–D12** (A2). Di cuáles cambiarías y por qué; no las aceptes por defecto. Regla de John: la complejidad se añade solo ante un fallo demostrado.
4. **Resuelve A8 con John**, una decisión por mensaje.
5. **Baja H0–H2 a pasos TDD** (test → verlo fallar → implementación mínima → verlo pasar → commit) con firmas y aserciones exactas. H3–H6 pueden quedarse como contrato hasta cerrar H2.
6. **Entrega** el plan v1 en `docs/superpowers/plans/` del repo `astillero`, con la lista de cambios respecto a este v0.

Para redactar las fases usa `superpowers:writing-skills`: cada regla de una fase debe responder a un fallo observado en una corrida sin el skill.

---

## Parte A — Diseño v0

### A1. Alcance

- **Es:** un flujo por fases con estado en archivos, un arnés de gates por repo y un ruteo de modelo/esfuerzo por complejidad, para uso personal de John en Claude Code.
- **No es:** un reemplazo de Spec Kit, un framework multiagente ni un sistema de despliegue. V1 no ejecuta bloques en paralelo.
- **Sería un fracaso aunque funcione si:** el arnés pesa más que el producto; una regla depende de que el modelo se acuerde; aparece un nombre de modelo fuera de `routing.json`; conviven dos cadenas de specs y planes en el mismo repo.
- **"100" significa:** todas las rebanadas del brief integradas en la rama principal, `./verify.sh` en verde, revisión final sin bloqueantes y arranque reproducible desde un clon limpio. El despliegue a un servidor real queda fuera de V1 (A8-2).

### A2. Decisiones tomadas

| # | Decisión | Razón | Alternativa descartada |
|---|---|---|---|
| D1 | Un skill personal con archivos de apoyo en `~/.claude/skills/astillero/` | Es lo mínimo que da `/astillero`, estado y plantillas. Hooks y agentes viven en el repo del producto, no en el skill | Plugin con marketplace: sobra hasta que haya que distribuirlo |
| D2 | Dos capas: el skill orquesta, el arnés del repo exige | El repo queda autosuficiente: CI, Codex u otra máquina respetan los mismos gates | Gates dentro del skill: desaparecen al cambiar de herramienta |
| D3 | Spec Kit sin fork y sin preset | Astillero solo lee sus artefactos. Un preset se añade si una plantilla demuestra quedarse corta | Fork: obliga a seguir al upstream a mano |
| D4 | Estado en JSON versionado más `PROJECT_STATE.md` generado | Reanudar tras un corte de sesión o un salto a Codex sin depender del chat | Estado en la conversación |
| D5 | Ruteo por niveles en `routing.json`; ningún nombre de modelo en prosa | Cambiar de modelo es editar un archivo. Respeta "no fijar la arquitectura a un modelo" | "Opus xhigh" escrito en el skill |
| D6 | Lo exigible se exige con código; la prosa solo guía | Una instrucción se sigue casi siempre; un hook se ejecuta siempre | TDD y verify como reglas de CLAUDE.md |
| D7 | Orden por bloque: TDD → verify rápido → revisión → verify completo → PR | No se gasta revisor en código que no compila, y el último gate es determinista | Revisión antes de cualquier verify (idea original; ver A8-3) |
| D8 | Un solo proceso rector por repo; skills externas a la carta, máximo 5 | Los paquetes con flujo propio compiten por dirigir la sesión | Instalar varios paquetes completos |
| D9 | John aprueba: brief, stack, hallazgos de auditoría, plan de bloques, cada merge, hallazgos finales | Control humano en los puntos irreversibles o caros | Autonomía total |
| D10 | Construir primero gates, luego bloques y ruteo, luego el frente | Lo determinista da valor desde el día 1; el frente ya funciona a mano con Spec Kit | Construir en orden de fase |
| D11 | Preparar el repo antes de las specs; el esqueleto andante es la primera rebanada | La constitution cita gates que ya existen, y el flujo completo se prueba con algo trivial | Arnés después de tasks |
| D12 | Python 3 con librería estándar y JSON | Cero instalación en cualquier máquina o runner | Bash con `jq`; YAML |

### A3. Flujo de fases

```
requisitos → arquitectura → auditoria → preparar → [ specs → bloques → construir ]* → revision
                                                     └──── una vuelta por rebanada ────┘
```

| # | Fase | Hace | Produce | Cierra el gate |
|---|---|---|---|---|
| 1 | `requisitos` | Interrogatorio de una pregunta a la vez hasta agotar el árbol de decisiones | `docs/astillero/brief.md`: problema, usuarios, alcance, fuera de alcance, criterios de éxito medibles, restricciones y rebanadas verticales en orden (la 0 es el esqueleto andante) | John aprueba el brief |
| 2 | `arquitectura` | Consulta guiada: máquina de desarrollo, destino de despliegue, lenguajes y frameworks con versión exacta, BD y migraciones, estilo (Clean, hexagonal, monolito modular), módulos, pruebas, CI/CD | `docs/astillero/stack.md` (componente, versión fijada, fuente oficial, fecha de consulta, fin de soporte) y un ADR por decisión en `docs/adr/` | John aprueba el stack |
| 3 | `auditoria` | Un agente con contexto limpio evalúa el stack contra la rúbrica de abajo y propone cambios | `docs/astillero/auditoria.md`: hallazgo, severidad, evidencia con fuente, cambio propuesto, decisión de John | 0 bloqueantes abiertos |
| 4 | `preparar` | Instala el arnés, genera los agentes, elige skills, escribe `AGENTS.md`, `CLAUDE.md` y `CLAUDE.local.md` | Arnés (A6) y `docs/astillero/skills.md` | `astillero.py doctor` sale 0 |
| 5 | `specs` | Constitution una sola vez; por rebanada: specify → clarify → plan → tasks → analyze con Spec Kit | `specs/<rebanada>/{spec,plan,tasks}.md` | Analyze sin críticos y John aprueba la spec |
| 6 | `bloques` | Puntúa cada tarea, agrupa en bloques y asigna nivel | `.astillero/blocks.json` | `blocks validate` sale 0 y John aprueba el plan de bloques |
| 7 | `construir` | Por bloque: TDD → verify rápido → revisión independiente → verify completo → PR | Un PR por bloque y `metrics.jsonl` | Todos los bloques en `done`; John elige otra rebanada (→ 5) o revisión (→ 8) |
| 8 | `revision` | Revisión global, arranque desde clon limpio y retro | `docs/astillero/revision-final.md` y entradas en `LEARNINGS.md` | 0 bloqueantes y `clean-clone` sale 0 |

**Rúbrica de la auditoría (fase 3):** compatibilidad entre versiones (framework, runtime, driver, BD, imagen base) · soporte y fin de vida · ajuste al problema (¿la arquitectura excede el alcance del brief?) · viabilidad en la máquina de desarrollo y en el destino · estrategia de migraciones y datos · testabilidad por capa · seguridad base · operabilidad. Cada hallazgo es bloqueante, mayor o menor.

**Revisión final (fase 8):** trazabilidad requisito → test · conformidad con las reglas de capas · seguridad básica · sobreingeniería (lista de borrado) · arranque y migraciones desde cero · deuda. Cada hallazgo termina en bloque de corrección, pendiente o riesgo aceptado, a decisión de John.

**Dónde quedó cada idea tuya:**

| Tu idea | Dónde quedó |
|---|---|
| 1 Requerimientos y grilling | Fase 1 |
| 2 Consultar arquitectura | Fase 2 |
| 3 Evaluar y proponer cambios | Fase 3 |
| 4 Constitution, specs, plan, tasks | Fase 5 (Spec Kit sin fork) |
| 5 Bloques con modelo y esfuerzo | Fase 6 y `routing.json` |
| 6 Skills del repo | Fase 4 (criterios en A7) |
| 7 TDD, `verify.sh`, revisión independiente | Se instalan en la fase 4 y se ejercen en la 7 (A5) |
| 8 CLAUDE.md y local | Fase 4 |
| 9 Implementar por bloques | Fase 7 |
| 10 Review completa | Fase 8 |

### A4. Bloques y ruteo

`routing.json` es el único lugar con nombres de modelo:

```json
{
  "version": 1,
  "tiers": {
    "T1": {"model": "sonnet", "effort": "medium", "max_tasks": 8},
    "T2": {"model": "sonnet", "effort": "high", "max_tasks": 4},
    "T3": {"model": "opus", "effort": "xhigh", "max_tasks": 1}
  },
  "roles": {
    "revisor": {"model": "sonnet", "effort": "medium"},
    "revisor-t3": {"model": "opus", "effort": "high"},
    "auditor": {"model": "opus", "effort": "xhigh"},
    "revisor-final": {"model": "opus", "effort": "high"}
  }
}
```

T1 y T3 son tus dos ejemplos. T2 es mío, para lo que no es rutina ni crítico.

**Puntuación por tarea** (0–2 por dimensión, total 0–10):

| Dimensión | 0 | 1 | 2 |
|---|---|---|---|
| `novedad` | patrón ya presente en el repo | variación de un patrón | diseño o algoritmo nuevo |
| `alcance` | un módulo, una capa | 2–3 módulos o capas | transversal |
| `riesgo` | reversible, sin datos | toca datos o contratos públicos | dinero, autenticación, concurrencia, migraciones destructivas |
| `prueba` | unitaria pura | integración | E2E, infraestructura o tiempo |
| `ambiguedad` | spec cerrada | un supuesto por confirmar | decisiones de diseño abiertas |

Nivel por total: 0–3 → T1, 4–6 → T2, 7–10 → T3. `riesgo = 2` fuerza T2 como mínimo. El nivel del bloque es el de su tarea más alta.

**Reglas de formación:**

1. Un bloque agrupa tareas del mismo nivel y del mismo módulo, en orden de dependencia.
2. Tamaño máximo por nivel: sale de `max_tasks`.
3. Cada bloque termina con `./verify.sh` en verde y un diff que un revisor pueda leer de una sentada.
4. Subir de nivel exige `tier_override` con motivo. Bajar no se permite.

La puntuación la propone un modelo y es falible; la estructura la valida la CLI y el plan lo aprueba John.

**Agentes** (generados en `.claude/agents/` del producto a partir de `routing.json`):

| Agente | Sale de | Restricciones |
|---|---|---|
| `astillero-impl-t1`, `-t2`, `-t3` | `tiers` | Sin `Agent`; no abre PR; termina con `./verify.sh --fast` en verde |
| `astillero-revisor`, `astillero-revisor-t3` | `roles` | Sin `Write`, `Edit` ni `Agent`; su respuesta empieza con `verdict: approve` o `verdict: changes` |
| `astillero-auditor` | `roles` | Sin `Write` ni `Edit`; con búsqueda web para comprobar versiones |
| `astillero-revisor-final` | `roles` | Sin `Write` ni `Edit` |

El orquestador despacha estos agentes **sin pasar `model` ni `effort`**: un parámetro en el despacho gana al frontmatter y rompería el ruteo.

### A5. Gates

| Se exige | Mecanismo que no depende del modelo | V1 |
|---|---|---|
| `verify.sh` antes de cada PR | Un hook `PreToolUse` niega `gh pr create` sin evidencia para el commit actual. CI corre el mismo script como check requerido | Sí |
| Revisión independiente antes del PR | El mismo hook exige un veredicto `approve` registrado para el commit actual | Sí, desde H2 |
| TDD | L0: prosa en el agente implementador. **L1:** paso `tests-touched` en verify (cambió código y ningún test → falla). L2: el test nuevo debe fallar en el commit previo a la implementación | L0 + L1. L2 solo si el piloto muestra que L1 no basta |
| Reglas de capas | Tests de arquitectura dentro de verify (ArchUnit, NetArchTest, dependency-cruiser o import-linter, según stack) | Sí, desde el esqueleto |
| Ruteo | Agentes generados desde `routing.json`; `doctor` detecta deriva y variables de entorno que lo pisan | Sí |
| Versiones reales | `stack.md` exige URL oficial y fecha por versión; la auditoría las recomprueba | Sí |

**Orden dentro de un bloque:**

1. `astillero.py block start <id>` y rama `bloque/<id>`.
2. Implementador del nivel del bloque. Por tarea: test, verlo fallar, implementación mínima, verlo pasar, commit `feat(<bloque>/<tarea>): …`.
3. `./verify.sh --fast`. Si falla, vuelve al implementador. Tras 2 reintentos sube un nivel una sola vez; si falla de nuevo, se detiene y pregunta a John.
4. Revisor con contexto limpio. Recibe el id del bloque, los criterios de aceptación, la constitution y el comando del diff. No recibe el relato del implementador.
5. `astillero.py review record` guarda el veredicto. Si es `changes`: corrección y nueva revisión del delta, máximo 2 rondas; después decide John.
6. `./verify.sh` completo sobre el commit aprobado. Si falla: corrección y vuelta al paso 4.
7. `gh pr create` con cuerpo generado (tareas, veredicto, hallazgos, resumen de verify). El hook comprueba evidencia y veredicto.
8. John hace merge. `astillero.py block close <id> --merged-sha <sha>` registra métricas.

**Invariante:** entre el veredicto `approve`, el verify completo y la creación del PR no entra ningún commit. Por eso evidencia y veredictos viven en `.astillero/local/` (sin versionar) y su contenido se copia al cuerpo del PR.

**Dónde se versiona el estado:** `block start` es el primer commit de la rama del bloque. `block close` se versiona junto con el `block start` del bloque siguiente, y el del último bloque junto con el cierre de la fase.

**Contrato de `verify.sh`:**

- Uso: `./verify.sh [--fast]`. Lee `.astillero/verify.json`.
- Ejecuta los pasos en orden y corta en el primer fallo. `--fast` omite los pasos con `"mode": "full"`.
- Paso interno `tests-touched`, solo en modo completo: compara contra la base de la rama; si cambió algún archivo de `src_globs` y ninguno de `test_globs`, falla.
- Escribe `.astillero/local/evidence/<sha>.<fast|full>.json` con `sha`, `mode`, `result`, `dirty`, `steps[{name, exit, seconds}]` y `finished_at`.
- Salida: 0 pasa · 1 falla un paso · 2 error de configuración.
- Evidencia válida para PR: `mode = full`, `result = pass`, `dirty = false`, `sha = HEAD`.

Ejemplo de `verify.json` (comandos `[VERIFICAR]` por stack):

```json
{
  "src_globs": ["src/**"],
  "test_globs": ["tests/**"],
  "steps": [
    {"name": "formato", "mode": "fast", "run": "dotnet format --verify-no-changes"},
    {"name": "build", "mode": "fast", "run": "dotnet build -warnaserror"},
    {"name": "unit", "mode": "fast", "run": "dotnet test --filter Category!=Integration"},
    {"name": "integracion", "mode": "full", "run": "dotnet test --filter Category=Integration"}
  ]
}
```

**Contrato de `pr_gate.py`** (hook `PreToolUse` sobre `Bash`):

- Lee el JSON del hook por stdin y toma `tool_input.command` y `cwd`.
- Si el comando no contiene `gh pr create` (también dentro de un comando compuesto): sale 0 sin escribir nada.
- Si el repo no tiene `.astillero/`: sale 0 sin escribir nada.
- Resuelve la raíz con `git -C <cwd> rev-parse --show-toplevel`, no con `CLAUDE_PROJECT_DIR`, que no cambia dentro de un worktree.
- Permite solo si hay evidencia válida para `HEAD` y, cuando `state.current_block` no es nulo, un veredicto `approve` en `.astillero/local/reviews/<bloque>-<sha>.md`.
- Para negar imprime esto y sale 0:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Falta verify completo para este commit. Corre ./verify.sh"
  }
}
```

- Ante un error interno con un comando de PR, niega (falla cerrado).
- El hook es respuesta rápida para el agente. La autoridad es CI como check requerido en la rama principal.

### A6. Arnés por repo

```
<producto>/
├── verify.sh                      # envoltorio: python3 .astillero/bin/verify.py "$@"
├── AGENTS.md                      # reglas compartidas por cualquier agente
├── CLAUDE.md                      # @AGENTS.md + lo propio de Claude Code
├── CLAUDE.local.md                # personal, sin versionar
├── PROJECT_STATE.md               # generado: fase, bloque y qué sigue
├── .astillero/
│   ├── state.json  routing.json  blocks.json  verify.json  metrics.jsonl
│   ├── bin/verify.py  bin/pr_gate.py
│   └── local/                     # sin versionar: evidence/ y reviews/
├── .claude/
│   ├── settings.json              # hook PreToolUse → pr_gate.py
│   └── agents/astillero-*.md      # generados desde routing.json
├── .github/workflows/verify.yml   # corre ./verify.sh en cada PR
├── .specify/  specs/              # Spec Kit
└── docs/astillero/  docs/adr/
```

- `AGENTS.md`, máximo 60 líneas: comandos (build, test, run, verify), reglas de capas, convención de ramas y commits, dónde están specs y ADR, qué no hacer.
- `CLAUDE.md` importa `@AGENTS.md` y añade: el flujo lo dirige `/astillero`; de superpowers se usan solo `test-driven-development` y `systematic-debugging`; no se abre PR sin verify.
- `CLAUDE.local.md`: preferencias personales y límites de la máquina (por ejemplo, cuántos contenedores aguanta a la vez).
- `PROJECT_STATE.md` se regenera desde `state.json` y `blocks.json`; nadie lo edita a mano. Incluye la siguiente acción y el comando de la CLI, para que Codex pueda retomar.

### A7. Curaduría de skills (fase `preparar`)

Reglas: astillero es el único proceso rector · máximo 5 skills externas por repo · se instala la skill suelta, no el paquete · cada elección se anota en `docs/astillero/skills.md` con origen, versión y motivo.

| Necesidad | Elección por defecto | Cuándo | Nota |
|---|---|---|---|
| Interrogatorio | `grill-with-docs` (mattpocock/skills) o el bucle propio de la fase 1 | Siempre | Deja glosario y ADR mientras pregunta |
| Cadena de artefactos | Spec Kit | Siempre | Sin fork ni preset |
| TDD y depuración | `test-driven-development` y `systematic-debugging` de superpowers | Siempre | Solo como librería; su flujo brainstorming → plan duplicaría a Spec Kit |
| Sobreingeniería | `ponytail-review` | Fase 8; opcional en bloques T1 | Prueba independiente de JetBrains con 80 tareas pareadas: mediana de −15 % de código y −10,3 % de costo, sin diferencia significativa de calidad |
| Diseño de front | impeccable | Solo si hay interfaz | Un skill con 23 comandos |
| Rúbrica de revisión | `code-review-and-quality` (addyosmani/agent-skills) | Opcional, como guía del revisor | Sin instalar las 24 skills |
| Documentación oficial | Microsoft Learn MCP para .NET, Azure y SQL Server; el equivalente del stack | Fases 2 y 3 | Las versiones se comprueban en la fuente, no de memoria |
| E2E | Playwright dentro de verify completo | Si hay web | |
| pstack | No instalar; tomar ideas (`architect`, modelo por rol) | — | Trae su propio enrutado al iniciar sesión y competiría |
| ECC | No instalar completo | — | 68 subagentes y 386 skills y comandos: demasiado contexto |
| tgrep | No | Solo en repos enormes | Índice de trigramas pensado para cientos de miles de archivos |

Ideas propias, para después del piloto: skills locales creadas por "regla de tres" (un procedimiento que se repite tres veces en un repo se vuelve skill en `.claude/skills/`) y segunda revisión con Codex en bloques T3, para no repetir los puntos ciegos de una sola familia de modelos.

### A8. Decisiones abiertas (son de John)

| # | Decisión | Recomendación |
|---|---|---|
| 1 | Nombre | `astillero` (alternativa: `drydock`) |
| 2 | Alcance del "100" | Hasta rama principal verde y arranque reproducible; despliegue real fuera de V1 |
| 3 | Orden revisión/verify | Verify rápido → revisión → verify completo. Tu idea original era revisión → verify |
| 4 | Revisor en bloques T3 | Escalarlo (`revisor-t3`). Tu regla era Sonnet medium siempre |
| 5 | Merge | Siempre humano en V1; auto-merge de T1 con CI verde, más adelante |
| 6 | Stack del piloto | El primero define qué plantilla de verify se escribe antes |
| 7 | superpowers en repos gestionados | Mantenerlo y usar solo TDD y depuración |
| 8 | Idioma de nombres | Fases en español, CLI en inglés |
| 9 | Codex en V1 | Solo estado, `verify.sh` y `AGENTS.md`; el skill completo en Codex, después |
| 10 | Exigencia de TDD | L1 al inicio |

### A9. Fuera de V1 y qué lo activaría

| No se construye | Se añade cuando |
|---|---|
| Plugin y marketplace | Haga falta instalarlo en otra cuenta o equipo |
| Preset de Spec Kit | Una plantilla de Spec Kit obligue a corregir a mano dos veces |
| Bloques en paralelo con worktrees | El tiempo de pared sea el cuello de botella |
| Hook sobre el despacho de agentes | Se observe un despacho con `model` o `effort` distintos al ruteo |
| TDD nivel L2 | El piloto muestre tests escritos después del código |
| Estado inyectado al iniciar sesión | Retomar un repo cueste más de un comando |

---

## Parte B — Plan de construcción

### B1. Restricciones globales

- Python 3.9 o superior, solo librería estándar. Sin `pip`, sin `jq`, sin YAML.
- Ningún nombre de modelo fuera de `plantillas/routing.json` (lo comprueba un test).
- `SKILL.md` ≤ 80 líneas; cada archivo de `fases/` ≤ 120; `AGENTS.md` y `CLAUDE.md` generados ≤ 60 cada uno.
- Tras `preparar`, los gates del repo funcionan sin el skill instalado.
- Evidencia y veredictos nunca se versionan y siempre van atados al SHA de `HEAD`.
- Spec Kit no se modifica.
- `harness install` nunca pisa un archivo existente sin `--force` y conserva lo que ya haya en `.claude/settings.json`.
- Tests con `python3 -m unittest discover -s tests -v`. Cada test crea su repo git temporal.
- Textos en español; identificadores de código en inglés.

### B2. Foco de revisión

Fallos que el diseño implica y que ningún test cubriría por defecto. Cada uno ya tiene su test en la tarea dueña.

1. **PR abierto por una vía que el hook no ve** (comando compuesto, push más interfaz web). Se espera que CI lo detenga igual. → `test_compound_command_detected` (T4) y check requerido en la aceptación de H1.
2. **Evidencia que no corresponde al árbol real** (commit posterior, árbol sucio, subcarpeta o worktree). Se espera negación. → `test_stale_evidence_denied`, `test_dirty_tree_marks_dirty`, `test_cwd_subdirectory` (T3, T4).
3. **Ruteo pisado** por variables de entorno o por parámetros en el despacho. Se espera aviso. → `test_doctor_warns_env_override` (T5) y escenario 07.
4. **`tasks.md` con formato distinto o tareas sin asignar.** Se espera error con la lista exacta. → `test_all_tasks_assigned` con dos fixtures (T6).
5. **Sesión cortada a mitad de bloque.** Se espera que `status` diga rama, bloque y siguiente paso. → `test_status_mid_block_shows_next_action` (T6).

### B3. Estructura de archivos (repo `astillero`)

```
astillero/                          # enlazado a ~/.claude/skills/astillero
├── SKILL.md                        # router: inyecta el estado y carga la fase
├── fases/
│   ├── 1-requisitos.md  2-arquitectura.md  3-auditoria.md  4-preparar.md
│   └── 5-specs.md  6-bloques.md  7-construir.md  8-revision.md
├── bin/astillero.py                # CLI única
├── plantillas/
│   ├── routing.json  settings.json  verify.sh  verify.py  pr_gate.py
│   ├── verify-steps/{dotnet,spring-maven,node-ts,python}.json
│   ├── agents/{impl,revisor,auditor,revisor-final}.md.tmpl
│   ├── ci/github-actions.yml
│   ├── AGENTS.md.tmpl  CLAUDE.md.tmpl  CLAUDE.local.md.tmpl
│   └── docs/{brief,stack,auditoria,adr,skills,revision-final}.md
├── tests/                          # unittest
├── escenarios/                     # pruebas de las fases en prosa
├── verify.sh  .astillero/verify.json   # el propio repo pasa por su gate
├── README.md
└── LEARNINGS.md                    # fallo observado → cambio hecho
```

Cada archivo de `fases/` tiene las mismas secciones: propósito, entradas, pasos, salidas, gate, errores frecuentes.

**Interfaz de la CLI** (`python3 bin/astillero.py <comando>`):

| Comando | Efecto | Salida |
|---|---|---|
| `init` | Crea `.astillero/state.json` y `routing.json`; añade `.astillero/local/` a `.gitignore` | 0 · 1 ya inicializado · 2 no es repo git |
| `status [--json] [--soft]` | Fase, gates, rebanada, bloque y siguiente acción. `--soft` nunca falla | 0 · 2 sin inicializar |
| `gate pass <fase> [--nota T] [--next specs\|revision]` | Cierra el gate de la fase actual y avanza. `--next` es obligatorio en `construir` | 0 · 1 fase incorrecta o falta `--next` |
| `slice set <id>` | Fija la rebanada en curso; solo en fase `specs` | 0 · 1 |
| `render-state` | Regenera `PROJECT_STATE.md` | 0 |
| `harness install --stack <s> [--force]` | Copia el arnés al repo y fusiona el hook | 0 · 1 |
| `doctor` | Comprueba arnés, hook, agentes y variables de entorno | 0 con o sin avisos · 1 con errores |
| `blocks validate` | Valida `blocks.json` | 0 · 1 con lista de errores |
| `agents render` | Escribe `.claude/agents/astillero-*.md` | 0 |
| `block start <id>` / `block close <id> --merged-sha <sha> [--intentos N] [--hallazgos N]` | Mueve el estado del bloque; `close` añade una línea a `metrics.jsonl` | 0 · 1 |
| `review record <id> --verdict approve\|changes --sha <sha>` | Guarda el veredicto leído por stdin | 0 · 1 si `sha` no es `HEAD` |
| `clean-clone` | Clona a un directorio temporal y corre `./verify.sh` | Código de verify |

`state.json`:

```json
{
  "version": 1,
  "phase": "requisitos",
  "gates": {
    "requisitos": null, "arquitectura": null, "auditoria": null, "preparar": null,
    "specs": null, "bloques": null, "construir": null, "revision": null
  },
  "slice": null,
  "slices_done": [],
  "current_block": null
}
```

Un gate cerrado guarda `{"passed_at": "<ISO 8601>", "nota": "<texto o null>"}`. Tras `revision`, `phase` pasa a `cerrado`.

`blocks.json`:

```json
{
  "version": 1,
  "slice": "001-esqueleto",
  "base_branch": "main",
  "tasks_file": "specs/001-esqueleto/tasks.md",
  "blocks": [
    {
      "id": "B01",
      "title": "Esqueleto andante y arnés",
      "tier": "T2",
      "tier_override": null,
      "depends_on": [],
      "status": "pending",
      "tasks": [
        {"id": "T001", "score": {"novedad": 1, "alcance": 2, "riesgo": 0, "prueba": 1, "ambiguedad": 0}}
      ]
    }
  ]
}
```

Reglas de `blocks validate`: (1) ids de bloque y de tarea únicos, cada tarea en un solo bloque; (2) toda tarea de `tasks_file` (ids `T` + 3 o más dígitos) está asignada y no hay tareas inventadas; (3) cinco dimensiones por tarea con valores 0, 1 o 2; (4) `tier` no menor que el calculado, y mayor solo con `tier_override`; (5) tareas por bloque ≤ `max_tasks` de su nivel; (6) `depends_on` existe y no hay ciclos; (7) `status` es `pending`, `in_progress` o `done`.

### B4. Hitos y tareas

Cada tarea sigue el ciclo: tests en rojo → implementación mínima → tests en verde → commit.

#### H0 — Esqueleto usable

**Tarea 1: estado y CLI base**

- [ ] Archivos: `bin/astillero.py`, `plantillas/routing.json`, `tests/test_state.py`
- Produce: `init`, `status`, `gate pass`, `slice set`, `render-state`; constante `PHASES` con las 8 fases en orden.
- Tests:
  - `test_init_creates_state`: `phase == "requisitos"`, 8 gates en `null`, `.gitignore` contiene `.astillero/local/`.
  - `test_init_twice_fails`: sale 1 y no modifica el archivo.
  - `test_init_outside_git_fails`: sale 2.
  - `test_gate_pass_advances`: tras `gate pass requisitos`, `phase == "arquitectura"` y el gate tiene `passed_at`.
  - `test_gate_pass_wrong_phase_rejected`: `gate pass specs` en fase `requisitos` sale 1 y deja el estado intacto.
  - `test_construir_requires_next`: sin `--next` sale 1; con `--next specs` vuelve a `specs`, pone en `null` los gates `specs`, `bloques` y `construir`, y mueve `slice` a `slices_done`; con `--next revision` avanza a `revision`.
  - `test_slice_set_only_in_specs`: fuera de la fase `specs` sale 1; dentro, fija `slice`.
  - `test_revision_closes`: tras `gate pass revision`, `phase == "cerrado"`.
  - `test_status_soft_never_fails`: en un repo sin inicializar, `status --soft` sale 0 e imprime `sin inicializar`.
  - `test_render_state_idempotent`: dos ejecuciones seguidas dejan `PROJECT_STATE.md` idéntico.
- Verificación: `python3 -m unittest tests.test_state -v`

**Tarea 2: router**

- [ ] Archivos: `SKILL.md`, `README.md`, `tests/test_budgets.py`, `escenarios/00-router.md`
- Consume: `status --soft` (T1).
- Frontmatter de `SKILL.md`: `name: astillero`, `disable-model-invocation: true`, `argument-hint: "[estado]"` y `allowed-tools` para la CLI. `[VERIFICAR V4]`
- Reglas del router: (1) inyecta el estado con `` !`python3 "${CLAUDE_SKILL_DIR}/bin/astillero.py" status --soft` ``; (2) sin inicializar: propone `init` y se detiene; (3) lee únicamente el archivo de `fases/` de la fase actual; (4) un gate se cierra solo con `gate pass`, después de cumplir la condición escrita en la fase; (5) `/astillero estado` muestra el estado y termina.
- Tests:
  - `test_skill_md_budget`: `SKILL.md` ≤ 80 líneas.
  - `test_fases_budget`: cada archivo de `fases/` ≤ 120 líneas.
  - `test_no_model_names_outside_routing`: `opus`, `sonnet`, `haiku` y `fable` no aparecen en `SKILL.md`, `fases/` ni en `plantillas/agents/`.
- Escenario 00: en un repo sin inicializar propone `init` y no toca nada más; en fase `requisitos` lee solo `fases/1-requisitos.md`.
- Verificación: `python3 -m unittest tests.test_budgets -v` y escenario 00 a mano.

#### H1 — Gates deterministas

**Tarea 3: verify**

- [ ] Archivos: `plantillas/verify.py`, `plantillas/verify.sh`, `tests/test_verify.py`
- Produce: el contrato de verify de A5.
- Tests:
  - `test_full_pass_writes_evidence`: pasos `true` → sale 0 y `<sha>.full.json` tiene `result == "pass"` y `dirty == false`.
  - `test_stops_at_first_failure`: pasos `true`, `false`, `touch marcador` → sale 1, `marcador` no existe, `result == "fail"`.
  - `test_fast_skips_full_steps`: `--fast` no ejecuta pasos `full` y escribe `<sha>.fast.json`, no `<sha>.full.json`.
  - `test_dirty_tree_marks_dirty`: con un archivo sin commit, `dirty == true`.
  - `test_tests_touched_fails_without_tests`: cambio en `src_globs` y ninguno en `test_globs` → falla el paso `tests-touched`.
  - `test_tests_touched_passes_with_tests`: cambios en ambos → pasa.
  - `test_missing_config_exits_2`.
- Verificación: `python3 -m unittest tests.test_verify -v`

**Tarea 4: gate de PR**

- [ ] Archivos: `plantillas/pr_gate.py`, `plantillas/settings.json`, `tests/test_pr_gate.py`
- Consume: formato de evidencia (T3) y `state.json` (T1).
- Produce: el contrato de `pr_gate.py` de A5 y el hook `PreToolUse` con `matcher: "Bash"`. `[VERIFICAR V3]`
- Tests:
  - `test_non_pr_command_allowed`: `git status` → sale 0 y stdout vacío.
  - `test_pr_without_evidence_denied`: `gh pr create --fill` → `permissionDecision == "deny"` y la razón menciona `./verify.sh`.
  - `test_pr_with_fresh_evidence_allowed`: evidencia válida para `HEAD` → sale 0 y stdout vacío.
  - `test_stale_evidence_denied`: evidencia de un SHA anterior → deny.
  - `test_fast_evidence_denied`: solo evidencia `fast` → deny.
  - `test_compound_command_detected`: `cd api && gh pr create --fill` sin evidencia → deny.
  - `test_cwd_subdirectory`: `cwd` en una subcarpeta → encuentra la raíz y decide igual.
  - `test_unmanaged_repo_ignored`: repo sin `.astillero/` → sale 0.
  - `test_missing_review_denied`: con `current_block` y sin veredicto `approve` para `HEAD` → deny y la razón nombra al revisor.
  - `test_internal_error_fails_closed`: evidencia con JSON corrupto y comando de PR → deny.
- Verificación: `python3 -m unittest tests.test_pr_gate -v`

**Tarea 5: instalación del arnés y doctor**

- [ ] Archivos: `bin/astillero.py` (`harness install`, `doctor`), `plantillas/verify-steps/*.json`, `plantillas/ci/github-actions.yml`, `tests/test_harness.py`
- Consume: T3 y T4.
- Tests:
  - `test_install_copies_files`: existen `verify.sh` (ejecutable), `.astillero/bin/verify.py`, `.astillero/bin/pr_gate.py`, `.astillero/verify.json`, `.github/workflows/verify.yml` y el hook en `.claude/settings.json`.
  - `test_install_idempotent`: la segunda ejecución no duplica el hook ni cambia archivos.
  - `test_install_preserves_existing_settings`: los hooks y permisos previos siguen ahí.
  - `test_install_no_overwrite_without_force`: un `verify.json` editado no se pisa.
  - `test_doctor_ok`: arnés completo → sale 0.
  - `test_doctor_missing_hook_fails`: sin hook → sale 1.
  - `test_doctor_warns_env_override`: con `CLAUDE_CODE_EFFORT_LEVEL` o `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` definidas → aviso y sale 0.
- **Aceptación de H1** (a mano, en un repo de juguete): pedir a Claude Code un PR sin haber corrido verify → la llamada se niega y Claude corre `./verify.sh`; al pasar, el PR se crea; el workflow corre el mismo script; la rama principal exige ese check.
- Al cerrar H1, instala el arnés en el propio repo `astillero`, con `python3 -m unittest discover -s tests` como paso de su `verify.json`. Desde aquí el skill se construye bajo su propio gate.
- Verificación: `python3 -m unittest tests.test_harness -v`

#### H2 — Bloques y ruteo

**Tarea 6: bloques**

- [ ] Archivos: `bin/astillero.py` (`blocks validate`, `block start`, `block close`), `tests/test_blocks.py`, `tests/fixtures/tasks-a.md`, `tests/fixtures/tasks-b.md`
- Tests: uno por regla de B3 (`test_unique_ids`, `test_all_tasks_assigned`, `test_score_range`, `test_tier_not_below_computed`, `test_tier_above_needs_override`, `test_max_tasks_per_tier`, `test_dependency_cycle_rejected`, `test_status_values`), más:
  - `test_risk_two_forces_t2`: tarea con total 2 y `riesgo == 2` en un bloque T1 → error.
  - `test_block_start_requires_deps_done`.
  - `test_block_close_appends_metrics`: una línea nueva en `metrics.jsonl` con `block`, `tier`, `intentos`, `hallazgos`, `merged_sha`.
  - `test_status_mid_block_shows_next_action`: con un bloque en curso, `status` nombra la rama `bloque/<id>` y el siguiente paso.
- Verificación: `python3 -m unittest tests.test_blocks -v`

**Tarea 7: generación de agentes**

- [ ] Archivos: `plantillas/agents/*.md.tmpl`, `bin/astillero.py` (`agents render`), `tests/test_agents.py`
- Produce: los 7 agentes de A4 con `model` y `effort` tomados de `routing.json`. Desde aquí `doctor` exige los agentes generados (actualiza `test_doctor_ok`).
- Tests:
  - `test_all_roles_rendered`: 7 archivos en `.claude/agents/`.
  - `test_render_uses_routing`: cambiar `tiers.T3.model` cambia el frontmatter de `astillero-impl-t3.md`.
  - `test_render_idempotent`.
  - `test_impl_agents_cannot_spawn`: `disallowedTools` incluye `Agent`.
  - `test_reviewer_read_only`: `disallowedTools` incluye `Write` y `Edit`.
  - `test_doctor_detects_drift`: un agente editado a mano → `doctor` sale 1.
- Verificación: `python3 -m unittest tests.test_agents -v`

**Tarea 8: fases `bloques` y `construir`**

- [ ] Archivos: `fases/6-bloques.md`, `fases/7-construir.md`, `bin/astillero.py` (`review record`), `tests/test_review.py`, `escenarios/06-bloques.md`, `escenarios/07-construir.md`
- Consume: T6 y T7. `construir` sigue el orden de A5.
- Tests:
  - `test_review_record_requires_head_sha`: `sha` distinto de `HEAD` → sale 1.
  - `test_review_record_writes_verdict_first_line`: el archivo empieza con `verdict: approve` o `verdict: changes`.
- Escenario 06: con un `tasks.md` de 8 tareas mixtas, propone bloques que pasan `blocks validate` y se detiene a pedir aprobación.
- Escenario 07: (a) bloque T1 de juguete: despacha `astillero-impl-t1` sin `model` ni `effort`, corre verify rápido, despacha al revisor, registra el veredicto, corre verify completo, crea el PR y se detiene antes del merge; (b) mismo encargo sin el skill, anotando qué pasos se salta.
- **Aceptación de H2:** una funcionalidad de juguete de 6 a 8 tareas llega a PR pasando por todos los pasos, y el modelo y esfuerzo aplicados coinciden con `routing.json`. `[VERIFICAR V2]`

#### H3 — Frente del flujo

**Tarea 9: fases 1 a 3**

- [ ] Archivos: `fases/1-requisitos.md`, `fases/2-arquitectura.md`, `fases/3-auditoria.md`, `plantillas/docs/{brief,stack,auditoria,adr}.md`, `escenarios/01-requisitos.md`, `escenarios/02-arquitectura.md`, `escenarios/03-auditoria.md`
- Contratos: tabla de A3. La fase 2 no acepta una versión sin URL oficial y fecha de consulta.
- Escenarios: (01) de una idea de un párrafo sale un brief con rebanadas ordenadas; (02) cada fila de `stack.md` tiene fuente y fecha; (03) con una incompatibilidad sembrada a propósito en el stack, la auditoría la reporta como bloqueante.

**Tarea 10: fase `specs`**

- [ ] Archivos: `fases/5-specs.md`, `escenarios/05-specs.md`
- Contrato: comprueba que `specify` esté instalado; inicializa si falta `.specify/`; la constitution se siembra con el brief, el stack, las decisiones de la auditoría y las reglas de calidad de A5; por rebanada corre la cadena de Spec Kit y fija la rebanada con `slice set`. `[VERIFICAR V1]`

#### H4 — Preparar el repo

**Tarea 11: fase `preparar`**

- [ ] Archivos: `fases/4-preparar.md`, `plantillas/{AGENTS.md,CLAUDE.md,CLAUDE.local.md}.tmpl`, `plantillas/docs/skills.md`, `escenarios/04-preparar.md`
- Consume: `harness install`, `agents render`, `doctor`.
- Contrato: aplica las reglas de A6 y A7; el gate es `doctor` en 0. `[VERIFICAR V5]`

#### H5 — Revisión final

**Tarea 12: fase `revision`**

- [ ] Archivos: `fases/8-revision.md`, `plantillas/docs/revision-final.md`, `bin/astillero.py` (`clean-clone`), `tests/test_clean_clone.py`, `escenarios/08-revision.md`
- Tests:
  - `test_clean_clone_runs_verify_in_fresh_clone`: un archivo sin versionar del repo original no existe en el clon.
  - `test_clean_clone_fails_when_verify_fails`.
- Escenario 08: con un requisito sin test sembrado a propósito, la matriz de trazabilidad lo marca.

#### H6 — Piloto

**Tarea 13: un producto pequeño real, de punta a punta**

- [ ] Registrar en `LEARNINGS.md`, por bloque: nivel, intentos, hallazgos del revisor, fallos de verify e intervenciones de John.
- Al cerrar: borrar cada regla que no evitó ningún fallo y subir un escalón de exigencia donde un fallo se repitió.

### B5. Por verificar antes de implementar

| # | Qué | Dónde afecta |
|---|---|---|
| V1 | Spec Kit: nombres exactos de los comandos en Claude Code, la bandera de `specify init` para Claude y el formato de ids en `tasks.md` | T6, T10 |
| V2 | Cómo observar el modelo y el esfuerzo que aplicó un subagente | Aceptación de H2 |
| V3 | Hook: forma `command` + `args`, salida JSON de negación, comportamiento con comandos compuestos; decidir si conviene añadir `if` | T4 |
| V4 | Skill personal: enlace simbólico, `disable-model-invocation`, `allowed-tools` con `${CLAUDE_SKILL_DIR}` e inyección con `` !`…` `` | T2 |
| V5 | `CLAUDE.local.md` y el import `@AGENTS.md` en la versión instalada | T11 |
| V6 | Comandos de cada plantilla de `verify-steps` contra la versión fijada del stack | T5 |
| V7 | Cómo correr los escenarios sin intervención (sesión sin interfaz o subagente en un repo temporal) | T2, T8, T9 |
| V8 | Dónde lee Codex sus skills y si tolera los campos de frontmatter propios de Claude Code | A8-9 |

Verificado el 2026-11-15 en la documentación oficial: campos `model` y `effort` en subagentes y en skills · precedencia de agentes (proyecto por encima de usuario y de plugin) · orden de resolución (el parámetro de despacho gana al frontmatter; en esfuerzo, `CLAUDE_CODE_EFFORT_LEVEL` gana a todo; en modelo, solo `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` anula el frontmatter) · negación desde `PreToolUse` con `permissionDecision: "deny"` · los hooks del proyecto también se disparan en las llamadas de los subagentes · `CLAUDE.local.md` vigente e import `@AGENTS.md` recomendado · capas de personalización de Spec Kit (overrides locales, presets, extensiones).

## Fuentes

- Claude Code — skills: https://code.claude.com/docs/en/skills.md
- Claude Code — subagentes: https://code.claude.com/docs/en/sub-agents
- Claude Code — hooks: https://code.claude.com/docs/en/hooks.md
- Claude Code — CLAUDE.md y memoria: https://code.claude.com/docs/en/memory
- Spec Kit — documentación y presets: https://github.github.com/spec-kit/ · https://github.github.com/spec-kit/reference/presets.html
- Spec Kit — personalizar sin fork: https://developer.microsoft.com/blog/from-spec-first-to-enterprise-ready-extending-github-spec-kit/
- mattpocock/skills: https://github.com/mattpocock/skills
- addyosmani/agent-skills: https://github.com/addyosmani/agent-skills
- ponytail y su prueba independiente: https://github.com/dietrichgebert/ponytail · https://blog.jetbrains.com/ai/2026/07/ponytail-skill-claude-tested/
- pstack para Claude Code: https://github.com/michael-denyer/pstack-claude
- impeccable: https://github.com/pbakaus/impeccable
- ECC y su medición: https://github.com/affaan-m/ECC · https://developertoolkit.ai/en/ecosystem/frameworks/everything-claude-code/
- tgrep: https://github.com/microsoft/tgrep
