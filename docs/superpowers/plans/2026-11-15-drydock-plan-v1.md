# Drydock — Plan de implementación v1

> **Para quien ejecute (agente):** SUB-SKILL OBLIGATORIA: `superpowers:subagent-driven-development` (recomendada) o `superpowers:executing-plans`, tarea por tarea. Los pasos usan casillas (`- [ ]`). Las fases en prosa se redactan con `superpowers:writing-skills`. **No se escribe código hasta que John apruebe este plan.**

**Objetivo:** un skill personal, `/drydock`, que lleva un producto de software de la idea al código integrado, revisado y desplegado: estado en archivos, modelo y esfuerzo asignados por complejidad, y gates que se exigen con código.

**Arquitectura:** dos capas. El **skill** es un router corto que lee el estado del repo y carga solo la fase en curso; trae una CLI en Python y plantillas. El **arnés por repo** son archivos versionados dentro de cada producto (`verify.sh`, hook, agentes, estado) que siguen funcionando sin el skill instalado. Spec Kit genera constitution/spec/plan/tasks sin modificarse.

**Stack:** Markdown · Python ≥ 3.9 con solo librería estándar · JSON · `git`, `gh` · Spec Kit 1.0.8 · Claude Code 2.1.325 (Codex 0.169 en H7).

**Spec:** la Parte A (diseño v1) viaja con el plan. El v0 se guarda al lado (`docs/superpowers/plans/2026-11-15-astillero-plan-v0.md`); su sección A7 (curaduría de skills) no cambia y se lee allí. El v0 usa el nombre anterior del proyecto, `astillero`.

## Contexto

John pidió "Crear (ver md)" sobre `2026-11-15-astillero-plan-v0.md`. Ese documento ordena **refinar antes de construir** (su sección 0) y no escribir código hasta que John apruebe el plan refinado. Este archivo es el resultado de esa sección 0: entorno leído, V1–V8 comprobados contra la documentación oficial, D1–D12 cuestionadas, A8 resuelta con John (una decisión por mensaje) y H0–H2 bajados a pasos TDD con firmas y aserciones exactas. H3–H7 quedan como contrato hasta cerrar H2.

Al aprobarlo se ejecuta el paso 0 (B0): actualizar herramientas, mover la carpeta a `~/Developer/drydock`, crear ahí el repo y guardar v0 y v1 en `docs/superpowers/plans/`. Después, H0.

## Resumen para John

- **Tus decisiones de A8 agrandaron V1:** despliegue real ejecutado por drydock, auto-merge de T1, TDD nivel L2, todo en inglés y skill completo en Codex. V1 pasa de 13 a 17 tareas y de 7 a 8 hitos (H0–H7). H0–H2 no implementan despliegue ni Codex, aunque ya llevan la regla `ask` de `deploy`; L2 y el auto-merge sí pesan en H1 y H2.
- **La verificación cambió tres cosas de fondo:** (1) un hook `PreToolUse` **falla abierto** por defecto, así que el gate de v0 podía no exigir nada sin avisar; ahora lleva `onFailure: "block"`; (2) Spec Kit 1.0.8 instala skills `/speckit-*` y sus banderas no son las de v0; (3) si el comando que inyecta el estado sale distinto de 0, el skill entero no carga.
- **Corregí huecos de v0:** las aprobaciones tuyas (D9) eran solo prosa y ahora son reglas `permissions.ask`; nada decía cómo llegan a la rama principal los cambios de estado y de specs; el escenario 00 leía un archivo que no existía hasta H3.
- **Añadidos que no pediste** (marcados ⊕ en la lista de cambios): guardia de push directo a la rama base, reglas `allow` para la CLI y negar el skill `speckit-implement`. Qué arrastra quitar cada uno está en «Para recortar».
- **Sigue sin probarse en ejecución:** todo lo verificado salió de documentación y de `--help`. Cada hito tiene una aceptación manual que comprueba los puntos dudosos (lista en B5).
- **Acciones hacia afuera que pediré confirmar cuando toquen:** enlaces simbólicos en `~/.claude/skills` y `~/.agents/skills`, repo de GitHub para drydock (cuenta y visibilidad) y repo de juguete para las aceptaciones.
- **Revisión adversaria (2026-11-15):** tres revisores leyeron este plan. De 39 hallazgos apliqué 30, 8 en parte y descarté 1 (cambios 29–44 y «De la revisión, no aplicado»). Los tres más graves: tu modo por defecto (`dontAsk`) convierte cada aprobación en una negación sin prompt; el auto-merge de T1 podía integrar cambios al propio arnés; y `block start` barría con `git add -A` cualquier archivo pendiente, `.env` incluido.
- **Decisiones tuyas que el plan deja con un valor por defecto:** (1) cómo apruebas (A5, «Aprobaciones y modo de permisos»): reglas `ask` y, donde el modo no pregunta, corres tú el comando; (2) L2 frente al auto-merge (A5): el test en rojo arma toda su tarea; (3) qué hacer si la cuenta de GitHub no admite el check requerido (aceptación de H1, paso 7).
- **Nombre:** `drydock` en lugar de `astillero` (cambio 45). La carpeta actual se mueve en B0. No comprobé si el nombre ya está tomado en GitHub, npm, PyPI o los marketplaces de plugins: es una palabra muy usada y, si vas a publicar, conviene mirarlo antes de H0.

## Cambios respecto a v0

**Por tus decisiones (A8):**

1. Despliegue real en V1: `.drydock/deploy.json`, comando `deploy` (tú apruebas cada ejecución), smoke, y evidencia de despliegue exigida al cerrar cada rebanada y en la revisión final. La rebanada 0 es el esqueleto andante ya desplegado. (A1, A3, A5, H5)
2. Auto-merge de T1: comando `block merge`, con condiciones exigidas por código. T2 y T3 los integras tú. (A5, T6C)
3. L2 desde el inicio: el paso `red-first` reemplaza a `tests-touched`. (A5, T3)
4. Todo en inglés: fases, carpetas, roles, CLI, prosa del skill, mensajes y plantillas. Este plan sigue en español.
5. Skill completo en Codex: hito H7 nuevo, después del piloto.
6. Piloto en .NET 10: solo se escribe esa plantilla de verify y de CI.
7. Confirmado sin cambio de diseño: verify rápido → revisión → verify completo (ahora exigido por código), revisor escalado en T3, superpowers limitado por `CLAUDE.md`.

**Por verificación (sección 0.2):**

8. Hook con `onFailure: "block"`; el script imprime siempre un único objeto JSON y sale 0; se filtra a sí mismo en vez de usar `if`. (T4)
9. Spec Kit 1.0.8: `specify init --here --force --non-interactive --integration claude --script sh`; skills `/speckit-*`; `/speckit-analyze` no escribe archivo (la fase lo guarda); la rebanada sale de `.specify/feature.json`. (T10)
10. `status --soft` sale 0 en todos los casos, también con estado corrupto; un test fija que `allowed-tools` coincide con el comando inyectado. (T1, T2)
11. Los subagentes pueden lanzar subagentes por defecto: todos los agentes generados llevan `Agent` en `disallowedTools`. (T7)
12. `git init -b main` siempre: `init.defaultBranch` no está definido en esta máquina. (B0, tests)
13. Los escenarios corren con `claude -p "/drydock"` sin `--bare` y se detienen solos en los gates humanos. (T2, T8)
14. El modelo y esfuerzo aplicados se observan con `/tasks`. (aceptación de H2)

**Por la crítica de D1–D12 y huecos de v0:**

15. Aprobaciones humanas exigidas: `permissions.ask` para `gate pass`, `deploy` y `gh pr merge`. (T4, T5)
16. `gate pass` ejecuta el chequeo automático de la fase cuando existe (`prepare` → doctor, `blocks` → validate, `build` → bloques cerrados y despliegue, `review` → clon limpio y despliegue).
17. `review record` exige evidencia de verify en verde para ese commit y toma el veredicto de la primera línea del texto del revisor; desaparece la bandera `--verdict`. (T8)
18. Estado: cada comando que lo cambia regenera `PROJECT_STATE.md`; `block start` crea la rama y hace commit de todo lo pendiente (specs, plan de bloques, estado). Regla escrita para lo que no es bloque (A5).
19. ⊕ Guardia de push directo a la rama base: el hook devuelve `ask`. Cierra el hueco "merge sin aprobación" sin depender del plan de GitHub. (T4)
20. `block pr-body`: cuerpo del PR determinista; implementa la copia de evidencia y veredicto al PR que v0 ya pedía. (T8)
21. ⊕ `permissions.allow` para la CLI y `./verify.sh`: sin esto cada comando pide permiso y las tres aprobaciones reales se pierden entre el ruido. (T5)
22. ⊕ `permissions.deny: Skill(speckit-implement)`: evita la segunda cadena de implementación que A1 llama fracaso. (T5)
23. T2 crea los 8 archivos de fase como stubs con propósito y gate.
24. `harness install` no requiere `init` (los gates sirven en cualquier repo) y `--force` solo pisa los scripts propios, nunca `verify.json` ni el workflow.
25. `base_branch` vive solo en `verify.json`; `tier_override` es una cadena con el motivo; `--merged-sha` es opcional.
26. `dirty` se calcula después de correr los pasos.
27. `doctor` comprueba además `onFailure`, las reglas `ask`, deriva de los scripts y que `.drydock/local/` no esté versionado.
28. T6 se divide en 6A/6B/6C y T12 en 12A/12B; T14 es nueva.

**Por la revisión adversaria (2026-11-15):** tres revisores leyeron este plan (cobertura contra v0, escéptico y ejecutor; el ejecutor llegó hasta T6B). De 39 hallazgos se aplicaron 30, 8 en parte y 1 se descartó. Los hallazgos completos están en `docs/superpowers/plans/2026-11-15-review-checkpoint.json`.

29. Aprobaciones en el modo real de John: en `dontAsk` una regla `ask` niega sin preguntar, así que el skill se detiene y John corre el comando. `init` instala las reglas de permisos desde el primer gate. Un «Paso 0 de H1» prueba hook y permisos antes de escribir T4. (A5, T2, T5, H1)
30. El check requerido en la rama base pasa de exigido (v0) a condicionado al plan de GitHub; si la cuenta no lo admite, John decide antes de H2. (aceptación de H1)
31. `block merge` rechaza un bloque que toca el arnés (`verify.json`, `deploy.json`, `routing.json`, scripts, settings, agentes, workflows). (T6C)
32. `block start` solo barre rutas conocidas y se niega ante cualquier otra pendiente; devuelve la base local a `origin`. (T6B)
33. Con bloque en curso, el hook exige evidencia, veredicto y `--match-head-commit <HEAD>` también en `gh pr merge`. (T4)
34. `blocks.json` queda atado a la rebanada en curso y el gate `specs` exige rebanada y `tasks.md`. Un `tasks.md` ausente, vacío o con ids en otro formato es un error. (T6A, T6B)
35. `block close` con remoto `origin` solo acepta el merge que diga `gh`; `block merge` comprueba la rama destino del PR. (T6C)
36. `red-first`: un test en rojo arma todos los commits de su tarea, no uno solo (decisión de John pendiente, A5); la base se resuelve primero en `origin`. Plantilla .NET con globs amplios. (T3, T5, T11)
37. `block merge` hace una sola consulta de checks en vez de esperar con `--watch`; si CI no terminó, se repite. Las salidas reales de `gh` se capturan antes de escribir el fake. (T6C)
38. Hook: más formas de `gh pr create` y de push a la base; un error interno ante un push pregunta en vez de dejar pasar. (T4)
39. El repo propio entra por PR desde el cierre de H1 (`task/T<n>`); `.gitignore` con `__pycache__/` desde B0; la suite corre también con Python 3.9 desde T1. (B0, B1, cierre de H1)
40. Líneas base de los escenarios 06 y 07 al empezar H2, antes de escribir T6A; el escenario 00 no lleva. Los escenarios 06 y 07 corren con `acceptEdits`. (H2, T8)
41. Recortes: `status --json` y el escaneo de `maxEffortLevel` y `availableModels` en `doctor`; la regla 2 del router no nombra el adaptador de Codex hasta H7. (T1, T2, T5)
42. Tests que no podían verse fallar (`test_init_outside_git_fails`, `test_render_idempotent`), aislamiento de `helpers.run`, mensajes de `doctor` fijados, `templates_dir` en T1. (T1, T2, T3, T5, T6A, T7)
43. Contratos de H3–H7: agentes antes de la fase 3, rebanada de corrección desde `review`, precondición y orden de cierre de `deploy`, `--deny-on-ask` para Codex, columnas de `audit.md` y contenido de `AGENTS.md`. (A3, A6, T9–T14)
44. «Entorno leído» recoge permisos, plugins y hooks de John; A7 reconoce que el entorno real no cumple sus reglas. (A7)

**Por el cambio de nombre (2026-11-15):**

45. El proyecto pasa de `astillero` a `drydock`, por decisión de John, por si se publica: skill `/drydock`, CLI `bin/drydock.py`, carpeta `.drydock/`, agentes `drydock-*`, docs en `docs/drydock/` y repo `~/Developer/drydock`. El v0 conserva su nombre de archivo y usa el nombre antiguo. No se comprobó si el nombre choca con proyectos ya publicados.

**Por la pasada final de verificación (2026-11-15, tras la aprobación):** el workflow de revisión terminó después de aprobarse el plan: 38 hallazgos, 37 confirmados y 1 refutado, casi todos ya aplicados (`docs/superpowers/plans/2026-11-15-review-final.json`).

46. Sus seis ajustes pendientes, todos pequeños y sin cambiar ningún total de tests: `status --soft` atrapa cualquier excepción; `test_render_state_idempotent` comprueba el código de salida; `HARNESS_PATHS` cubre también `AGENTS.md`, `CLAUDE.md`, `.claude/skills/` y `.specify/`; un check en `skipping` no bloquea `block merge`; el Paso 0 de H1 comprueba qué niega `dontAsk` además de los `ask`; y la respuesta del revisor se registra sin editar. (T1, T6B, T6C, T8, H1)

**Por la aceptación de H0 (2026-11-16):**

47. El router inyecta la fase. En `dontAsk`, Claude Code niega leer los archivos del propio skill (`Read`, y `cat` por Bash), así que la fase nunca cargaba; permitirlo en `allowed-tools` no sirvió. Ahora `status --soft --phase` imprime el archivo de la fase en curso y `adapters/claude.md`, `SKILL.md` lo inyecta en una sección `## Phase`, y la regla 2 solo manda leerlos a mano si la inyección no corrió. Aprobado por John en la sesión de H0. Suma un test, así que todos los totales suben uno desde T2. Coste: cada `/drydock` inyecta la fase entera, también con `status`. Además, de la revisión de T1: `gate pass build` sin rebanada fijada sale 1 (`no slice set in build`) en vez de corromper el estado. (T1, T2, B3, T14)

**De la revisión, no aplicado** (y por qué): un hook que niegue siempre en lugar de reglas `ask` queda como opción B de A5; `block merge` como comprobador para T2 y T3 sobra, porque el hook ya exige lo mismo en `gh pr merge`; `deploy <sha>` cubría un `deploy.json` cambiado por auto-merge, que cierra el cambio 31; que el revisor registre su propio veredicto sigue dependiendo de prosa, y se mide en H2 y H6; revalidar el plan en `block merge` no detecta una rebaja coherente de nivel y puntuación; `block abort` y el contador de commits de código en la evidencia pasan a A9; `--attempts`, `--findings` y `--stack` se quedan como están; y el aviso sobre el SHA abreviado de `review record` no aplica, porque T8 ya nombra el archivo con el `HEAD` completo.

**Para recortar**, si quieres menos, y qué arrastra cada ⊕: el 19 se lleva `PUSH_RE`, `test_push_to_base_asks`, el punto 1 de B2 y el paso 5 de la aceptación de H1; el 21 y el 22 están fijados por `test_settings_template` y `test_install_preserves_existing_settings`, y sin el 21 cada comando de la CLI pide permiso (en `dontAsk`, se niega). El 20 no era un añadido: v0 ya pedía copiar evidencia y veredicto al cuerpo del PR. Yo conservaría los tres. Lo único de H0–H2 que aplazaría es el auto-merge (T6C), y solo si tú lo dices.

## Entorno leído (sección 0.1, 2026-11-15)

macOS 27.3 arm64 · Claude Code 2.1.325 · Python 3.14.7 · git 2.54.0 (`init.defaultBranch` sin definir) · gh 2.103.3 con sesión activa (no pude leer el plan de la cuenta: no sé si admite protección de rama en repos privados) · specify-cli 1.0.8 (upstream va por 1.4.x) · uv 0.13.7 · codex-cli 0.169.0 · dotnet 10.0.201 · Node 26, JDK 21, Docker 29, Swift 6.4 disponibles. `~/Developer/astillero`, la carpeta de trabajo actual, no es repo git y solo contiene `docs/superpowers/plans/`; B0 la mueve a `~/Developer/drydock`. `~/.claude/skills` ya usa enlaces simbólicos. `/usr/bin/python3` es 3.9.6.

Ajustes de John en `~/.claude/settings.json` (leídos en la revisión): `permissions.defaultMode = dontAsk`, `permissions.allow = [Bash(gh pr merge:*)]`, `autoMode.allow` con la misma regla y `skipDangerousModePermissionPrompt = true`; trae `effortLevel` y `modelSettings`, no `maxEffortLevel` ni `availableModels`. Esa regla `allow` hace que, en cualquier repo sin arnés, `gh pr merge` no pregunte. Plugins activos a nivel de usuario: context-mode, ecc, mattpocock-skills, playwright, ponytail, rembric, superpowers, swift-lsp y usage-monitor (apagados: frontend-design, gsd, ralph-loop). Hooks de usuario: `SessionStart`, `PreToolUse` sobre `Grep|Glob`, `PostToolUse` sobre `Read` y `SubagentStart` sobre todo subagente; lo que inyectan llega también a los agentes de drydock. Los hooks propios de cada plugin no se leyeron uno a uno.

## Verificación de V1–V8 (sección 0.2)

| # | Resultado | Efecto en el plan |
|---|---|---|
| V1 | Spec Kit 1.0.8: `specify init` usa `--integration claude --script sh --non-interactive` (no existen `--ai` ni `--no-git`); instala skills `.claude/skills/speckit-<nombre>/`; tareas `- [ ] T012 [P] [US1] …` con ids `T` + 3 dígitos o más; `/speckit-analyze` es de solo lectura | Regex de T6A; contrato de T10 |
| V2 | `/tasks` muestra modelo y esfuerzo por subagente; las transcripciones `subagents/agent-<id>.jsonl` traen `message.model` (no documentado) | Aceptación de H2 |
| V3 | Esquema con `command` + `args` válido. **Falla abierto** salvo `onFailure: "block"`. Decisiones `allow`, `deny`, `ask`, `defer`. El hook recibe el comando compuesto entero. `if` es de mejor esfuerzo | T4 |
| V4 | Enlaces simbólicos admitidos; `${CLAUDE_SKILL_DIR}` se sustituye en el contenido y en `allowed-tools`; un comando inyectado que sale ≠ 0 o que no está preaprobado aborta el skill | T1, T2 |
| V5 | `CLAUDE.local.md` vigente; `@AGENTS.md` válido; `AGENTS.md` solo se lee nativo si no hay `CLAUDE.md` | T11 mantiene `CLAUDE.md` con `@AGENTS.md` |
| V6 | .NET 10: `dotnet format --verify-no-changes`, `dotnet build -warnaserror`, `dotnet test --filter Category!=Integration` con VSTest, que es el runner por defecto. Si el piloto activa Microsoft.Testing.Platform en `global.json`, los filtros cambian | Plantilla `dotnet`; las otras tres salen de V1 |
| V7 | `claude -p "/skill"` ejecuta skills invocados por el usuario con hooks y settings del proyecto; una regla `ask` se niega en modo `dontAsk` | Escenarios sin intervención; aprobaciones en el modo de John (A5) |
| V8 | Codex 0.169 lee skills de `.agents/skills` y `~/.agents/skills`; exige `description`; ignora el frontmatter que no conoce; sus hooks solo niegan (no hay `ask`) | H7 |

Además: precedencia de permisos `deny` > `ask` > `allow`; `ask` gana a `allowed-tools` de un skill; `Skill(nombre)` es una regla de permiso válida; un proyecto puede desactivar un plugin del usuario con `enabledPlugins`.

---

## Parte A — Diseño v1

### A1. Alcance

- **Es:** un flujo por fases con estado en archivos, un arnés de gates por repo y un ruteo de modelo y esfuerzo por complejidad, para uso personal de John en Claude Code y, desde H7, en Codex.
- **No es:** un reemplazo de Spec Kit, un framework multiagente ni una plataforma de despliegue: drydock ejecuta el comando de despliegue del repo, no lo diseña. V1 no ejecuta bloques en paralelo y maneja un solo entorno.
- **Sería un fracaso aunque funcione si:** el arnés pesa más que el producto; una regla depende de que el modelo se acuerde; un gate puede fallar abierto sin que nadie lo note; aparece un nombre de modelo fuera de `routing.json`; conviven dos cadenas de specs y planes en el mismo repo.
- **"100" significa:** todas las rebanadas del brief integradas en la rama base, `./verify.sh` en verde, cada rebanada desplegada con smoke en verde, revisión final sin bloqueantes y arranque reproducible desde un clon limpio.

### A2. Decisiones D1–D12: veredicto (sección 0.3)

| # | Veredicto | Motivo |
|---|---|---|
| D1 skill, no plugin | Se mantiene | Enlaces simbólicos comprobados. Un segundo enlace en `~/.agents/skills` cubre Codex. El plugin solo aporta `claude plugin eval`, que nadie ha echado en falta |
| D2 dos capas | Se mantiene | Los tests de T5 lo prueban: los gates corren con solo los archivos copiados |
| D3 Spec Kit sin fork | Se mantiene, con una regla | La versión instalada (1.0.8) se anota en `docs/drydock/skills.md` y no se actualiza a mitad de un producto |
| D4 estado en JSON + `PROJECT_STATE.md` | **Cambia el cómo** | El archivo generado se regenera solo. Se conserva porque sin el skill es lo único legible; la CLI no vive en el repo del producto |
| D5 ruteo por niveles | Se mantiene | El test cubre también `bin/` y todas las plantillas |
| D6 exigir con código | **Se refuerza** | v0 no lo cumplía en tres puntos: hook que falla abierto, aprobaciones solo en prosa, revisión sin verify previo |
| D7 orden rápido → revisión → completo | Se mantiene y se exige | `review record` rechaza un commit sin verify en verde |
| D8 un proceso rector | Se mantiene | El máximo de 5 skills queda como guía, sin código. Riesgo propio de esta máquina: plugins con hooks que interceptan Bash (B5) |
| D9 aprobaciones de John | **Cambia el mecanismo** | Reglas `ask`. Excepción decidida: auto-merge de T1. Se añade el despliegue |
| D10 gates primero | Se mantiene | Despliegue en H5 y Codex en H7 no atrasan el núcleo |
| D11 preparar antes de specs | Se mantiene | La rebanada 0 incluye llegar al servidor |
| D12 Python estándar y JSON | Se mantiene | El piso declarado es la versión más baja que la matriz de CI pruebe; si 3.9 ya no está disponible en los runners, se sube |

**Contra tu propia regla** (complejidad solo ante un fallo demostrado) van cuatro de tus decisiones: despliegue, auto-merge, L2 y Codex. Las respeto; el plan las aísla para poder apagarlas: L2 se desactiva quitando la clave `red`, el auto-merge no usando `block merge`, y el despliegue y Codex son hitos aparte.

### A3. Flujo de fases

```
requirements → architecture → audit → prepare → [ specs → blocks → build ]* → review → closed
                                                 └──── una vuelta por rebanada ────┘
```

| # | Fase | Hace | Produce | Gate (se cierra con `gate pass <phase>`; John aprueba el prompt) |
|---|---|---|---|---|
| 1 | `requirements` | Interrogatorio de una pregunta a la vez | `docs/drydock/brief.md`: problema, usuarios, alcance, fuera de alcance, criterios medibles, restricciones, rebanadas en orden (la 0 es el esqueleto andante desplegado) | John aprueba el brief |
| 2 | `architecture` | Consulta guiada: máquina, **destino y mecanismo de despliegue**, lenguajes y frameworks con versión exacta, BD, estilo, módulos, pruebas, CI/CD | `docs/drydock/stack.md` (componente, versión, fuente oficial, fecha, fin de soporte) y un ADR por decisión en `docs/adr/` | John aprueba el stack |
| 3 | `audit` | Un agente con contexto limpio evalúa el stack con la rúbrica de v0 | `docs/drydock/audit.md`: hallazgo, severidad, evidencia con fuente, cambio propuesto, decisión de John | 0 bloqueantes abiertos |
| 4 | `prepare` | Instala el arnés, genera agentes, elige skills, escribe `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md` y `deploy.json`; crea el remoto | Arnés (A6) y `docs/drydock/skills.md` | Automático: `doctor` sin errores |
| 5 | `specs` | Constitution una vez; por rebanada: specify → clarify → plan → tasks → analyze | `specs/<slice>/{spec,plan,tasks,analysis}.md` | Automático: rebanada fijada y `tasks.md` presente. Analyze sin CRITICAL y John aprueba la spec |
| 6 | `blocks` | Puntúa tareas, agrupa bloques, asigna nivel | `.drydock/blocks.json` | Automático: `blocks validate`. John aprueba el plan |
| 7 | `build` | Por bloque: TDD con red-first → verify rápido → revisión → verify completo → PR → merge. Al cerrar la rebanada: despliegue y smoke | Un PR por bloque, `metrics.jsonl`, evidencia de despliegue | Automático: todos los bloques `done` y despliegue en verde. John elige `--next specs` o `--next review` |
| 8 | `review` | Revisión global, clon limpio, retro | `docs/drydock/final-review.md` y entradas en `LEARNINGS.md` | Automático: `clean-clone` y despliegue en verde. 0 bloqueantes; si los hay, `--next specs` abre una rebanada de corrección |

La rúbrica de auditoría, el contenido de la revisión final y la tabla "dónde quedó cada idea tuya" no cambian respecto a v0.

### A4. Bloques y ruteo

`templates/routing.json` es el único lugar con nombres de modelo:

```json
{
  "version": 1,
  "tiers": {
    "T1": {"model": "sonnet", "effort": "medium", "max_tasks": 8},
    "T2": {"model": "sonnet", "effort": "high", "max_tasks": 4},
    "T3": {"model": "opus", "effort": "xhigh", "max_tasks": 1}
  },
  "roles": {
    "reviewer": {"model": "sonnet", "effort": "medium"},
    "reviewer-t3": {"model": "opus", "effort": "high"},
    "auditor": {"model": "opus", "effort": "xhigh"},
    "final-reviewer": {"model": "opus", "effort": "high"}
  }
}
```

**Puntuación por tarea** (0–2 por dimensión): `novelty` · `scope` · `risk` · `testing` · `ambiguity`, con las mismas definiciones de v0. Nivel por total: 0–3 → T1, 4–6 → T2, 7–10 → T3. `risk = 2` fuerza T2 como mínimo. El nivel del bloque es el de su tarea más alta. Subir de nivel exige `tier_override` con el motivo; bajar no se permite. Las reglas de formación de v0 se mantienen.

**Agentes generados** en `.claude/agents/` del producto:

| Agente | Sale de | `disallowedTools` | Regla de cuerpo |
|---|---|---|---|
| `drydock-impl-t1`, `-t2`, `-t3` | `tiers` | `Agent` | Por tarea: commit de test en rojo, luego commit de implementación. No abre PR ni hace push a la base. Termina con `./verify.sh --fast` en verde |
| `drydock-reviewer`, `drydock-reviewer-t3` | `roles` | `Write, Edit, NotebookEdit, Agent` | La respuesta empieza con `verdict: approve` o `verdict: changes` |
| `drydock-auditor` | `roles` | `Write, Edit, NotebookEdit, Agent` | Comprueba versiones en la fuente oficial |
| `drydock-final-reviewer` | `roles` | `Write, Edit, NotebookEdit, Agent` | — |

El orquestador despacha **sin pasar `model` ni `effort`**: el parámetro del despacho gana al frontmatter. `CLAUDE_CODE_EFFORT_LEVEL` y `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` pisan el ruteo; `doctor` avisa.

### A5. Gates

| Se exige | Mecanismo que no depende del modelo |
|---|---|
| `verify.sh` antes de cada PR | Hook `PreToolUse` con `onFailure: "block"` que niega `gh pr create` y `gh pr new` sin evidencia completa para `HEAD`. CI corre el mismo script |
| Revisión independiente antes del PR | El mismo hook exige veredicto `approve` para `HEAD` cuando hay bloque en curso. `review record` exige verify en verde |
| Se integra lo revisado y nada más | Con bloque en curso, el hook exige la misma evidencia y veredicto ante `gh pr merge`, y que el comando lleve `--match-head-commit <HEAD>` |
| TDD (L2) | Paso `red-first` de verify: todo commit que toca código necesita antes, en su misma tarea, un commit de test que falle, o un trailer `TDD-Exempt: <motivo>`, que queda en la evidencia y en el PR |
| Aprobaciones de John (D9) | `permissions.ask`: `gate pass`, `deploy`, `gh pr merge`, instaladas por `init`. El hook devuelve `ask` ante un push a la rama base. Donde el modo de permisos no puede preguntar, `ask` niega y John corre el comando (ver abajo) |
| Auto-merge solo de T1 | `block merge` comprueba nivel, evidencia sin exenciones, que el bloque no toque el arnés, veredicto, que el PR apunte a `HEAD` y a la base, y que el check `verify` esté en verde |
| Despliegue por rebanada | `gate pass build` y `gate pass review` exigen evidencia de despliegue para el `HEAD` de la base |
| Reglas de capas | Sin código propio: son tests de arquitectura del producto dentro de verify; la librería se elige en H6 |
| Ruteo | Agentes generados desde `routing.json`; `doctor` detecta deriva y variables que lo pisan |
| Versiones reales | Sin código en V1: `stack.md` exige URL oficial y fecha y la auditoría las recomprueba (prosa) |

**Aprobaciones y modo de permisos (decisión de John).** El modo por defecto de John es `dontAsk`, y ahí una regla `ask` no pregunta: niega. Eso falla cerrado, pero deja las aprobaciones sin clic. Valor por defecto del plan, opción A: se mantienen las reglas `ask`; en `default` y `acceptEdits` John aprueba con un clic, y en `dontAsk` o `claude -p` el comando se niega, el skill se detiene y John lo ejecuta él mismo (`! <comando>` en la sesión, o su terminal). Opción B: el hook niega siempre `gate pass`, `deploy`, `gh pr merge` y el push a la base con el motivo `Run it yourself: <command>`; es un solo mecanismo para todos los modos y para Codex, y cuesta reescribir T4 y T5 y perder el clic. El «Paso 0 de H1» mide la opción A en los modos reales, incluido `bypassPermissions`, antes de escribir T4; si `ask` deja pasar sin preguntar en algún modo que John use, se cambia a B. Además, `dontAsk` niega todo lo que no tenga regla `allow` (ediciones, `git commit`, `gh pr create`), así que lo previsible es que drydock se trabaje en `default` o `acceptEdits`; el mismo Paso 0 lo confirma. Medido el 2026-11-16 con `claude -p`: en `default`, `acceptEdits`, `dontAsk`, `auto` y `bypassPermissions` no hay prompt — la decisión `ask` del hook y las reglas `ask` niegan con el motivo, también en `bypassPermissions`; `auto` no está disponible en esa modalidad. En sesión interactiva `default`, la regla `ask` y la decisión `ask` del hook piden confirmación con su motivo, y un hook instalado a mitad de sesión dispara sin reiniciar. Falta el clic interactivo en `acceptEdits`.

**Orden dentro de un bloque:**

1. `drydock.py block start <id>`: crea `block/<id>` desde la base y hace commit de lo pendiente, siempre que todo caiga en rutas conocidas (estado, specs, docs); ante cualquier otra ruta se niega.
2. Implementador del nivel del bloque. Por tarea: `test(<block>/<task>): …` en rojo, después `feat(<block>/<task>): …`. Los arreglos posteriores de esa tarea llevan el mismo ámbito.
3. `./verify.sh --fast`. Si falla, vuelve al implementador. Tras 2 reintentos sube un nivel una sola vez (se anota en `tier` y `tier_override`); si falla de nuevo, se detiene y pregunta a John.
4. Revisor con contexto limpio: id del bloque, criterios de aceptación, constitution y el comando del diff. No recibe el relato del implementador.
5. `drydock.py review record <id> --sha <HEAD>` con el texto del revisor por stdin. Si es `changes`: corrección y revisión del delta, máximo 2 rondas; después decide John.
6. `./verify.sh` completo sobre el commit aprobado. Si falla: corrección y vuelta al paso 3.
7. `git push -u origin block/<id>` y `drydock.py block pr-body <id> | gh pr create --title "<id>: <title>" --body-file -`.
8. T1: `drydock.py block merge <id>`; si CI no ha terminado sale 1 y se repite. T2 y T3: John integra (su clic sobre `gh pr merge block/<id> --squash --delete-branch --match-head-commit <HEAD>`, o la web) y luego `drydock.py block close <id>`.

Al cerrar el último bloque de la rebanada: `drydock.py deploy` (H5) y `gate pass build --next specs|review`.

**Invariante:** entre el veredicto `approve`, el verify completo y la creación del PR no entra ningún commit, y entre la creación del PR y el merge tampoco: `block merge` y el hook (ante `gh pr merge`) vuelven a exigir evidencia y veredicto para `HEAD`. Un merge hecho en la web solo lo cubre CI. Evidencia y veredictos viven en `.drydock/local/` (sin versionar), atados al SHA.

**Dónde se versiona lo que no es bloque:** hasta cerrar el gate `prepare`, los artefactos de fase se confirman directo en la rama base (aún no hay hook ni CI). Después, la base solo cambia por PR de bloque: lo que se produce entre bloques (specs, `blocks.json`, estado) queda sin confirmar en el árbol de trabajo y viaja en el commit `chore(drydock): start <id>` del siguiente bloque. La única excepción es el cierre del producto: `final-review.md` y el estado final van en un PR `chore/close`. Límite conocido: hasta ese commit, las aprobaciones de los gates y las specs de la rebanada viven solo en el árbol de trabajo.

**Contrato de `verify.py`** (lo envuelve `./verify.sh [--fast]`):

- Lee `.drydock/verify.json` en la raíz del repo (`git rev-parse --show-toplevel` desde el directorio actual). Claves: `steps[{name, mode: "fast"|"full", run}]` obligatoria; `base_branch` (por defecto `main`), `src_globs`, `test_globs` y `red` opcionales (`red` exige los dos globs).
- Ejecuta los pasos en orden con `sh` desde la raíz y corta en el primer fallo. `--fast` omite los pasos `full`.
- Si existe `red`, añade al final el paso interno `red-first`, en ambos modos.
- Escribe `.drydock/local/evidence/<sha>.<fast|full>.json` con `sha`, `mode`, `result`, `dirty`, `steps[{name, exit, seconds}]`, `tdd_exempt[{sha, reason}]` y `finished_at`. `dirty` se calcula al final con `git status --porcelain`.
- Salida: 0 pasa · 1 falla un paso · 2 error de configuración (sin evidencia).
- Evidencia válida para PR: `mode = full`, `result = pass`, `dirty = false`, `sha = HEAD`.
- Los globs usan `fnmatch`: `*` también cruza `/`, así que `*.cs` casa cualquier ruta que termine en `.cs`. Un archivo que casa `test_globs` no cuenta como código.

**Paso `red-first`:** recorre los commits de `base..HEAD` (sin merges, del más viejo al más nuevo). Un commit que toca `test_globs` y no `src_globs`, y cuyo comando `red` sale distinto de 0 en ese commit, arma su ámbito, que es el texto entre paréntesis del asunto (`test(B01/T003): …` arma `B01/T003`). Un commit que toca `src_globs` pasa si su ámbito está armado; si no, necesita `TDD-Exempt: <motivo>` o el paso falla. Un test sin ámbito arma un solo commit sin ámbito. El comando `red` corre en un `git worktree` temporal del commit de test y su resultado se guarda en `<sha>.red.json` (cada commit se evalúa una vez). La base se resuelve como `refs/remotes/origin/<base>` o, si no existe, `refs/heads/<base>`, para que el resultado local sea el de CI; CI necesita `fetch-depth: 0`.

**L2 frente al auto-merge (decisión de John).** Con el armado de un solo commit, cualquier tercer commit de una tarea (formato, hallazgo del revisor, refactor) necesitaba `TDD-Exempt`, y una exención apaga el auto-merge: las dos decisiones se anulaban. Queda aplicada la opción A, el armado por tarea. Opción B: volver al uno a uno y aceptar que el auto-merge dispare solo con parejas test y feat perfectas. H6 registra cuántos bloques T1 llegan de verdad al auto-merge.

**Contrato de `pr_gate.py`** (hook `PreToolUse` sobre `Bash`):

- Imprime **siempre** un único objeto JSON y sale 0. `{}` significa "sin opinión".
- Lee `tool_input.command` y `cwd` del JSON de stdin. Si el comando no es creación de PR, ni `gh pr merge`, ni `git push`: `{}`.
- Resuelve la raíz con `git -C <cwd> rev-parse --show-toplevel`. Si no es repo o no tiene `.drydock/`: `{}`.
- Creación de PR: niega si falta evidencia válida para `HEAD` o, con `state.current_block` no nulo, si `.drydock/local/reviews/<block>-<sha>.md` no empieza con `verdict: approve`.
- `gh pr merge` con bloque en curso: las mismas dos condiciones y, además, que el comando lleve `--match-head-commit <HEAD>`. Sin bloque en curso: `ask`, como segunda red cuando el repo no tiene las reglas de permisos (la regla `ask` del proyecto ya lo hace cuando están).
- `git push`: devuelve `ask` si la rama actual es la base o el comando la nombra.
- Ante un error interno: niega si la entrada parece una creación de PR o un merge, pregunta si parece un push y, si no, `{}`.
- El hook es respuesta rápida para el agente. La autoridad es CI y, donde el plan de GitHub lo permita, la protección de rama.

**`templates/settings.json`** (`init` fusiona en `.claude/settings.json` el bloque `permissions`; `harness install`, el archivo entero):

```json
{
  "permissions": {
    "allow": ["Bash(python3 *drydock.py *)", "Bash(./verify.sh*)"],
    "ask": ["Bash(*drydock.py gate pass*)", "Bash(*drydock.py deploy*)", "Bash(*gh pr merge*)"],
    "deny": ["Skill(speckit-implement)"]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3",
            "args": ["${CLAUDE_PROJECT_DIR}/.drydock/bin/pr_gate.py"],
            "onFailure": "block",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

`block merge` ejecuta `gh pr merge` dentro de la CLI, así que no dispara la regla `ask`: es el camino sin clic, y solo acepta T1.

**Contrato de `deploy`** (H5): `.drydock/deploy.json` = `{"deploy": "<cmd>", "smoke": "<cmd>"}`, sin secretos (los comandos leen credenciales del entorno de John). `drydock.py deploy` exige: fase `build` o `review`; en `build`, ningún bloque en curso y todos `done` (`slice has open blocks`); rama base, `HEAD` igual a `origin/<base>`, ningún cambio fuera de los archivos de estado. Corre `./verify.sh`, luego `deploy`, luego `smoke`, y escribe `<sha>.deploy.json`. Sale 0 · 1 · 2 (sin `deploy.json`). No hay rollback automático: un fallo se corrige con un bloque nuevo o a mano. El despliegue es siempre este comando explícito: ningún workflow despliega por push a la base, porque cada auto-merge de T1 desplegaría sin aprobación.

### A6. Arnés por repo

```
<producto>/
├── verify.sh                      # exec python3 "$(dirname "$0")/.drydock/bin/verify.py" "$@"
├── AGENTS.md  CLAUDE.md           # CLAUDE.md = @AGENTS.md + lo propio de Claude Code
├── CLAUDE.local.md                # personal, sin versionar
├── PROJECT_STATE.md               # generado
├── .drydock/
│   ├── state.json  routing.json  blocks.json  verify.json  deploy.json  metrics.jsonl
│   ├── bin/verify.py  bin/pr_gate.py
│   └── local/                     # sin versionar: evidence/ y reviews/
├── .claude/settings.json          # hook, ask, allow, deny
├── .claude/agents/drydock-*.md  # generados
├── .github/workflows/verify.yml
├── .specify/  specs/  .claude/skills/speckit-*/     # Spec Kit
└── docs/drydock/  docs/adr/
```

El contenido y los límites de `AGENTS.md`, `CLAUDE.md` y `CLAUDE.local.md` son los de v0 (A6): `AGENTS.md`, de 60 líneas como máximo, lleva comandos, reglas de capas, convención de ramas (`block/<id>`) y de commits (`test(…)`, `feat(…)`), dónde están specs y ADR y qué no hacer; `CLAUDE.md` importa `@AGENTS.md` y añade que el flujo lo dirige `/drydock`, el límite de superpowers y que no se abre PR sin verify. `PROJECT_STATE.md` se genera solo desde archivos versionados; el paso exacto dentro de un bloque lo da `drydock.py status`, que sí lee la evidencia local.

### A7. Curaduría de skills

Las reglas son las de v0, pero el entorno real ya no las cumple: hay nueve plugins activos a nivel de usuario (ECC completo entre ellos) y hooks que inyectan contexto en cada subagente (ver «Entorno leído»). Valor por defecto: se acepta lo instalado, la aceptación de H1 (paso 9) mide si interfiere, y solo entonces se apaga ese plugin en los repos gestionados con `enabledPlugins` (A9). Otras dos notas: las cifras del ecosistema citadas en v0 no se volvieron a comprobar, y la versión de Spec Kit se anota y se congela por producto.

### A8. Decisiones abiertas: resueltas

| # | Decisión | Resultado |
|---|---|---|
| 1 | Nombre | `drydock` (antes `astillero`; cambio de John del 2026-11-15, por si se publica) |
| 2 | Alcance del "100" | Incluye despliegue real; lo ejecuta drydock con tu aprobación; obligatorio al cerrar cada rebanada |
| 3 | Orden revisión/verify | Rápido → revisión → completo |
| 4 | Revisor en T3 | Escalado (`reviewer-t3`) |
| 5 | Merge | Auto-merge de T1 desde V1; T2 y T3, John |
| 6 | Stack del piloto | .NET 10 |
| 7 | superpowers | Se mantiene, limitado por `CLAUDE.md` |
| 8 | Idioma | Todo en inglés, nombres y prosa |
| 9 | Codex | Skill completo (H7) |
| 10 | TDD | L2 desde el inicio |

### A9. Fuera de V1 y qué lo activaría

| No se construye | Se añade cuando |
|---|---|
| Plugin y marketplace | Haga falta en otra cuenta, o se quiera `claude plugin eval` |
| Preset de Spec Kit | Una plantilla obligue a corregir a mano dos veces |
| Bloques en paralelo con worktrees | El tiempo de pared sea el cuello de botella |
| Hook sobre el despacho de agentes | Se observe un despacho con `model` o `effort` distintos al ruteo |
| Veredicto capturado por `SubagentStop`, o registrado por el propio revisor | El archivo de `reviews/` difiera de la respuesta del revisor (se compara en la aceptación de H2 y en H6) |
| `block abort` | Un bloque se abandone y recuperarlo exija editar el estado a mano |
| Contador de commits de código en la evidencia de `red-first` | Un bloque con código pase `red-first` sin que ningún archivo case `src_globs` |
| Aviso de `doctor` por topes de esfuerzo o de modelos en settings | `/tasks` muestre un modelo o esfuerzo distinto al de `routing.json` |
| Filtro `if` en el hook | La latencia del hook en cada Bash se note |
| Matcher para PR por MCP o `gh api` | Se conecte un servidor MCP de GitHub o se observe esa vía |
| Sonda "verde en la base" para red-first | Un bloque pase red-first porque el comando falla por entorno |
| Saltar red-first en CI | El tiempo de CI por PR moleste |
| Rollback automático, varios entornos, productos sin servidor | El piloto lo pida |
| Plantillas de verify para otros stacks | Empiece un producto en ese stack |
| Desactivar plugins por repo (`enabledPlugins`) | Un plugin de John interfiera con el flujo |
| Estado inyectado al iniciar sesión | Retomar un repo cueste más de un comando |

---

## Parte B — Plan de construcción

### B0. Paso 0 (al aprobar este plan)

- [ ] Actualizar herramientas (pedido por John): `claude plugin marketplace update` y después `claude plugin update <id>`, uno por uno y sin `-y`, para context-mode, ecc, ponytail, rembric, gsd y los de claude-plugins-official; `uv tool upgrade headroom-ai`; `codebase-memory-mcp update`. Si un plugin declara un comando de instalación, se le muestra a John antes de correrlo. Fuera, salvo que John lo pida: Spec Kit (se decide en H3), Homebrew, npm y pstack.
- [ ] Mover la carpeta: `mv ~/Developer/astillero ~/Developer/drydock` (ya contiene `docs/superpowers/plans/`) y abrir una sesión nueva en `~/Developer/drydock`, que además carga las herramientas actualizadas. La memoria de proyecto de Claude Code va por ruta: la sesión nueva no hereda la de esta.
- [ ] `git -C ~/Developer/drydock init -b main`
- [ ] Crear `.gitignore` con la línea `__pycache__/`.
- [ ] Copiar el v0 (`~/Downloads/2026-11-15-astillero-plan-v0.md`) a `docs/superpowers/plans/2026-11-15-astillero-plan-v0.md` (conserva su nombre de archivo) y la versión final de este plan a `docs/superpowers/plans/2026-11-15-drydock-plan-v1.md`. La evidencia de verificación y los hallazgos de la revisión ya están en esa carpeta. Borrar `docs/superpowers/plans/2026-11-15-pending.md`.
- [ ] `git add -A && git commit -m "docs: add plan v0 and v1"`

Sin remoto todavía: se crea al cerrar H1, con confirmación de John (cuenta y visibilidad).

**Convención de commits de todo el plan:** dos commits por ciclo, `test(T<n>): …` con los tests en rojo y `feat(T<n>): …` con la implementación. Sin líneas de atribución. Es el mismo ciclo que `red-first` exigirá cuando el repo se instale su propio arnés (cierre de H1).

### B1. Restricciones globales

- Python ≥ 3.9, solo librería estándar. `from __future__ import annotations`; sin `match`, sin `pip`, sin `jq`, sin YAML.
- Ningún nombre de modelo fuera de `templates/routing.json` (lo comprueba un test).
- `SKILL.md` ≤ 80 líneas; cada `phases/*.md` ≤ 120; cada `adapters/*.md` ≤ 60; `AGENTS.md` y `CLAUDE.md` generados ≤ 60 cada uno.
- Tras `prepare`, los gates del repo funcionan sin el skill: `verify.py` y `pr_gate.py` no importan nada de drydock.
- Evidencia y veredictos nunca se versionan y siempre van atados al SHA de `HEAD`.
- Spec Kit no se modifica.
- `harness install` nunca pisa `verify.json` ni el workflow; `--force` solo pisa `verify.sh`, `verify.py` y `pr_gate.py`; conserva lo que ya haya en `.claude/settings.json`.
- `pr_gate.py` imprime siempre un único objeto JSON y sale 0.
- Salidas de la CLI: 0 bien · 1 rechazado o chequeo fallido · 2 entorno (no es repo git, sin inicializar, estado ilegible). Los errores van a stderr como `error: <mensaje>`.
- Todo texto que se entrega (skill, CLI, plantillas, mensajes) en inglés. Este plan, en español.
- Tests: `python3 -m unittest discover -s tests -v`; un solo archivo con `-p "test_state.py"`. Sin `tests/__init__.py`: los tests importan `from helpers import …`. Cada test crea su repo temporal con `git init -b main` y neutraliza la configuración global de git. Cada «correr y ver pasar» se repite con `/usr/bin/python3` (3.9.6 en esta máquina), que es el piso declarado.
- La red que toca la CLI: `gh` (`block merge`, y `block close` sin `--merged-sha`), `git fetch` y `git pull` contra `origin` en `block close`, y el comando de despliegue del repo.

### B2. Foco de revisión

Fallos que el diseño implica y que ningún test cubriría por defecto. Cada uno tiene su test en la tarea dueña.

1. **PR o merge por una vía que el hook no ve** (comando compuesto, alias `pr new`, ruta absoluta, `bash -c` y `-lc`, `if …; then`, push directo a la base, push más interfaz web). Se espera negación o pregunta; lo que el hook no ve lo detiene CI como check requerido (aceptación de H1, paso 7). → `test_pr_command_forms_detected`, `test_push_to_base_asks`, `test_merge_in_block_needs_evidence_review_and_head` (T4).
2. **Evidencia que no corresponde al árbol real** (commit posterior, árbol sucio, subcarpeta) o auto-merge de algo distinto a lo verificado. → `test_stale_evidence_denied`, `test_dirty_is_computed_after_steps`, `test_cwd_subdirectory`, `test_refuses_when_pr_head_differs`, `test_refuses_harness_changes` (T3, T4, T6C).
3. **Gate que falla abierto o skill que no carga** (script roto, stdin basura, estado corrupto). → `test_internal_error_fails_closed`, `test_garbage_stdin`, `test_status_soft_never_fails`, `test_doctor_errors` (T1, T4, T5).
4. **Ruteo pisado** por variables de entorno o parámetros en el despacho. → `test_doctor_warnings_do_not_fail` (T5) y escenario 07; los topes de esfuerzo en settings se ven en `/tasks` (aceptación de H2, paso 3).
5. **`tasks.md` ausente, vacío o con otro formato, tareas sin asignar o líneas sin id.** → `test_all_tasks_assigned` con dos fixtures, `test_checklist_line_without_id_rejected`, `test_task_in_other_format_rejected`, `test_empty_plan_rejected` (T6A).
6. **Sesión cortada a mitad de bloque.** → `test_status_mid_block_shows_next_action` (T6B).
7. **red-first con resultado falso** (test verde en su commit, caché, worktree huérfano). → `test_green_test_does_not_arm`, `test_cache_is_used`, `test_leaves_no_worktree_behind` (T3).
8. **Archivos ajenos barridos a un bloque** (`.env`, artefactos de build, trabajo a medias) o un plan de otra rebanada. → `test_block_start_refuses_unexpected_pending_paths` (T6B), `test_plan_of_another_slice_rejected` (T6A).

### B3. Estructura de archivos (repo `drydock`)

```
drydock/                          # enlazado a ~/.claude/skills/drydock (y a ~/.agents/skills/drydock en H7)
├── SKILL.md                        # router: inyecta el estado y carga la fase
├── phases/1-requirements.md  2-architecture.md  3-audit.md  4-prepare.md
│          5-specs.md  6-blocks.md  7-build.md  8-review.md
├── adapters/claude.md  codex.md    # cómo se despacha y se aprueba en cada herramienta (codex.md en H7)
├── agents/openai.yaml              # metadatos del skill para Codex (H7)
├── bin/drydock.py                # CLI única
├── templates/
│   ├── routing.json  settings.json  verify.sh  verify.py  pr_gate.py
│   ├── verify-steps/dotnet.json    ci/github-actions-dotnet.yml
│   ├── agents/{impl,reviewer,auditor,final-reviewer}.md.tmpl
│   ├── AGENTS.md.tmpl  CLAUDE.md.tmpl  CLAUDE.local.md.tmpl          # H4
│   └── docs/{brief,stack,audit,adr,skills,final-review}.md           # H3–H5
├── tests/helpers.py  fake_gh.py  fixtures/tasks-{a,b}.md  test_*.py
├── scenarios/                      # pruebas de las fases en prosa
├── docs/superpowers/plans/         # v0, v1
├── verify.sh  .drydock/  .claude/settings.json  .github/workflows/verify.yml   # arnés propio, desde el cierre de H1
├── README.md
└── LEARNINGS.md                    # fallo observado → cambio hecho
```

Cada archivo de `phases/` acaba con las mismas secciones: Purpose, Inputs, Steps, Outputs, Gate, Common mistakes.

**Interfaz de la CLI** (`python3 bin/drydock.py <comando>`):

| Comando | Efecto | Salida |
|---|---|---|
| `init` | Crea `.drydock/state.json` y `routing.json`, añade `.drydock/local/` a `.gitignore`, genera `PROJECT_STATE.md`; desde T5 fusiona las reglas `permissions` en `.claude/settings.json` | 0 · 1 ya inicializado · 2 no es repo git |
| `status [--soft] [--phase]` | Fase, rebanada, bloque y siguiente acción. `--soft` sale 0 siempre. `--phase` imprime en su lugar el archivo de la fase en curso y el adaptador | 0 · 2 |
| `gate pass <phase> [--note T] [--next specs\|review]` | Corre el chequeo automático de la fase si existe, cierra el gate y avanza. `--next` es obligatorio en `build`; desde H5, opcional en `review` (`--next specs`) | 0 · 1 |
| `slice set <id>` | Fija la rebanada; solo en `specs` y si existe `specs/<id>/` | 0 · 1 |
| `render-state` | Regenera `PROJECT_STATE.md` (también lo hace todo comando que cambia estado) | 0 |
| `harness install --stack <s> [--force]` | Copia el arnés y fusiona `.claude/settings.json`. No requiere `init` | 0 · 1 |
| `doctor` | Arnés, hook, permisos, agentes, variables de entorno | 0 con o sin avisos · 1 con errores |
| `blocks validate` | Valida `blocks.json` contra `tasks.md` y `routing.json` | 0 · 1 con todos los errores |
| `agents render` | Escribe `.claude/agents/drydock-*.md` | 0 · 1 |
| `block start <id>` | Valida el plan, crea `block/<id>` desde la base y hace commit de lo pendiente si cae bajo `SWEEP_PATHS` | 0 · 1 |
| `block close <id> [--merged-sha S] [--attempts N] [--findings N]` | Comprueba que el merge está en la base, vuelve a ella, marca `done`, añade métricas. `--merged-sha` solo vale sin remoto `origin` | 0 · 1 |
| `block merge <id> [--attempts N] [--findings N]` | Solo T1: comprueba que el check `verify` está en verde, hace squash-merge y cierra | 0 · 1 |
| `block pr-body <id>` | Imprime el cuerpo del PR | 0 · 1 |
| `review record <id> --sha <sha>` | Guarda el texto del revisor leído por stdin | 0 · 1 |
| `deploy` (H5) | verify, despliegue y smoke; escribe evidencia de despliegue | 0 · 1 · 2 |
| `clean-clone` (H5) | Clona a un temporal y corre `./verify.sh` | Código de verify |

`state.json` inicial:

```json
{
  "version": 1,
  "phase": "requirements",
  "gates": {
    "requirements": null, "architecture": null, "audit": null, "prepare": null,
    "specs": null, "blocks": null, "build": null, "review": null
  },
  "slice": null,
  "slices_done": [],
  "current_block": null
}
```

Un gate cerrado guarda `{"passed_at": "2026-11-15T18:04:05Z", "note": "<texto o null>"}` (UTC). Tras `review`, `phase` pasa a `closed`.

`blocks.json`:

```json
{
  "version": 1,
  "slice": "001-skeleton",
  "tasks_file": "specs/001-skeleton/tasks.md",
  "blocks": [
    {
      "id": "B01",
      "title": "Walking skeleton",
      "tier": "T2",
      "tier_override": null,
      "depends_on": [],
      "status": "pending",
      "tasks": [
        {"id": "T001", "score": {"novelty": 1, "scope": 2, "risk": 0, "testing": 1, "ambiguity": 0}}
      ]
    }
  ]
}
```

Reglas de `blocks validate` y su mensaje (uno por línea en stderr, todos a la vez):

| Regla | Mensaje |
|---|---|
| Ids de bloque y de tarea únicos | `duplicate block id B01` · `duplicate task id T004` |
| Toda tarea de `tasks_file` asignada y ninguna inventada | `unassigned tasks: T003, T004` · `unknown tasks: T099` |
| Línea de casilla sin id en `tasks.md` | `tasks.md:2: checklist item without task id` |
| Cinco dimensiones con valor 0, 1 o 2 | `T001: score.risk must be 0, 1 or 2` · `T002: missing score.testing` |
| `tier` existe en `routing.json` | `B02: unknown tier T9` |
| `tier` no menor que el calculado | `B01: tier T1 is below computed T2` |
| `tier` mayor solo con `tier_override` | `B01: tier T2 above computed T1 needs tier_override` |
| Tareas por bloque ≤ `max_tasks` | `B01: 5 tasks exceeds max_tasks 4 for T2` |
| `depends_on` existe y no hay ciclos | `B01: unknown dependency B09` · `dependency cycle: B01 -> B03 -> B02 -> B01` |
| `status` es `pending`, `in_progress` o `done` | `B01: invalid status "wip"` |
| El plan es de la rebanada en curso | `blocks.json is for slice "000-old", current slice is "001-skeleton"` · `tasks_file must be specs/001-skeleton/tasks.md` |
| `tasks_file` existe y tiene tareas | `tasks file not found: specs/001-skeleton/tasks.md` · `no tasks found in specs/001-skeleton/tasks.md` |
| Id de tarea en un formato que no es el de Spec Kit | `tasks.md:2: task id in unsupported format` |

### B4. Hitos y tareas

Orden: T1 → T2 (H0) · T3 → T4 → T5 (H1) · T6A → T6B → T6C → T7 → T8 (H2) · H3 a H7 como contrato. En los bloques de test se omiten los `import`: librería estándar y nombres de `helpers`.

#### H0 — Esqueleto usable

### Tarea 1: estado y CLI base

**Archivos:**
- Crear: `bin/drydock.py`, `templates/routing.json`, `tests/helpers.py`, `tests/test_state.py`

**Interfaces:**
- Produce (CLI): `init`, `status`, `gate pass`, `slice set`, `render-state`, como en B3.
- Produce (Python, las tareas siguientes amplían el mismo archivo):

```python
PHASES = ("requirements", "architecture", "audit", "prepare", "specs", "blocks", "build", "review")
CLOSED = "closed"
STATE_PATHS = (".drydock/state.json", ".drydock/blocks.json", ".drydock/metrics.jsonl", "PROJECT_STATE.md")

class CliError(Exception):
    def __init__(self, code: int, message: str): ...
def git(root: Path, *args: str) -> str            # stdout sin espacios finales; CliError(1, stderr) si falla
def templates_dir() -> Path                       # Path(__file__).resolve().parent.parent / "templates"
def repo_root(cwd: Path) -> Path                  # CliError(2, "not a git repository")
def load_state(root: Path) -> dict                # CliError(2, "not initialized") · CliError(2, "state unreadable: <motivo>")
def save_state(root: Path, state: dict) -> None   # escribe JSON (indent=2, salto final) y llama a render_state
def render_state(root: Path) -> None              # escribe PROJECT_STATE.md
def next_action(root: Path, state: dict, live: bool) -> str
def ensure_gitignore(root: Path) -> None          # añade la línea ".drydock/local/" si falta
def now_utc() -> str                              # "%Y-%m-%dT%H:%M:%SZ"
def main(argv: Optional[list] = None) -> int      # argparse; CliError → "error: <mensaje>" en stderr y su código
```

- Produce (tests): `tests/helpers.py`.

- [ ] **Paso 1: escribir `templates/routing.json`** con el contenido exacto de A4.

- [ ] **Paso 2: escribir `tests/helpers.py`**

```python
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

    def set_phase(self, phase, slice=None):          # salta a una fase: init si hace falta, gates anteriores cerrados
        if not (self.repo / ".drydock/state.json").exists():
            self.cli("init")
        closed = {"passed_at": "2026-01-01T00:00:00Z", "note": None}
        gates = {p: (dict(closed) if PHASES.index(p) < PHASES.index(phase) else None) for p in PHASES}
        self.set_state(phase=phase, gates=gates, slice=slice)

    def snapshot(self):                              # {ruta relativa: bytes} de todo lo que no es .git
        files = (p for p in sorted(self.repo.rglob("*")) if p.is_file())
        return {str(p.relative_to(self.repo)): p.read_bytes() for p in files if ".git" not in p.relative_to(self.repo).parts}
```

- [ ] **Paso 3: escribir los tests que fallan** en `tests/test_state.py`

```python
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
        self.assertEqual(self.cli("gate", "pass", "build").returncode, 1)
        self.assertEqual(self.cli("gate", "pass", "build", "--next", "specs").returncode, 0)
        s = self.state()
        self.assertEqual((s["phase"], s["slice"], s["slices_done"]), ("specs", None, ["001-skeleton"]))
        self.assertEqual([s["gates"][p] for p in ("specs", "blocks", "build")], [None, None, None])
        self.assertIsNotNone(s["gates"]["prepare"])
        self.set_phase("build", slice="002-users")
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
```

- [ ] **Paso 4: correrlos y verlos fallar**

Correr: `python3 -m unittest discover -s tests -p "test_state.py" -v`
Esperado: 11 fallos (`bin/drydock.py` no existe).

- [ ] **Paso 5: commit** `git add templates tests && git commit -m "test(T1): state and base CLI"`

- [ ] **Paso 6: implementar `bin/drydock.py`** con las firmas del bloque Interfaces. Decisiones que los tests no fijan:

  - `init` comprueba primero que es repo git (2) y después que no existe `state.json` (1). `gate pass` sobre fase `closed` sale 1. `gate pass build` sin rebanada fijada sale 1 con `no slice set in build`.
  - `status` imprime exactamente cuatro líneas: `phase: <phase>`, `slice: <slice o ->`, `block: <id o ->`, `next: <frase>`. `--soft` convierte cualquier excepción (`except Exception`, no solo `CliError`) en `drydock: <mensaje>` por stdout y sale 0: un `state.json` o un `blocks.json` con forma rara no puede impedir que el skill cargue.
  - `gate pass build --next specs`: `phase = "specs"`; gates `specs`, `blocks` y `build` vuelven a `null`; `slice` pasa a `slices_done` y queda en `null`. `--next review`: cierra el gate `build`, mueve `slice` igual y avanza a `review`. Imprime `gate <phase> closed -> <nueva fase>`.
  - `PROJECT_STATE.md` (sin fechas, para que sea idempotente):

```markdown
<!-- Generated by drydock.py. Do not edit. -->
# Project state

- Phase: <phase>
- Slice: <slice o ->
- Block: <id o ->
- Gates closed: <lista separada por comas o ->
- Slices done: <lista separada por comas o ->

## Next

<next_action(root, state, live=False)>
```

  - Frases de `next_action` por fase:

```python
NEXT = {
    "requirements": "Write docs/drydock/brief.md with the user, then run: drydock.py gate pass requirements",
    "architecture": "Write docs/drydock/stack.md and the ADRs with the user, then run: drydock.py gate pass architecture",
    "audit": "Audit the stack into docs/drydock/audit.md, resolve blockers with the user, then run: drydock.py gate pass audit",
    "prepare": "Install the harness and render the agents, then run: drydock.py gate pass prepare",
    "specs": "Run the Spec Kit chain for the next slice and drydock.py slice set <id>, then run: drydock.py gate pass specs",
    "blocks": "Write .drydock/blocks.json and run drydock.py blocks validate, then run: drydock.py gate pass blocks",
    "build": "Start the next pending block: drydock.py block start <id>",
    "review": "Run the final review and drydock.py clean-clone, then run: drydock.py gate pass review",
    "closed": "Nothing: the project is closed",
}
```

- [ ] **Paso 7: correr y ver pasar**

Correr: `python3 -m unittest discover -s tests -p "test_state.py" -v`
Esperado: `Ran 11 tests … OK`

- [ ] **Paso 8: commit** `git add bin && git commit -m "feat(T1): state and base CLI"`

### Tarea 2: router y stubs de fase

**Archivos:**
- Crear: `SKILL.md`, `phases/1-requirements.md` … `phases/8-review.md`, `adapters/claude.md`, `README.md`, `LEARNINGS.md`, `tests/test_budgets.py`, `scenarios/00-router.md`
- Modificar: `bin/drydock.py` (`status --phase`), `tests/test_state.py`

**Interfaces:**
- Consume: `status --soft` (T1).
- Produce (CLI): `status --soft --phase` imprime `phases/<n>-<phase>.md` de la fase en curso, una línea en blanco y `adapters/claude.md`, resueltos desde la carpeta del skill; en fase `closed` no imprime nada.
- Produce: el skill invocable como `/drydock`; los nombres de archivo `phases/<n>-<phase>.md` que T8 y H3–H5 rellenan.

- [ ] **Paso 1: escribir los tests que fallan** en `tests/test_budgets.py`

```python
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
        self.assertIn("!`python3 ${CLAUDE_SKILL_DIR}/bin/drydock.py status --soft --phase`", text)
```

Y un test más en `tests/test_state.py`, dentro de `StateTests` (el `import` de `helpers` gana `ROOT`):

```python
    def test_status_phase_prints_phase_file_and_adapter(self):
        self.cli("init")
        r = self.cli("status", "--soft", "--phase")
        self.assertEqual(r.returncode, 0, r.stderr)
        expected = (ROOT / "phases" / "1-requirements.md").read_text() + "\n" + (ROOT / "adapters" / "claude.md").read_text()
        self.assertEqual(r.stdout, expected)
        self.set_phase("review")
        self.cli("gate", "pass", "review")
        self.assertEqual(self.cli("status", "--soft", "--phase").stdout, "")     # closed: no phase file
```

- [ ] **Paso 2: correrlos y verlos fallar**

Correr: `python3 -m unittest discover -s tests -v`
Esperado: 4 errores en `test_budgets.py` (`SKILL.md` y `phases/` no existen) y 1 fallo en `test_state.py` (`status` no conoce `--phase`).

- [ ] **Paso 3: commit** `git add tests && git commit -m "test(T2): budgets and skill frontmatter"`

- [ ] **Paso 4: escribir `SKILL.md`** con este contenido exacto

```markdown
---
name: drydock
description: Drives a software product from idea to merged, reviewed and deployed code through gated phases. Use when the user runs /drydock or $drydock, or asks to continue the drydock flow in a repository.
argument-hint: "[status]"
disable-model-invocation: true
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/bin/drydock.py status*)
---

# Drydock

State: !`python3 ${CLAUDE_SKILL_DIR}/bin/drydock.py status --soft`

If the State line still shows the command instead of its output, run it yourself:
`python3 <directory of this file>/bin/drydock.py status --soft`.

`drydock.py <command>`, here and in every phase file, means
`python3 <directory of this file>/bin/drydock.py <command>` run from inside the product repository.

## Phase

!`python3 ${CLAUDE_SKILL_DIR}/bin/drydock.py status --soft --phase`

## Rules

1. State says `not initialized`: explain that `drydock.py init` creates `.drydock/` and adds permission rules to `.claude/settings.json` in this repository, run it only after the user agrees, then stop.
2. The Phase section above holds the phase file for the phase in State, followed by `adapters/claude.md`. Only if it still shows the command, read them yourself: `phases/<n>-<phase>.md` (1 requirements, 2 architecture, 3 audit, 4 prepare, 5 specs, 6 blocks, 7 build, 8 review) and `adapters/claude.md`. Never read another phase to get ahead.
3. Follow that phase file step by step. Its Gate section is the only definition of done.
4. A gate closes only with `drydock.py gate pass <phase>`, after its condition holds. The user approves that command. Never rephrase a command to avoid an approval prompt, and never edit `.drydock/state.json` or `.drydock/local/` by hand. If the command is denied without a prompt, stop and ask the user to run it themselves.
5. Argument `status`: print State and stop.
6. Phase `closed`: say the project is closed and stop.
7. When a CLI command fails, show its message and fix the cause. Do not skip the step.
```

- [ ] **Paso 5: escribir los 8 stubs de fase** con esta plantilla y los datos de la tabla

```markdown
# Phase <n>: <phase>

## Purpose
<Purpose>.

## Gate
<Gate>. Close it with `drydock.py gate pass <phase>`.

## Status
Not built yet (milestone <H>). Do this phase by hand until the gate condition holds; do not invent extra steps.
```

| Archivo | Purpose | Gate | H |
|---|---|---|---|
| `1-requirements.md` | Interrogate the user one question at a time until `docs/drydock/brief.md` is complete | The user approves the brief | H3 |
| `2-architecture.md` | Agree the stack with pinned versions and official sources, and the deploy target; write `docs/drydock/stack.md` and one ADR per decision | The user approves the stack | H3 |
| `3-audit.md` | Have a clean-context auditor challenge the stack; record findings in `docs/drydock/audit.md` | No blocker is open | H3 |
| `4-prepare.md` | Install the harness, render the agents, choose skills, write `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md` and `.drydock/deploy.json` | `drydock.py doctor` reports no errors | H4 |
| `5-specs.md` | Run the Spec Kit chain for the next slice | `/speckit-analyze` reports no CRITICAL finding and the user approves the spec | H3 |
| `6-blocks.md` | Score the tasks, group them into blocks and assign tiers in `.drydock/blocks.json` | `drydock.py blocks validate` passes and the user approves the plan | H2 |
| `7-build.md` | Build each block: red-first TDD, fast verify, independent review, full verify, PR, merge; deploy when the slice is complete | Every block is done and the slice is deployed | H2 |
| `8-review.md` | Review the whole product, start it from a clean clone, write the retro | No blocker is open and `drydock.py clean-clone` passes | H5 |

- [ ] **Paso 6: escribir `adapters/claude.md`, `README.md` y `LEARNINGS.md`, e implementar `status --phase`**

  - `adapters/claude.md`: la CLI es `python3 ${CLAUDE_SKILL_DIR}/bin/drydock.py <command>`; las aprobaciones llegan como prompts de permiso (`gate pass`, `deploy`, `gh pr merge`, push a la base) y se esperan sin reformular el comando, y si el modo de permisos las niega sin preguntar se le pide a John que corra el comando; una línea "Subagent dispatch: see Task 8" que T8 sustituye.
  - `README.md`: qué es, instalación (`ln -s "$HOME/Developer/drydock" "$HOME/.claude/skills/drydock"`; la ruta no puede llevar espacios), tabla de comandos de B3, y recuperación: si todo Bash queda bloqueado, el hook está fallando; correr `python3 .drydock/bin/pr_gate.py < /dev/null` en una terminal para ver el error.
  - `LEARNINGS.md`: solo el título y la cabecera de tabla `| Date | Observed failure | Change made |`.
  - `bin/drydock.py`: `status --phase`, como en Interfaces. Lee el estado igual que `status`, así que con `--soft` un repo sin inicializar imprime `drydock: not initialized` y sale 0.

- [ ] **Paso 7: correr y ver pasar**

Correr: `python3 -m unittest discover -s tests -v`
Esperado: `Ran 16 tests … OK`

- [ ] **Paso 8: escribir `scenarios/00-router.md`** con las secciones Setup, Prompt, Pass criteria, Log (sin línea base: sin el skill no hay router que comparar). Casos: (a) repo sin inicializar → propone `init` y no toca nada más; (b) fase `requirements` → sigue solo la fase 1, que llega inyectada, sin leer ningún archivo del skill; (c) `/drydock status` → imprime el estado y termina. Comando sin intervención: `claude -p "/drydock" --permission-mode dontAsk --output-format json` en un repo temporal.

- [ ] **Paso 9: commit** `git add -A && git commit -m "feat(T2): router skill and phase stubs"`

**Aceptación de H0** (a mano; pide confirmación a John antes de crear el enlace en `~/.claude/skills`):

1. Crear el enlace y abrir Claude Code en un repo git vacío de prueba. `/drydock` muestra `drydock: not initialized` en la línea State, sin prompt de permiso, y propone `init`.
2. Tras `init`, `/drydock` sigue solo la fase 1 (`phases/1-requirements.md`, inyectada por `status --soft --phase`), sin leer archivos del skill.
3. `claude -p "/drydock status"` imprime el estado y termina.
4. Anotar en el Log del escenario 00 la fecha, `claude --version` y si `${CLAUDE_SKILL_DIR}` apuntó al enlace o al destino.
5. En el modo habitual de John (`dontAsk`), `drydock.py gate pass requirements` se niega sin prompt, y el skill se detiene y le pide a John que lo corra él (regla 4).

Contingencia si el paso 1 pide permiso o aborta: cambiar `allowed-tools` a `Bash(python3 *drydock.py status*)` y actualizar `test_skill_frontmatter_matches_injection`.

#### H1 — Gates deterministas

**Paso 0 de H1 (antes de T3, con John delante, unos 20 minutos).** T4 y T5 fijan con aserciones exactas la forma del hook y de los permisos. Antes de escribirlas se comprueban sus supuestos en un repo temporal, con un hook de diez líneas que imprime una decisión fija y un `.claude/settings.json` de usar y tirar. Nada de esto se versiona.

- [ ] `{}` con salida 0 no bloquea Bash bajo `onFailure: "block"`; un script que revienta sí.
- [ ] Una decisión `deny` y una `ask` del hook llegan al agente y a John, y un subagente recibe la misma.
- [ ] Las reglas `ask` con comodín inicial (`Bash(*drydock.py gate pass*)`) ganan a `allow`, también a la regla `Bash(gh pr merge:*)` del usuario.
- [ ] Qué hace cada `ask` (regla y hook) en `default`, `acceptEdits`, `dontAsk`, `auto` y `bypassPermissions`: pregunta, niega o deja pasar.
- [ ] Con los plugins de John activos, cómo se combinan sus hooks `PreToolUse` sobre Bash con el nuestro.
- [ ] Si un hook, una regla de permisos o un agente creados a mitad de sesión cargan sin reiniciarla.
- [ ] En `dontAsk`, qué pasa con lo que no tiene regla `allow` (Edit, Write, `git commit`, `gh pr create`): si se niega, A5 declara que drydock se trabaja en `default` o `acceptEdits` y que `dontAsk` solo sirve para `status` y el escenario 00.

Resultados a `LEARNINGS.md`. Si `ask` deja pasar sin preguntar en un modo que John usa, se cambia a la opción B de A5 antes de T4.

### Tarea 3: verify y red-first

**Archivos:**
- Crear: `templates/verify.py`, `templates/verify.sh`, `tests/test_verify.py`
- Modificar: `tests/helpers.py` (añadir `install_verify`, `set_verify`)

**Interfaces:**
- Produce: el contrato de `verify.py` y de `red-first` de A5; el formato de evidencia que consumen T4, T6B, T6C y T8.

```python
# templates/verify.py — autónomo, sin imports de drydock
TRAILER_RE = re.compile(r"^TDD-Exempt:\s*(\S.*)$", re.M)
SCOPE_RE = re.compile(r"^\w+\(([^)]+)\)!?:")             # "test(B01/T003): …" -> "B01/T003"
def git(root: Path, *args: str) -> str
def repo_root() -> Path                                   # desde el directorio actual; sale 2 si no es repo
def load_config(root: Path) -> dict                       # sale 2 si falta, no es JSON, steps es inválido o red viene sin los dos globs
def run_step(root: Path, name: str, command: str) -> dict # {"name", "exit", "seconds"}; salida del comando sin capturar
def matches(path: str, globs: list) -> bool               # fnmatch.fnmatchcase
def resolve_base(root: Path, base: str) -> str            # refs/remotes/origin/<base> o, si no existe, refs/heads/<base>; sale 2 si ninguna
def is_red(root: Path, sha: str, command: str) -> bool    # caché <sha>.red.json; si no, corre command en un worktree temporal
def red_first(root: Path, config: dict) -> tuple          # (exit, tdd_exempt)
def main(argv: Optional[list] = None) -> int
```

- [ ] **Paso 1: añadir a `tests/helpers.py`** (métodos de `RepoCase`)

```python
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
```

- [ ] **Paso 2: escribir los tests que fallan** en `tests/test_verify.py`

```python
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
```

- [ ] **Paso 3: correrlos y verlos fallar**

Correr: `python3 -m unittest discover -s tests -p "test_verify.py" -v`
Esperado: 21 errores en `setUp` (`templates/verify.py` no existe).

- [ ] **Paso 4: commit** `git add tests && git commit -m "test(T3): verify and red-first"`

- [ ] **Paso 5: implementar `templates/verify.sh` y `templates/verify.py`**

`templates/verify.sh`, exacto:

```sh
#!/bin/sh
exec python3 "$(dirname "$0")/.drydock/bin/verify.py" "$@"
```

`verify.py`: firmas del bloque Interfaces y contrato de A5. Cada paso imprime `== <name> ==` y deja pasar la salida del comando; la última línea es `verify <mode>: pass` o `verify <mode>: fail (<step>)`. Los errores de configuración salen por stderr como `verify: config error: <mensaje>`; `red` sin `src_globs` o sin `test_globs` da `"red" requires src_globs and test_globs`. `is_red` crea el worktree con `git worktree add --detach <tmp> <sha>` sobre un `tempfile.mkdtemp(prefix="drydock-red-")`, corre el comando con la salida descartada y lo retira en un `finally` con `git worktree remove --force`. El algoritmo de `red_first`, que las firmas no determinan:

```python
def red_first(root, config):
    base = resolve_base(root, config.get("base_branch", "main"))
    armed, exempt = set(), []                       # ámbitos con un test en rojo; None es un commit sin ámbito
    for sha in git(root, "rev-list", "--reverse", "--no-merges", f"{base}..HEAD").split():
        files = git(root, "-c", "core.quotePath=false", "diff-tree", "--no-commit-id", "--name-only", "-r", sha).splitlines()
        message = git(root, "log", "-1", "--format=%B", sha)
        scope = (SCOPE_RE.match(message) or [None, None])[1]
        touches_test = any(matches(f, config["test_globs"]) for f in files)
        touches_src = any(matches(f, config["src_globs"]) and not matches(f, config["test_globs"]) for f in files)
        if touches_src:
            trailer = TRAILER_RE.search(message)
            if trailer:
                exempt.append({"sha": sha, "reason": trailer.group(1).strip()})
            elif scope in armed:
                if scope is None:
                    armed.discard(None)             # sin ámbito, un test arma un solo commit
            else:
                print(f"red-first: {sha[:7]} changes source with no failing test commit before it. "
                      "Commit the test first, or add a 'TDD-Exempt: <reason>' trailer.")
                return 1, exempt
        elif touches_test and is_red(root, sha, config["red"]):
            armed.add(scope)
    return 0, exempt
```

Atajo conocido, como comentario en el código: `# shortcut: "red" means non-zero exit in a clean worktree; add a green-at-base probe if a stack's test command can fail for missing dependencies`.

- [ ] **Paso 6: correr y ver pasar**

Correr: `python3 -m unittest discover -s tests -p "test_verify.py" -v`
Esperado: `Ran 21 tests … OK`

- [ ] **Paso 7: commit** `git add templates tests && git commit -m "feat(T3): verify and red-first"`

### Tarea 4: gate de PR y de push

**Archivos:**
- Crear: `templates/pr_gate.py`, `templates/settings.json`, `tests/test_pr_gate.py`
- Modificar: `tests/helpers.py` (añadir `write_evidence`, `write_review`)

**Interfaces:**
- Consume: formato de evidencia (T3), `state.json` (T1).
- Produce: el contrato de `pr_gate.py` y `templates/settings.json` de A5.

```python
# templates/pr_gate.py — autónomo
SEP = (r"(?:^|[;&|\n(`{!]|\$\(|-\w*c\s+[\"']|\b(?:then|do|else|time|exec|command|env|nohup|eval|timeout\s+\S+)\s+[\"']?)"
       r"\s*(?:\w+=\S*\s+)*(?:\S*/)?")
PR_RE = re.compile(SEP + r"gh\b[^|;&\n]*\bpr\s+(?:create|new)\b")
MERGE_RE = re.compile(SEP + r"gh\b[^|;&\n]*\bpr\s+merge\b")
PUSH_RE = re.compile(SEP + r"git(?:\s+-[cC]\s+\S+|\s+--[\w-]+(?:=\S+)?)*\s+push\b")
LOOSE_RE = re.compile(r"\bgh\b.*\bpr\b.*\b(?:create|new|merge)\b", re.S)
LOOSE_PUSH_RE = re.compile(r"\bgit\b.*\bpush\b", re.S)
def decision(kind: str, reason: str) -> dict   # {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": kind, "permissionDecisionReason": reason}}
def decide(payload: dict) -> dict              # {} = sin opinión
def main() -> int                              # imprime un único objeto JSON; devuelve 0 siempre
```

Las expresiones se ejecutaron el 2026-11-15 contra las listas de los tests de abajo; falta verlas dentro de un hook real (Paso 0 de H1). El precio de cubrir más formas es algún falso positivo, que falla cerrado: `git commit -m "then gh pr create"` sin evidencia se niega. Atajo conocido, como comentario: `# shortcut: regex, not a shell parser; CI is the authority`.

- [ ] **Paso 1: añadir a `tests/helpers.py`** (métodos de `RepoCase`)

```python
    def write_evidence(self, mode="full", result="pass", dirty=False, sha=None, tdd_exempt=()):
        sha = sha or self.head()
        return self.write_json(f".drydock/local/evidence/{sha}.{mode}.json",
                               {"sha": sha, "mode": mode, "result": result, "dirty": dirty, "steps": [],
                                "tdd_exempt": list(tdd_exempt), "finished_at": "2026-01-01T00:00:00Z"})

    def write_review(self, block, verdict="approve", sha=None):
        return self.write(f".drydock/local/reviews/{block}-{sha or self.head()}.md", f"verdict: {verdict}\n\nok\n")
```

- [ ] **Paso 2: escribir los tests que fallan** en `tests/test_pr_gate.py`

```python
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
```

- [ ] **Paso 3: correrlos y verlos fallar**

Correr: `python3 -m unittest discover -s tests -p "test_pr_gate.py" -v`
Esperado: 15 fallos (`templates/pr_gate.py` y `templates/settings.json` no existen).

- [ ] **Paso 4: commit** `git add tests && git commit -m "test(T4): PR and push gate"`

- [ ] **Paso 5: implementar `templates/settings.json`** (contenido exacto de A5) **y `templates/pr_gate.py`**

`main()` es la única red de seguridad y su forma está fijada:

```python
def main():
    raw = sys.stdin.read()
    try:
        out = decide(json.loads(raw))
    except Exception as exc:                        # falla cerrado si la entrada parece un PR, un merge o un push
        reason = f"pr_gate internal error: {exc!r}"
        out = decision("deny", reason) if LOOSE_RE.search(raw) else decision("ask", reason) if LOOSE_PUSH_RE.search(raw) else {}
    print(json.dumps(out))
    return 0
```

`decide(payload)`, en este orden:

1. `command = payload["tool_input"]["command"]`. Si no casa con `PR_RE`, `MERGE_RE` ni `PUSH_RE`: `{}`.
2. Raíz con `git -C <cwd> rev-parse --show-toplevel` (`cwd` del payload, o el directorio actual). Si falla o no existe `<raíz>/.drydock/`: `{}`.
3. Creación de PR, o merge (`MERGE_RE`) cuando `state.json` existe y `current_block` no es nulo; un merge sin bloque en curso devuelve `ask` (A5). Con `head = git rev-parse HEAD`; si no hay `HEAD` (repo sin commits), deny:
   - Sin `.drydock/local/evidence/<head>.full.json`: deny `No full verify evidence for commit <head7>. Run ./verify.sh and retry.`
   - Evidencia que no cumple `sha == head`, `mode == "full"`, `result == "pass"`, `dirty is False`: deny `Verify evidence for <head7> is not a clean full pass (result=<r>, dirty=<d>). Commit or ignore the pending files, then run ./verify.sh.`
   - `state.json` existe, `current_block` no es nulo y la primera línea de `.drydock/local/reviews/<block>-<head>.md` no es `verdict: approve`: deny `Block <block> has no approving review for commit <head7>. Dispatch the reviewer and run drydock.py review record.`
   - Merge cuyo comando no contiene `--match-head-commit <head>` con el SHA completo: deny `Add --match-head-commit <head> to the merge command so it cannot include unreviewed commits.`
   - Si no: `{}`, o el resultado del paso 4 si el comando también casa `PUSH_RE`.
4. `git push`, con `base` = `base_branch` de `.drydock/verify.json` (o `main`) y `branch = git rev-parse --abbrev-ref HEAD`: si `branch == base` o `re.search(rf"(?:^|[\s:+\"']|refs/heads/){re.escape(base)}(?![\w./-])", command)`: ask `Direct push to the base branch "<base>". Drydock integrates through block PRs; approve only for repository bootstrap.` Si no: `{}`.

- [ ] **Paso 6: correr y ver pasar**

Correr: `python3 -m unittest discover -s tests -p "test_pr_gate.py" -v`
Esperado: `Ran 15 tests … OK`

- [ ] **Paso 7: commit** `git add templates tests && git commit -m "feat(T4): PR and push gate"`

### Tarea 5: instalación del arnés y doctor

**Archivos:**
- Crear: `templates/verify-steps/dotnet.json`, `templates/ci/github-actions-dotnet.yml`, `tests/test_harness.py`
- Modificar: `bin/drydock.py` (`harness install`, `doctor`, chequeo en `gate pass`; `init` fusiona `permissions`)

**Interfaces:**
- Consume: T3, T4, `ensure_gitignore` y `templates_dir` (T1).
- Produce:

```python
GATE_CHECKS = {}                                              # fase -> función(root) que devuelve la lista de errores
def merge_settings(existing: dict, template: dict) -> dict
def doctor_report(root: Path) -> tuple                        # (errores, avisos)
GATE_CHECKS["prepare"] = lambda root: doctor_report(root)[0]
```

`cmd_gate_pass` corre `GATE_CHECKS.get(phase)` antes de tocar el estado; si devuelve errores, los imprime como `error: …` y sale 1.

- [ ] **Paso 1: escribir los tests que fallan** en `tests/test_harness.py`

```python
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
```

- [ ] **Paso 2: correrlos y verlos fallar**

Correr: `python3 -m unittest discover -s tests -p "test_harness.py" -v`
Esperado: 12 fallos (argparse no conoce `harness` ni `doctor`; `init` aún no escribe settings).

- [ ] **Paso 3: commit** `git add tests && git commit -m "test(T5): harness install and doctor"`

- [ ] **Paso 4: escribir las plantillas**

`templates/verify-steps/dotnet.json`, exacto:

```json
{
  "base_branch": "main",
  "src_globs": ["*.cs"],
  "test_globs": ["tests/*", "*Tests/*"],
  "red": "dotnet test --filter Category!=Integration",
  "steps": [
    {"name": "format", "mode": "fast", "run": "dotnet format --verify-no-changes"},
    {"name": "build", "mode": "fast", "run": "dotnet build -warnaserror"},
    {"name": "unit", "mode": "fast", "run": "dotnet test --no-build --filter Category!=Integration"},
    {"name": "integration", "mode": "full", "run": "dotnet test --no-build --filter Category=Integration"}
  ]
}
```

Los globs son amplios a propósito: cualquier `.cs` es código salvo lo que viva bajo `tests/` o una carpeta `*Tests/`; la fase `prepare` los ajusta al layout real (T11).

`templates/ci/github-actions-dotnet.yml`: un workflow con `name: verify` (el nombre que `block merge` busca entre los checks) y un job `verify` en `ubuntu-latest`, disparado por `pull_request` y por `push` a `main`, con `actions/checkout` (`fetch-depth: 0`), `actions/setup-dotnet` (`dotnet-version: "10.0.x"`) y `run: ./verify.sh`. Antes de escribirlo, fijar la versión mayor vigente de cada acción con `gh api repos/actions/checkout/releases/latest --jq .tag_name` (lo mismo para `setup-dotnet`).

- [ ] **Paso 5: implementar `harness install` y `doctor`**

  - `harness install`: copia `verify.sh` (modo 755), `verify.py`, `pr_gate.py`, `verify-steps/<stack>.json` → `.drydock/verify.json` y `ci/github-actions-<stack>.yml` → `.github/workflows/verify.yml`. Un archivo que existe se conserva; `--force` reescribe solo los tres scripts. Llama a `ensure_gitignore`. Imprime una línea por archivo: `created <ruta>`, `kept <ruta>`, `overwrote <ruta>`, `merged .claude/settings.json`. Stack desconocido: sale 1 y lista en stderr los nombres de `templates/verify-steps/*.json`.
  - `merge_settings`: en `permissions.allow`, `ask` y `deny`, unión que conserva el orden y no duplica; en `hooks.PreToolUse`, añade la entrada de la plantilla salvo que ya exista una cuyo hook nombre `pr_gate.py`; todo lo demás queda intacto.
  - `init` llama a `merge_settings` solo con el bloque `permissions` de la plantilla, sin `hooks`: las tres reglas `ask` existen desde el primer gate, antes de que haya arnés.
  - `doctor` imprime `error: …` y `warning: …` por stdout y termina con `doctor: ok` (añade `(N warnings)` si los hay) o `doctor: N error(s)`.
    - Errores, con su texto: `verify.sh is missing or not executable` · `<ruta> is missing` (para `verify.py` y `pr_gate.py`) · `.drydock/verify.json is missing, not JSON or has no steps` · `base_branch "<b>" does not resolve to a local or origin branch` · `no PreToolUse hook runs .drydock/bin/pr_gate.py` · `the pr_gate.py hook lacks "onFailure": "block"` · `missing permissions.ask rule <regla>` (uno por regla) · `.gitignore does not list .drydock/local/` · `.drydock/local is tracked by git`.
    - Avisos: `warning: <VAR> is set and overrides routing.json` para `CLAUDE_CODE_EFFORT_LEVEL` y `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` · `warning: <ruta> differs from the skill template (run harness install --force)` para cada script propio distinto de su plantilla.

- [ ] **Paso 6: correr y ver pasar**

Correr: `python3 -m unittest discover -s tests -v`
Esperado: `Ran 64 tests … OK`

- [ ] **Paso 7: commit** `git add -A && git commit -m "feat(T5): harness install and doctor"`

**Cierre de H1: el repo se instala su propio arnés.**

- [ ] Escribir a mano `.drydock/verify.json` del propio repo:

```json
{
  "base_branch": "main",
  "src_globs": ["bin/*", "templates/*.py"],
  "test_globs": ["tests/*"],
  "red": "python3 -m unittest discover -s tests",
  "steps": [{"name": "unit", "mode": "fast", "run": "python3 -m unittest discover -s tests"}]
}
```

- [ ] Escribir a mano `.github/workflows/verify.yml`: como la plantilla, pero con `actions/setup-python` y matriz `python: ["3.9", "3.x"]` en lugar de `setup-dotnet`. Si 3.9 ya no está disponible en los runners, la matriz empieza en la más baja disponible y B1 se corrige a esa versión.
- [ ] `python3 bin/drydock.py harness install --stack dotnet` (conserva los dos archivos anteriores, copia los scripts, fusiona settings), `python3 bin/drydock.py doctor`, `./verify.sh`, commit `chore: install own harness`.
- [ ] Regla desde aquí: tras cambiar `templates/verify.py`, `templates/pr_gate.py` o `templates/verify.sh`, correr `harness install --stack dotnet --force` en este repo. El hook vivo es la copia instalada, no la plantilla en edición.
- [ ] Regla desde aquí, con el remoto ya creado (aceptación de H1): cada tarea, de T6A en adelante, se hace en una rama `task/T<n>` creada desde `main` y entra por PR: `./verify.sh` completo, `git push -u origin task/T<n>`, `gh pr create`, y John integra. En `main`, `red-first` no evalúa nada (`base..HEAD` está vacío), así que sin rama el arnés propio no exigiría el ciclo.

**Aceptación de H1** (a mano; pide confirmación a John antes de crear el remoto de drydock y el repo de juguete: cuenta y visibilidad):

1. En un repo de juguete con el arnés instalado, `git status` desde Claude Code no se bloquea (el `{}` con salida 0 es válido bajo `onFailure: "block"`).
2. Pedir un PR sin haber corrido verify: la llamada se niega con nuestro motivo, Claude corre `./verify.sh` y entonces el PR se crea.
3. Romper `pr_gate.py` a propósito: `gh pr create` queda bloqueado. Restaurarlo.
4. En `default` y `acceptEdits`, `drydock.py gate pass …` y `gh pr merge` piden aprobación; en `dontAsk` se niegan sin prompt, y el skill se detiene y le pide a John que los corra. El resto de `drydock.py` y `./verify.sh` no piden nada en ningún modo.
5. `git push origin main` pide aprobación (decisión `ask` del hook).
6. Un subagente que intenta `gh pr create` recibe la misma negación.
7. El workflow corre `./verify.sh` en el PR. Poner el check `verify` como requerido en la rama base. Si la cuenta no lo admite en un repo privado, John decide antes de H2: repo público, cambio de plan de GitHub o CI solo consultivo; la decisión se anota en A5.
8. Repetir el paso 2 dentro de `claude --worktree` y anotar a qué ruta apunta `${CLAUDE_PROJECT_DIR}`.
9. Con los plugins habituales de John activos, `./verify.sh` y `gh` no son interceptados ni redirigidos por otro hook. Además, despachar un subagente cualquiera y leer su transcripción: qué contexto ajeno le inyecta `SubagentStart` y si algún hook le bloquea `Grep` o `Glob`. Si algo interfiere: desactivar ese plugin en el repo con `enabledPlugins` y anotarlo. Las líneas base y los escenarios de H2 corren con esta misma configuración de plugins.

Si tras `harness install` el hook no dispara, se abre una sesión nueva antes de dar un paso por fallido (el Paso 0 de H1 dice si hace falta). Resultados al `LEARNINGS.md` del repo. Un fallo en 1, 3, 4 o 5 detiene H2 hasta corregir el diseño; el 7 lo detiene hasta que John decida.

#### H2 — Bloques y ruteo

**Paso 0 de H2: líneas base (antes de T6A).** En el repo de juguete de H1, sin el skill, correr el encargo de los escenarios 06 (agrupar ocho tareas en bloques) y 07 (construir un bloque hasta el PR) y anotar en `scenarios/06-blocks.md` y `scenarios/07-build.md` qué pasos se salta el modelo. T6A–T8 suponen fallos concretos: tareas sin asignar, nivel rebajado, PR sin verify, revisión omitida, commit después del `approve`. Si la línea base no muestra alguno, se anota y se le pregunta a John antes de construir esa pieza.

### Tarea 6A: validación del plan de bloques

**Archivos:**
- Crear: `tests/test_blocks.py`, `tests/fixtures/tasks-a.md`, `tests/fixtures/tasks-b.md`
- Modificar: `bin/drydock.py` (`blocks validate`), `tests/helpers.py`

**Interfaces:**
- Consume: `routing.json` (T1), `GATE_CHECKS` (T5).
- Produce:

```python
TIERS = ("T1", "T2", "T3")
DIMENSIONS = ("novelty", "scope", "risk", "testing", "ambiguity")
TASK_RE = re.compile(r"^\s*-\s\[(?P<done>[ xX])\]\s+(?P<id>T\d{3,})\b(?P<text>.*)$")
CHECKBOX_RE = re.compile(r"^\s*-\s\[[ xX]\]\s")
UNSUPPORTED_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)?\s*(?:\[[ xX]\]\s*)?\**T\d{3,}\b")   # un id de tarea fuera del formato de Spec Kit
def parse_tasks(path: Path) -> tuple       # ({id: descripción}, errores); es error una línea que no casa TASK_RE y sí CHECKBOX_RE o UNSUPPORTED_RE
def computed_tier(score: dict) -> str      # suma 0–3 → T1, 4–6 → T2, 7–10 → T3; risk == 2 da T2 como mínimo
def load_blocks(root: Path) -> dict        # CliError(1, "no block plan: .drydock/blocks.json")
def validate_blocks(root: Path) -> list    # mensajes de B3; nunca lanza: un CliError, OSError o ValueError de la carga vuelve como lista de un elemento
def specs_gate_errors(root: Path) -> list  # "no slice set: run drydock.py slice set <id>" · "tasks file not found: specs/<slice>/tasks.md"
GATE_CHECKS["blocks"] = validate_blocks
GATE_CHECKS["specs"] = specs_gate_errors
```

- [ ] **Paso 1: escribir los fixtures**

`tests/fixtures/tasks-a.md`:

```text
# Tasks: walking skeleton

## Phase 1: Setup

- [ ] T001 Create solution structure
- [ ] T002 [P] Add health endpoint in src/Api/Health.cs
- [ ] T003 [P] [US1] Create User model in src/Domain/User.cs

## Phase 2: Core

- [ ] T004 [US1] Persist users
- [ ] T005 [US1] Money transfer endpoint
```

`tests/fixtures/tasks-b.md` (variantes que Spec Kit admite, y una línea que no es tarea):

```text
- [X] T001 Done task
  - [x] T002 [P] Nested and done
- [ ] T1000 Four-digit id
Prose that mentions T004 is not a task either
```

- [ ] **Paso 2: añadir a `tests/helpers.py`** (nivel de módulo)

```python
LOW = {"novelty": 0, "scope": 0, "risk": 0, "testing": 0, "ambiguity": 0}

def task(task_id, **score):
    return {"id": task_id, "score": {**LOW, **score}}

def block(block_id, tasks, tier="T1", **extra):
    return {"id": block_id, "title": f"Block {block_id}", "tier": tier, "tier_override": None, "depends_on": [],
            "status": "pending", "tasks": [task(t) if isinstance(t, str) else t for t in tasks], **extra}

def plan(*blocks):
    return {"version": 1, "slice": "001-skeleton", "tasks_file": "specs/001-skeleton/tasks.md", "blocks": list(blocks)}

def valid_plan():                                    # cubre tasks-a.md
    return plan(block("B01", ["T001", "T002", "T003"]),
                block("B02", ["T004"], depends_on=["B01"]),
                block("B03", [task("T005", risk=2, novelty=1)], tier="T2", depends_on=["B02"]))

class BlocksCase(RepoCase):
    def setUp(self):
        super().setUp()
        self.set_phase("blocks", slice="001-skeleton")
        self.commit("chore: init drydock")         # lo que deja init (settings, routing) ya está en la base, como en un producto real
        self.write("specs/001-skeleton/tasks.md", (FIXTURES / "tasks-a.md").read_text())

    def validate(self, plan_obj):
        self.write_json(".drydock/blocks.json", plan_obj)
        return self.cli("blocks", "validate")

    def block_of(self, block_id):
        return next(b for b in self.read_json(".drydock/blocks.json")["blocks"] if b["id"] == block_id)
```

- [ ] **Paso 3: escribir los tests que fallan** en `tests/test_blocks.py`

```python
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
```

- [ ] **Paso 4: correrlos y verlos fallar**

Correr: `python3 -m unittest discover -s tests -p "test_blocks.py" -v`
Esperado: 16 fallos (argparse no conoce `blocks`; `gate pass specs` aún no comprueba nada).

- [ ] **Paso 5: commit** `git add tests && git commit -m "test(T6A): block plan validation"`

- [ ] **Paso 6: implementar `blocks validate`** con las firmas de Interfaces y la tabla de mensajes de B3. `validate_blocks` acumula todos los errores, los devuelve ordenados por bloque y no corta en el primero; con un `tier` desconocido se saltan para ese bloque las reglas que dependen del nivel. El ciclo se informa con un camino completo. Antes de las reglas por bloque comprueba que `slice` y `tasks_file` son los de la rebanada de `state.json`, y que `tasks_file` existe y tiene al menos una tarea; si falla una de esas, devuelve solo ese error.

- [ ] **Paso 7: correr y ver pasar**

Correr: `python3 -m unittest discover -s tests -p "test_blocks.py" -v`
Esperado: `Ran 16 tests … OK`

- [ ] **Paso 8: commit** `git add bin && git commit -m "feat(T6A): block plan validation"`

### Tarea 6B: ciclo de vida del bloque

**Archivos:**
- Crear: `tests/test_block_lifecycle.py`
- Modificar: `bin/drydock.py` (`block start`, `block close`, `status`, `next_action`, `render_state`), `tests/test_state.py`

**Interfaces:**
- Consume: `load_blocks`, `validate_blocks` (T6A); evidencia y veredictos (T3, T4).
- Produce:

```python
def base_branch(root: Path) -> str                                   # base_branch de verify.json; "main" si no hay
def find_block(plan: dict, block_id: str) -> dict                    # CliError(1, "unknown block <id>")
def evidence(root: Path, sha: str, mode: str) -> Optional[dict]      # None si no existe
def review_verdict(root: Path, block_id: str, sha: str) -> Optional[str]   # "approve" | "changes" | None
def block_step(root: Path, block_id: str) -> str
def close_block(root: Path, block_id: str, merged_sha: str, attempts: int, findings: int) -> None
GATE_CHECKS["build"] = build_gate_errors                             # falta blocks.json, es de otra rebanada, hay bloque en curso o alguno no está done
SWEEP_PATHS = (".drydock/", "PROJECT_STATE.md", ".gitignore", "specs/", "docs/", ".specify/", ".claude/skills/")   # lo único que block start barre
```

- [ ] **Paso 1: escribir los tests que fallan** en `tests/test_block_lifecycle.py`

```python
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
```

- [ ] **Paso 2: actualizar `tests/test_state.py::test_build_requires_next`**: antes de cada `gate pass build`, escribir `.drydock/blocks.json` con `{"version": 1, "slice": "<s>", "tasks_file": "specs/<s>/tasks.md", "blocks": []}`, donde `<s>` es la rebanada pasada a `set_phase` (`001-skeleton` y después `002-users`): el gate `build` exigirá un plan de la rebanada en curso.

- [ ] **Paso 3: correrlos y verlos fallar**

Correr: `python3 -m unittest discover -s tests -p "test_block_lifecycle.py" -v`
Esperado: 8 fallos (argparse no conoce `block`).

- [ ] **Paso 4: commit** `git add tests && git commit -m "test(T6B): block lifecycle"`

- [ ] **Paso 5: implementar**

  - `block start <id>`, en este orden: fase `build` · `current_block` nulo · `validate_blocks(root)` sin errores · el bloque existe y está `pending` · todas sus dependencias `done` · la rama actual es `base_branch(root)` · toda ruta pendiente de `git -c core.quotePath=false status --porcelain --untracked-files=all` cae bajo `SWEEP_PATHS`; si no, sale 1 con `unexpected pending changes: <rutas>` sin tocar nada. Después: `git switch -c block/<id>`; si existe `refs/remotes/origin/<base>` y `<base>` tiene commits que no están ahí, `git branch -f <base> origin/<base>` e imprime `moved <base> back to origin/<base>; its local commits travel in block/<id>`; estado a `in_progress` y `current_block = <id>`, `save_state`, `git add -A`, `git commit -m "chore(drydock): start <id>"`. Imprime `started <id> on branch block/<id>` y las rutas incluidas en el commit.
  - `block close <id>`: exige `current_block == <id>`. Sin `--merged-sha` lo pide a `gh` (T6C). Si existe el remoto `origin`, `git fetch origin <base>` y la referencia a comprobar es `origin/<base>`; si no, `<base>`. Comprueba **antes de cambiar de rama** `git merge-base --is-ancestor <sha> <ref>`; si falla sale 1 con `<sha7> is not on <base>` y no toca nada. Después llama a `close_block`.
  - `close_block`: `git switch <base>`; con `origin`, `git pull --ff-only origin <base>`; relee estado y plan; bloque a `done`; `current_block = None`; añade a `.drydock/metrics.jsonl` una línea `{"block", "tier", "attempts", "findings", "merged_sha", "closed_at"}`; `save_state`. Por defecto `attempts = 1` y `findings = 0`.
  - `build_gate_errors`, en este orden y con estos textos: `no block plan: .drydock/blocks.json` · `blocks.json is for slice "<a>", current slice is "<b>"` · `block <id> is still in progress` (hay `current_block`) · `block <id> is <status>` por cada bloque que no está `done`. No corre `validate_blocks`: eso ya lo hizo cada `block start`.
  - `block_step`, con `head = HEAD`:

```python
    passed = any((evidence(root, head, mode) or {}).get("result") == "pass" for mode in ("fast", "full"))
    verdict = review_verdict(root, block_id, head)
    full = evidence(root, head, "full") or {}
    if not passed:
        return "implement the next task (test commit, then feat commit) and run ./verify.sh --fast"
    if verdict is None:
        return f"dispatch the reviewer, then drydock.py review record {block_id} --sha {head[:12]}"
    if verdict == "changes":
        return "fix the review findings and run ./verify.sh --fast"
    if not (full.get("result") == "pass" and full.get("dirty") is False):
        return "run ./verify.sh (full) on the approved commit"
    return (f"open the PR: drydock.py block pr-body {block_id} | gh pr create --title ... --body-file - ; "
            f"then T1: drydock.py block merge {block_id}; T2/T3: the user approves "
            f"gh pr merge block/{block_id} --squash --delete-branch --match-head-commit {head}, then drydock.py block close {block_id}")
```

  - `next_action` en fase `build`: con bloque en curso, `Continue block <id> on branch block/<id>: <block_step>` si `live`, o `Continue block <id> on branch block/<id> (run drydock.py status for the exact step)` si no. Sin bloque en curso: `Start the next pending block: drydock.py block start <primer pendiente con dependencias cerradas>`. Con todos cerrados: `All blocks are done: drydock.py gate pass build --next specs|review`.
  - `render_state` añade la línea `- Blocks: <hechos>/<total> done` cuando existe `blocks.json`.

- [ ] **Paso 6: correr y ver pasar**

Correr: `python3 -m unittest discover -s tests -v`
Esperado: `Ran 88 tests … OK`

- [ ] **Paso 7: commit** `git add -A && git commit -m "feat(T6B): block lifecycle"`

### Tarea 6C: auto-merge de T1

**Archivos:**
- Crear: `tests/test_block_merge.py`, `tests/fake_gh.py`, `tests/fixtures/gh/` (salidas reales de `gh`, Paso 0)
- Modificar: `bin/drydock.py` (`block merge`, `block close` sin `--merged-sha`), `tests/helpers.py`

**Interfaces:**
- Consume: `close_block`, `evidence`, `review_verdict` (T6B).
- Produce:

```python
def gh(root: Path, *args: str) -> subprocess.CompletedProcess    # nunca lanza por el código de salida; CliError(1, "gh not found") si no está
def checks_error(root: Path, number: int) -> Optional[str]             # None si el check verify está en verde; si no, el mensaje. Una sola consulta, sin esperar
HARNESS_PATHS = (".drydock/verify.json", ".drydock/deploy.json", ".drydock/routing.json", ".drydock/bin/", "verify.sh",
                 ".claude/settings.json", ".claude/agents/", ".github/workflows/",
                 "AGENTS.md", "CLAUDE.md", ".claude/skills/", ".specify/")   # un bloque que las toca no se auto-integra
```

Las únicas cuatro llamadas a `gh` de la CLI:

| Llamada | Uso |
|---|---|
| `gh pr view block/<id> --json number,state,headRefOid,baseRefName` | Antes del merge: PR abierto, apuntando a `HEAD` y con la base como destino |
| `gh pr checks <n> --json name,bucket,workflow` | Una consulta: hay un check del workflow `verify` en `pass` y los demás están en `pass` o `skipping` |
| `gh pr merge <n> --squash --delete-branch --match-head-commit <sha>` | El merge |
| `gh pr view <n o block/<id>> --json state,mergeCommit` | Después del merge, y en `block close` sin `--merged-sha` |

- [ ] **Paso 0: capturar las salidas reales de `gh`.** En el repo de juguete de H1, con un PR abierto, guardar en `tests/fixtures/gh/` el stdout, el stderr y el código de salida de las cuatro llamadas de la tabla (los checks, en tres momentos: recién creado el PR, con CI corriendo y con CI en verde), y anotar qué hace `--delete-branch` con la rama local. `fake_gh.py` copia esas formas; si difieren de lo que sigue, se corrigen aquí el fake y los pasos 3 y 6 antes de escribir los tests.

- [ ] **Paso 1: escribir `tests/fake_gh.py`** (script ejecutable con `#!/usr/bin/env python3`; lee su estado de `$FAKE_GH_DIR`)

| Argumentos | Efecto |
|---|---|
| Cualquiera | Añade los argumentos, unidos por espacios, a `calls.log` |
| `pr view …` | Imprime `pr.json` y sale 0 |
| `pr checks …` | Según el archivo `checks`, imprime una lista JSON: `pass` → `[{"name": "verify", "bucket": "pass", "workflow": "verify"}]`, sale 0 · `fail` → el mismo check con `bucket` `fail`, sale 1 · `pending` → con `bucket` `pending`, sale 8 · `other` → un check `lint` del workflow `lint` en `pass`, sale 0 · `skipped` → el check `verify` en `pass` más un `lint` en `skipping`, sale 0 · `none` → nada por stdout, `no checks reported on the 'block/B01' branch` en stderr, sale 1 |
| `pr merge <n> --squash --delete-branch --match-head-commit <sha>` | Si `<sha>` no es `headRefOid`, sale 1. Si lo es, en el repo actual: `git switch -q main`, `git merge -q --squash <headRefName>`, `git commit -q -m "<headRefName> (#<n>)"`, `git branch -q -D <headRefName>`; reescribe `pr.json` con `state: "MERGED"` y `mergeCommit.oid` = `HEAD` de main |

- [ ] **Paso 2: añadir a `tests/helpers.py`**

```python
class FakeGh:
    def __init__(self, case, pr, checks="pass"):
        self.dir = case.tmp / "gh"
        self.dir.mkdir()
        (case.tmp / "bin").mkdir()
        shutil.copy(ROOT / "tests" / "fake_gh.py", case.tmp / "bin" / "gh")
        os.chmod(case.tmp / "bin" / "gh", 0o755)
        self.env = {"PATH": f"{case.tmp / 'bin'}{os.pathsep}{os.environ['PATH']}", "FAKE_GH_DIR": str(self.dir)}
        self.set(pr=pr, checks=checks)

    def set(self, pr=None, checks=None):
        if pr is not None:
            (self.dir / "pr.json").write_text(json.dumps(pr))
        if checks is not None:
            (self.dir / "checks").write_text(checks)

    def calls(self):
        log = self.dir / "calls.log"
        return log.read_text().splitlines() if log.exists() else []
```

- [ ] **Paso 3: escribir los tests que fallan** en `tests/test_block_merge.py`

```python
class BlockMergeTests(BlocksCase):
    def setUp(self):
        super().setUp()
        self.write_json(".drydock/blocks.json", valid_plan())
        self.set_phase("build", slice="001-skeleton")
        self.cli("block", "start", "B01")
        self.commit("feat(B01/T001): x", {"src/x.txt": "x\n"})
        self.write_evidence()
        self.write_review("B01")
        self.gh = FakeGh(self, self.open_pr())

    def open_pr(self, **changes):
        return {"number": 7, "state": "OPEN", "headRefOid": self.head(), "headRefName": "block/B01", "baseRefName": "main", **changes}

    def merge(self, *extra):
        return self.cli("block", "merge", "B01", *extra, env=self.gh.env)

    def refused(self, needle):
        r = self.merge()
        self.assertEqual(r.returncode, 1)
        self.assertIn(needle, r.stderr)
        self.assertFalse(any(c.startswith("pr merge") for c in self.gh.calls()))
        self.assertEqual(self.block_of("B01")["status"], "in_progress")

    def test_t1_happy_path(self):
        head = self.head()
        r = self.merge("--attempts", "1", "--findings", "0")
        self.assertEqual(r.returncode, 0, r.stderr)
        calls = self.gh.calls()
        self.assertEqual([c.split()[:2] for c in calls], [["pr", "view"], ["pr", "checks"], ["pr", "merge"], ["pr", "view"]])
        self.assertIn(f"--squash --delete-branch --match-head-commit {head}", calls[2])
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), "main")
        self.assertEqual((self.block_of("B01")["status"], self.state()["current_block"]), ("done", None))
        line = json.loads((self.repo / ".drydock/metrics.jsonl").read_text().splitlines()[-1])
        self.assertEqual(line["merged_sha"], self.head())

    def test_refuses_non_t1(self):
        p = self.read_json(".drydock/blocks.json")
        p["blocks"][0].update(tier="T2", tier_override="escalated")
        self.write_json(".drydock/blocks.json", p)
        self.commit("chore: raise tier")
        self.write_evidence()
        self.write_review("B01")
        self.refused("only T1 blocks merge automatically")

    def test_refuses_tdd_exemptions(self):
        self.write_evidence(tdd_exempt=[{"sha": self.head(), "reason": "scaffolding"}])
        self.refused("TDD exemptions")

    def test_refuses_without_evidence_or_review(self):
        shutil.rmtree(self.repo / ".drydock/local/reviews")
        self.refused("approving review")
        self.write_review("B01")
        shutil.rmtree(self.repo / ".drydock/local/evidence")
        self.refused("verify evidence")

    def test_refuses_when_pr_head_differs(self):
        self.gh.set(pr=self.open_pr(headRefOid="0" * 40))
        self.refused("PR head")
        self.gh.set(pr=self.open_pr(baseRefName="other"))
        self.refused("PR targets other")

    def test_refuses_until_verify_check_is_green(self):
        for checks in ("none", "pending", "other"):
            self.gh.set(checks=checks)
            self.refused("checks not green yet")
        self.gh.set(checks="skipped")
        self.assertEqual(self.merge().returncode, 0)                  # un job omitido no bloquea

    def test_refuses_harness_changes(self):
        self.commit("docs: relax agent rules", {"AGENTS.md": "x\n"})
        self.write_evidence()
        self.write_review("B01")
        self.refused("block changes the harness (AGENTS.md)")
        self.commit("chore: loosen verify", {".drydock/verify.json": "{}\n", ".specify/feature.json": "{}\n"})
        self.write_evidence()
        self.write_review("B01")
        self.refused("block changes the harness (.drydock/verify.json, AGENTS.md)")      # feature.json no cuenta

    def test_block_close_rejects_merged_sha_when_origin_exists(self):
        self.git("remote", "add", "origin", str(self.tmp / "nowhere.git"))
        r = self.cli("block", "close", "B01", "--merged-sha", self.git("rev-parse", "main"), env=self.gh.env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("--merged-sha", r.stderr)
        self.assertEqual(self.block_of("B01")["status"], "in_progress")

    def test_stops_when_checks_fail(self):
        self.gh.set(checks="fail")
        self.refused("checks failed")

    def test_block_close_reads_merge_from_gh(self):
        self.assertEqual(self.cli("block", "close", "B01", env=self.gh.env).returncode, 1)   # el PR sigue abierto
        self.git("switch", "-q", "main")
        self.git("merge", "-q", "--squash", "block/B01")
        sha = self.commit("block/B01 (#7)")
        self.gh.set(pr=self.open_pr(state="MERGED", mergeCommit={"oid": sha}))
        r = self.cli("block", "close", "B01", env=self.gh.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.block_of("B01")["status"], "done")
```

- [ ] **Paso 4: correrlos y verlos fallar**

Correr: `python3 -m unittest discover -s tests -p "test_block_merge.py" -v`
Esperado: 10 fallos (argparse no conoce `block merge`; `block close` exige `--merged-sha` y aún lo acepta con `origin`).

- [ ] **Paso 5: commit** `git add tests && git commit -m "test(T6C): T1 auto-merge"`

- [ ] **Paso 6: implementar `block merge <id>`**. Comprobaciones en este orden, cada una con su mensaje; ninguna llama a `gh pr merge` si falla:

  1. `current_block == <id>` y la rama actual es `block/<id>`.
  2. `tier == "T1"` → `only T1 blocks merge automatically`.
  3. Evidencia completa válida para `HEAD` → `no valid full verify evidence for <sha7>`.
  4. `tdd_exempt` vacío → `block has TDD exemptions; the user merges this one`.
  5. `git -c core.quotePath=false diff --name-only <base>...HEAD` no toca ninguna ruta de `HARNESS_PATHS`, salvo `.specify/feature.json`, que cambia en cada rebanada → `block changes the harness (<rutas separadas por coma, en el orden de git>); the user merges this one`. Coste aceptado: el primer bloque tras `specify init` lo integra John.
  6. Veredicto `approve` para `HEAD` → `no approving review for <sha7>`.
  7. `gh pr view`: `state == "OPEN"` y `headRefOid == HEAD` → `PR head <a7> is not local HEAD <b7> (push first)`; `baseRefName` es la base → `PR targets <rama>, not <base>`.
  8. `checks_error`: una sola consulta, y el código de salida de `gh` no se usa. Algún `bucket` en `fail` o `cancel` → `checks failed; not merging`. Si falta un check con `workflow == "verify"` en `pass`, o alguno no está en `pass` ni en `skipping` (también si no hay JSON) → `checks not green yet; run block merge again`. Un job omitido no bloquea: si contara, `block merge` no terminaría nunca.
  9. `gh pr merge`; si sale distinto de 0, sale 1 con su stderr.
  10. `gh pr view --json state,mergeCommit`: exige `MERGED`; `close_block` con `mergeCommit.oid`.

  `block close` sin `--merged-sha` usa la llamada 10 con `block/<id>`; si el estado no es `MERGED` sale 1 con `PR for block/<id> is not merged`. Con remoto `origin`, `--merged-sha` se rechaza: `--merged-sha is only for repositories without an origin remote`.

- [ ] **Paso 7: correr y ver pasar**

Correr: `python3 -m unittest discover -s tests -v`
Esperado: `Ran 98 tests … OK`

- [ ] **Paso 8: commit** `git add -A && git commit -m "feat(T6C): T1 auto-merge"`

### Tarea 7: generación de agentes

**Archivos:**
- Crear: `templates/agents/impl.md.tmpl`, `reviewer.md.tmpl`, `auditor.md.tmpl`, `final-reviewer.md.tmpl`, `tests/test_agents.py`
- Modificar: `bin/drydock.py` (`agents render`, `doctor_report`), `tests/test_harness.py`

**Interfaces:**
- Consume: `routing.json` (T1), `doctor_report` (T5).
- Produce:

```python
ROLE_TEMPLATES = {"reviewer": "reviewer", "reviewer-t3": "reviewer", "auditor": "auditor", "final-reviewer": "final-reviewer"}
def render_agents(root: Path) -> dict    # {ruta relativa: contenido}; CliError(1, …) si a routing.json le falta model o effort, o trae un rol desconocido
```

`doctor_report`, solo cuando existe `.drydock/routing.json`: error si falta un agente o su contenido difiere de `render_agents` (el mensaje nombra el archivo).

- [ ] **Paso 1: escribir los tests que fallan** en `tests/test_agents.py`

```python
NAMES = ["drydock-auditor.md", "drydock-final-reviewer.md", "drydock-impl-t1.md", "drydock-impl-t2.md",
         "drydock-impl-t3.md", "drydock-reviewer-t3.md", "drydock-reviewer.md"]
READ_ONLY = "Write, Edit, NotebookEdit, Agent"

class AgentsTests(RepoCase):
    def setUp(self):
        super().setUp()
        self.cli("init")

    def front(self, name):                               # frontmatter como dict
        lines = (self.repo / ".claude/agents" / name).read_text().split("---")[1].strip().splitlines()
        return dict(line.split(": ", 1) for line in lines)

    def test_all_roles_rendered(self):
        self.assertEqual(self.cli("agents", "render").returncode, 0)
        self.assertEqual(sorted(p.name for p in (self.repo / ".claude/agents").iterdir()), NAMES)

    def test_render_uses_routing(self):
        routing = self.read_json(".drydock/routing.json")
        self.cli("agents", "render")
        fm = self.front("drydock-impl-t3.md")
        self.assertEqual((fm["name"], fm["model"], fm["effort"]),
                         ("drydock-impl-t3", routing["tiers"]["T3"]["model"], routing["tiers"]["T3"]["effort"]))
        self.assertEqual(self.front("drydock-reviewer-t3.md")["effort"], routing["roles"]["reviewer-t3"]["effort"])
        routing["tiers"]["T3"]["model"] = "other-model"
        self.write_json(".drydock/routing.json", routing)
        self.cli("agents", "render")
        self.assertEqual(self.front("drydock-impl-t3.md")["model"], "other-model")

    def test_render_idempotent(self):
        self.assertEqual(self.cli("agents", "render").returncode, 0)     # sin esto pasa en vacío antes de implementar
        before = self.snapshot()
        self.cli("agents", "render")
        self.assertEqual(self.snapshot(), before)

    def test_tool_restrictions(self):
        self.cli("agents", "render")
        for tier in ("t1", "t2", "t3"):
            self.assertEqual(self.front(f"drydock-impl-{tier}.md")["disallowedTools"], "Agent")
        for role in ("reviewer", "reviewer-t3", "auditor", "final-reviewer"):
            self.assertEqual(self.front(f"drydock-{role}.md")["disallowedTools"], READ_ONLY)

    def test_doctor_detects_drift(self):
        self.cli("harness", "install", "--stack", "dotnet")
        self.assertEqual(self.cli("doctor").returncode, 1)                       # faltan los agentes
        self.cli("agents", "render")
        self.assertEqual(self.cli("doctor").returncode, 0)
        path = self.repo / ".claude/agents/drydock-impl-t1.md"
        path.write_text(path.read_text() + "\nextra\n")
        r = self.cli("doctor")
        self.assertEqual(r.returncode, 1)
        self.assertIn("drydock-impl-t1.md", r.stdout)

    def test_bad_routing_fails(self):
        routing = self.read_json(".drydock/routing.json")
        del routing["roles"]["auditor"]["model"]
        self.write_json(".drydock/routing.json", routing)
        self.assertEqual(self.cli("agents", "render").returncode, 1)
```

- [ ] **Paso 2: actualizar `tests/test_harness.py::test_gate_pass_prepare_runs_doctor`**: añadir `self.cli("agents", "render")` después de `self.install()` (desde ahora `doctor` exige los agentes cuando hay `routing.json`).

- [ ] **Paso 3: correrlos y verlos fallar**

Correr: `python3 -m unittest discover -s tests -p "test_agents.py" -v`
Esperado: 6 fallos (argparse no conoce `agents`).

- [ ] **Paso 4: commit** `git add tests && git commit -m "test(T7): agent rendering"`

- [ ] **Paso 5: escribir las plantillas e implementar `agents render`**

Sustitución simple de `{{name}}`, `{{model}}`, `{{effort}}`, `{{tier}}` y `{{max_tasks}}`. Frontmatter exacto de `impl.md.tmpl` (las otras tres cambian `description` y llevan `disallowedTools: Write, Edit, NotebookEdit, Agent`):

```markdown
---
name: {{name}}
description: Drydock implementer for {{tier}} blocks. Use only when the drydock build phase dispatches it.
model: {{model}}
effort: {{effort}}
disallowedTools: Agent
---
```

Reglas que debe llevar el cuerpo (prosa en inglés, redactada con `superpowers:writing-skills`):

  - `impl`: trabaja en la rama `block/<id>` actual, hasta `{{max_tasks}}` tareas. Por tarea: test que falla, verlo fallar, commit `test(<block>/<task>): …`; implementación mínima, verlo pasar, commit `feat(<block>/<task>): …`. Los arreglos posteriores de una tarea llevan su mismo ámbito, `fix(<block>/<task>): …`, y no necesitan test nuevo. Un commit de código sin test en rojo en su tarea necesita `TDD-Exempt: <reason>`, solo para andamiaje, refactor puro o código generado. Nunca abre un PR, nunca hace push a la base, nunca edita `.drydock/`. Termina con `./verify.sh --fast` en verde y un informe: tareas, commits, exenciones, pendientes.
  - `reviewer`: la primera línea de la respuesta es `verdict: approve` o `verdict: changes`. Revisa `git diff <base>...HEAD` contra los criterios de aceptación y la constitution recibidos; no se fía de resúmenes. Cada hallazgo: `archivo:línea`, por qué importa, qué cambiar. Bloquea solo por corrección, seguridad, reglas de capas, tests ausentes o desajuste con la spec.
  - `auditor`: la rúbrica de la fase 3 (v0, A3); cada versión se comprueba en su fuente oficial; cada hallazgo es blocker, major o minor con evidencia y cambio propuesto.
  - `final-reviewer`: los seis puntos de la revisión final (v0, A3).

Nombres de archivo: `drydock-impl-<tier en minúsculas>.md` por cada nivel y `drydock-<rol>.md` por cada rol.

- [ ] **Paso 6: correr y ver pasar**

Correr: `python3 -m unittest discover -s tests -v`
Esperado: `Ran 104 tests … OK`

- [ ] **Paso 7: commit** `git add -A && git commit -m "feat(T7): agent rendering"`

### Tarea 8: revisión registrada, cuerpo del PR y fases `blocks` y `build`

**Archivos:**
- Crear: `tests/test_review.py`, `scenarios/06-blocks.md`, `scenarios/07-build.md`
- Modificar: `bin/drydock.py` (`review record`, `block pr-body`), `phases/6-blocks.md`, `phases/7-build.md`, `adapters/claude.md`

**Interfaces:**
- Consume: T6A–T6C, T7.
- Produce:

```python
def pr_body(root: Path, block_id: str) -> str    # CliError(1, …) sin evidencia completa válida o sin veredicto approve para HEAD
```

- [ ] **Paso 1: escribir los tests que fallan** en `tests/test_review.py`

```python
class ReviewTests(BlocksCase):
    def setUp(self):
        super().setUp()
        self.write_json(".drydock/blocks.json", valid_plan())
        self.set_phase("build", slice="001-skeleton")
        self.cli("block", "start", "B01")
        self.commit("feat(B01/T001): x", {"src/x.txt": "x\n"})

    def record(self, text, sha=None, block_id="B01"):
        return self.cli("review", "record", block_id, "--sha", sha or self.head(), stdin=text)

    def test_requires_head_sha(self):
        self.write_evidence(mode="fast")
        self.assertEqual(self.record("verdict: approve\n", sha=self.git("rev-parse", "HEAD~1")).returncode, 1)

    def test_requires_passing_verify_evidence(self):
        r = self.record("verdict: approve\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("./verify.sh --fast", r.stderr)
        self.write_evidence(mode="fast", result="fail")
        self.assertEqual(self.record("verdict: approve\n").returncode, 1)

    def test_writes_review_verbatim(self):
        self.write_evidence(mode="fast")
        text = "verdict: changes\n\n- src/x.txt:1 missing validation\n"
        self.assertEqual(self.record(text).returncode, 0)
        self.assertEqual((self.repo / f".drydock/local/reviews/B01-{self.head()}.md").read_text(), text)
        self.assertEqual(self.record("verdict: approve\n", sha=self.head()[:12]).returncode, 0)      # prefijo de 7 o más

    def test_rejects_missing_verdict_line(self):
        self.write_evidence(mode="fast")
        for text in ("looks good\n", "verdict: maybe\n", ""):
            self.assertEqual(self.record(text).returncode, 1, text)

    def test_rejects_other_block(self):
        self.write_evidence(mode="fast")
        self.assertEqual(self.record("verdict: approve\n", block_id="B02").returncode, 1)

    def test_pr_body(self):
        self.write_evidence(mode="fast")
        self.assertEqual(self.cli("block", "pr-body", "B01").returncode, 1)      # falta verify completo y veredicto
        self.write_evidence(mode="full", tdd_exempt=[{"sha": self.head(), "reason": "pure rename"}])
        self.record("verdict: approve\n\nLGTM\n")
        r = self.cli("block", "pr-body", "B01")
        self.assertEqual(r.returncode, 0, r.stderr)
        for needle in ("B01", "Tier: T1", "T001 Create solution structure", "verdict: approve", "LGTM", "pure rename", self.head()[:7]):
            self.assertIn(needle, r.stdout)
        self.assertEqual(self.cli("block", "pr-body", "B01").stdout, r.stdout)
```

- [ ] **Paso 2: correrlos y verlos fallar**

Correr: `python3 -m unittest discover -s tests -p "test_review.py" -v`
Esperado: 6 fallos (argparse no conoce `review` ni `block pr-body`).

- [ ] **Paso 3: commit** `git add tests && git commit -m "test(T8): review record and PR body"`

- [ ] **Paso 4: implementar `review record` y `block pr-body`**

  - `review record <id> --sha <sha>`: `<id>` es `current_block`; `<sha>` es `HEAD` o un prefijo suyo de 7 caracteres o más (`<sha> is not HEAD (<head7>)`); existe evidencia `fast` o `full` con `result == "pass"` para `HEAD` (`no passing verify evidence for <head7>; run ./verify.sh --fast first`); la primera línea de stdin es exactamente `verdict: approve` o `verdict: changes` (`review must start with "verdict: approve" or "verdict: changes"`). Escribe stdin tal cual en `.drydock/local/reviews/<id>-<HEAD>.md`, reemplazando el anterior.
  - `block pr-body <id>` imprime:

```markdown
## <id>: <title>

Tier: <tier> · Commit: <sha7>

### Tasks
- <T001 descripción de tasks.md>

### Review
<contenido del archivo de revisión>

### Verify
| Step | Exit | Seconds |
|---|---|---|
| <name> | <exit> | <seconds> |

### TDD exemptions
- <sha7>: <reason>
```

  Sin exenciones, la última sección dice `None`.

- [ ] **Paso 5: correr y ver pasar**

Correr: `python3 -m unittest discover -s tests -v`
Esperado: `Ran 110 tests … OK`

- [ ] **Paso 6: commit** `git add bin && git commit -m "feat(T8): review record and PR body"`

- [ ] **Paso 7: redactar `phases/6-blocks.md`, `phases/7-build.md` y `adapters/claude.md`** con `superpowers:writing-skills`, en inglés, con las seis secciones. Las reglas salen de los fallos de las líneas base (Paso 0 de H2), no de la intuición. Contenido obligatorio:

  - `6-blocks.md`: entradas (`specs/<slice>/tasks.md`, `routing.json`, constitution); tabla de puntuación de las cinco dimensiones (v0, A4, traducida); agrupar por nivel y módulo en orden de dependencia sin pasar de `max_tasks`; escribir `blocks.json` con el esquema de B3; correr `drydock.py blocks validate` hasta que salga 0; mostrar el plan como tabla (bloque, nivel, tareas, motivo) y detenerse. Errores frecuentes: los observados en la línea base; estas son hipótesis que se confirman o se borran: bajar un nivel para que quepan más tareas, inventar ids, subir de nivel sin `tier_override`.
  - `7-build.md`: los ocho pasos de A5 con sus comandos exactos; la regla de escalado; el límite de dos rondas de revisión; qué recibe el revisor y qué no; la respuesta del revisor se pasa tal cual a `review record`, y si su primera línea no es un veredicto se le vuelve a despachar, nunca se edita; T1 con `block merge`, T2 y T3 con merge de John y `block close`; al cerrar el último bloque, `gate pass build --next …` (el despliegue se añade en H5). Errores frecuentes: los observados en la línea base; estas son hipótesis que se confirman o se borran: pasar `model` o `effort` en el despacho, confirmar algo después del `approve`, abrir el PR sin `block pr-body`, hacer push a la base, usar `TDD-Exempt` para evitar un test.
  - `adapters/claude.md`: despacho con la herramienta Agent y `subagent_type` `drydock-impl-<tier>`, `drydock-reviewer` o `drydock-reviewer-t3` (bloques T3); nunca `model` ni `effort`; el implementador recibe id del bloque, tareas con su texto y rutas de spec, plan y constitution; el revisor recibe id, criterios de aceptación, ruta de la constitution y `git diff <base>...HEAD`; el modelo y esfuerzo aplicados se miran en `/tasks`.

- [ ] **Paso 8: escribir y correr los escenarios** con `claude -p "/drydock" --permission-mode acceptEdits` y, preaprobados con `--allowedTools`, `Bash(git:*)`, `Bash(gh pr create:*)` y los comandos del stack. Un `ask` sin nadie que responda es terminal y el escenario acaba ahí, que es lo esperado en los gates humanos (se confirma en el Paso 0 de H1).

  - `scenarios/06-blocks.md`: con un `tasks.md` de 8 tareas mixtas, propone bloques que pasan `blocks validate` y se detiene a pedir aprobación.
  - `scenarios/07-build.md`: bloque T1 de juguete: despacha `drydock-impl-t1` sin `model` ni `effort`, corre verify rápido, despacha al revisor, registra el veredicto, corre verify completo, crea el PR con `block pr-body` y lo integra con `block merge`. Un bloque T2 se detiene antes del merge.

- [ ] **Paso 9: correr la suite y commit**

Correr: `python3 -m unittest discover -s tests -v` → `Ran 110 tests … OK` (los presupuestos de líneas siguen en verde).
`git add -A && git commit -m "feat(T8): blocks and build phases"`

**Aceptación de H2** (repo de juguete en GitHub, 6 a 8 tareas):

1. Un bloque T1 llega a PR por todos los pasos y `block merge` lo integra cuando CI termina en verde. Mientras CI corre, o si `gh` aún no informa de checks, `block merge` sale 1 con `checks not green yet` y se repite.
2. Un bloque T2 se detiene antes del merge; el clic de John sobre `gh pr merge` lo integra y `block close` lo cierra.
3. `/tasks` muestra para cada agente el modelo y el esfuerzo de `routing.json`.
4. Un commit añadido después del `approve` hace que `gh pr create` se niegue.
5. Un commit de implementación sin test previo hace fallar `./verify.sh --fast` en `red-first`.
6. Cortar la sesión a mitad de bloque y abrir otra: `/drydock` retoma en el paso correcto.
7. Un commit empujado después de crear el PR hace que `gh pr merge` se niegue: falta evidencia y veredicto para el nuevo `HEAD`, o `--match-head-commit` nombra el anterior.
8. El archivo de `.drydock/local/reviews/` coincide con la respuesta del revisor. Si difiere, se activa la fila correspondiente de A9.

#### H3 — Frente del flujo (contrato; se baja a TDD al cerrar H2)

### Tarea 9: fases 1 a 3

- [ ] Archivos: `phases/1-requirements.md`, `phases/2-architecture.md`, `phases/3-audit.md`, `templates/docs/{brief,stack,audit,adr}.md`, `scenarios/01-requirements.md`, `scenarios/02-architecture.md`, `scenarios/03-audit.md`
- Contratos: tabla de A3. La fase 2 no acepta una versión sin URL oficial y fecha de consulta, y deja decididos el destino y el mecanismo de despliegue: un comando explícito, nunca un workflow que despliegue por push a la base. La fase 3 corre `drydock.py agents render` y comprueba que existe `.claude/agents/drydock-auditor.md` antes de despachar `drydock-auditor` (en v0 los agentes se generaban en la fase 4, después de usarse); si el agente no carga a mitad de sesión, sesión nueva. El orquestador escribe `audit.md` con las columnas de A3.
- Escenarios: (01) de una idea de un párrafo sale un brief con rebanadas ordenadas y la 0 desplegable; (02) cada fila de `stack.md` tiene fuente y fecha; (03) una incompatibilidad sembrada a propósito aparece como blocker.

### Tarea 10: fase `specs`

- [ ] Archivos: `phases/5-specs.md`, `scenarios/05-specs.md`
- Contrato:
  - Al empezar H3, John decide si se sube Spec Kit desde la 1.0.8 (upstream va por 1.4.x). Si se sube, se reverifican V1, `TASK_RE` y los fixtures antes de seguir.
  - `specify --version` debe responder; la versión se anota en `docs/drydock/skills.md`.
  - Solo si falta `.specify/`: `specify init --here --force --non-interactive --integration claude --script sh`. Nunca con `.specify/` presente (`--force` sobrescribe). No se instala la extensión `git` de Spec Kit: las ramas son de drydock.
  - Constitution una vez con `/speckit-constitution`, sembrada con el brief, el stack, las decisiones de la auditoría y las reglas de A5.
  - Por rebanada: `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze`. El id de la rebanada es el nombre de la carpeta `feature_directory` de `.specify/feature.json`; se fija con `drydock.py slice set <id>`.
  - El informe de analyze se guarda en `specs/<slice>/analysis.md` (Spec Kit no lo escribe).
  - Nunca `/speckit-implement` (negado en settings).
  - Si Spec Kit deja archivos fuera de `SWEEP_PATHS` (por ejemplo `CLAUDE.md`), se amplía la lista con su test; si no, `block start` se niega.
  - Gate: analyze sin CRITICAL y John aprueba la spec.

#### H4 — Preparar el repo (contrato)

### Tarea 11: fase `prepare`

- [ ] Archivos: `phases/4-prepare.md`, `templates/{AGENTS.md,CLAUDE.md,CLAUDE.local.md}.tmpl`, `templates/docs/skills.md`, `scenarios/04-prepare.md`
- Consume: `harness install`, `agents render`, `doctor`.
- Contrato: instala el arnés y ajusta `verify.json` con comandos comprobados contra las versiones fijadas en `stack.md`, y `src_globs` y `test_globs` según el layout real, probados con un commit de código sin test que debe fallar en `red-first`; añade a `.gitignore` lo propio del stack (`bin/`, `obj/`), que si no `block start` se niega; regenera los agentes; escribe `AGENTS.md` y `CLAUDE.md` (≤ 60 líneas; `CLAUDE.md` empieza con `@AGENTS.md` y limita superpowers a `test-driven-development` y `systematic-debugging`) y `CLAUDE.local.md` (añadido a `.gitignore`); aplica A7 y escribe `docs/drydock/skills.md`; escribe `.drydock/deploy.json` según `stack.md`; crea el remoto con confirmación de John, hace el primer push (el hook pregunta) y pone el check `verify` como requerido si la cuenta lo admite (decisión de la aceptación de H1). Si el hook no dispara tras instalarlo, sesión nueva. Gate automático: `doctor`.

#### H5 — Despliegue y revisión final (contrato)

### Tarea 12A: `deploy`

- [ ] Archivos: `bin/drydock.py` (`deploy`), `tests/test_deploy.py`, `phases/7-build.md`, y `tests/test_state.py` y `tests/test_block_lifecycle.py`, cuyos tests de `gate pass build` pasan a necesitar evidencia de despliegue
- Contrato: el de A5. `GATE_CHECKS["build"]` exige además evidencia de despliegue con `result == "pass"` para el `HEAD` de la base. `next_action` con todos los bloques cerrados pasa a `All blocks are done: drydock.py deploy, then drydock.py gate pass build --next specs|review`.
- Tests: `test_deploy_refuses_open_blocks`, `test_deploy_requires_base_branch_and_pushed_head`, `test_deploy_runs_verify_then_deploy_then_smoke` (orden comprobado con un archivo de traza), `test_deploy_failure_writes_failed_evidence`, `test_deploy_tolerates_only_state_file_changes`, `test_missing_deploy_json_exits_2`, `test_gate_pass_build_requires_deploy_evidence`.
- La fase `build` gana la sección de cierre de rebanada: un smoke en rojo se corrige con un bloque de corrección, nunca con un push a la base: tarea nueva en `tasks.md`, bloque nuevo en `blocks.json`, y `block start` revalida el plan.

### Tarea 12B: fase `review` y `clean-clone`

- [ ] Archivos: `phases/8-review.md`, `templates/docs/final-review.md`, `bin/drydock.py` (`clean-clone`), `tests/test_clean_clone.py`, `scenarios/08-review.md`
- Tests: `test_clean_clone_runs_verify_in_fresh_clone` (un archivo sin versionar del repo original no existe en el clon), `test_clean_clone_fails_when_verify_fails`, `test_gate_pass_review_requires_clean_clone_and_deploy`, `test_review_can_return_to_specs`. Se actualiza `test_review_closes` (T1), que pasa a necesitar clon limpio y evidencia de despliegue.
- Contrato: `GATE_CHECKS["review"]` corre `clean-clone` y exige evidencia de despliegue. `gate pass review --next specs` no cierra: vuelve a `specs` para una rebanada de corrección, con los gates `specs`, `blocks`, `build` y `review` en `null`. Orden de cierre: rama `chore/close` desde la base; ahí se escribe `final-review.md` y se corre `gate pass review`, que comprueba la evidencia de despliegue del `HEAD` de la base, no del de la rama; el commit con el informe y el estado cerrado entra por PR y no se vuelve a desplegar, porque solo toca docs y estado.
- Escenario 08: un requisito sin test, sembrado a propósito, aparece en la matriz de trazabilidad.

#### H6 — Piloto en .NET 10

### Tarea 13: un producto pequeño real, de punta a punta

- [ ] Reconfirmar los comandos de `verify-steps/dotnet.json` contra el SDK fijado y elegir la librería de tests de arquitectura en su fuente oficial.
- [ ] Registrar en `LEARNINGS.md`, por bloque: nivel, intentos, hallazgos del revisor, fallos de verify, exenciones de TDD, intervenciones de John, y los tiempos de `red-first`, de CI y de espera del auto-merge. Además: cuántos bloques T1 llegaron de verdad al auto-merge y por qué no los demás, y si cada archivo de `reviews/` coincide con la respuesta del revisor.
- [ ] Al cerrar: borrar cada regla que no evitó ningún fallo y subir un escalón de exigencia donde un fallo se repitió. Revisar con esos datos las cuatro decisiones que fueron contra la regla de John (despliegue, auto-merge, L2, Codex).

#### H7 — Codex (contrato; después de la poda del piloto)

### Tarea 14: el skill completo en Codex

- [ ] Archivos: `adapters/codex.md`, `agents/openai.yaml`, `bin/drydock.py` (`harness install` escribe también `.codex/hooks.json`), `tests/test_codex.py`, escenarios repetidos bajo Codex
- Contrato: enlace `~/.agents/skills/drydock` (con confirmación de John); `agents/openai.yaml` con `policy.allow_implicit_invocation: false`; el adaptador explica que el estado no se inyecta (se corre `status --soft` a mano), cómo se localiza la CLI y cómo se aprueba; `.codex/hooks.json` usa el mismo `pr_gate.py` con el argumento `--deny-on-ask`, leído de `sys.argv`: como Codex no admite `ask`, cada `ask` sale como `deny` con el motivo, y John corre las aprobaciones en su terminal. La regla 2 del router gana aquí la mención a `adapters/codex.md`, `status --phase` (que hoy imprime siempre `adapters/claude.md`) gana la elección de adaptador, y Spec Kit se inicializa con su integración de Codex (`--integration codex`; el Spec Kit 1.0.8 instalado la trae).
- Tests: `test_harness_installs_codex_hooks`, `test_openai_yaml_disables_implicit_invocation`, `test_ask_becomes_deny_for_codex`.
- Por comprobar antes de bajar a TDD: subagentes y elección de modelo por nivel en Codex, su política de aprobaciones como sustituto de las reglas `ask`, y el nombre de la integración de Spec Kit para Codex. Si Codex no puede rutear por nivel, el adaptador lo declara como límite y los bloques corren con el modelo de la sesión.

### B5. Pendiente de comprobar en ejecución

Casi nada de lo verificado se ejecutó: salió de documentación oficial y de `--help`. Solo se corrieron las expresiones regulares del hook y los globs de .NET. Cada punto dudoso tiene dónde se comprueba.

| Qué | Dónde |
|---|---|
| Inyección del estado con el skill enlazado; si `${CLAUDE_SKILL_DIR}` da el enlace o el destino | Comprobado en la aceptación de H0 (2026-11-16, `claude -p` en `dontAsk`): se inyecta sin prompt y da el enlace. Falta la sesión interactiva de John |
| `{}` con salida 0 no bloquea Bash bajo `onFailure: "block"`; un script roto sí | Paso 0 de H1; aceptación de H1 (1, 3) |
| `${CLAUDE_PROJECT_DIR}` dentro de `args` y bajo `claude --worktree` | Aceptación de H1 (2, 8) |
| Reglas `ask` con comodín inicial; `ask` gana a `allow`; decisión `ask` desde un hook; qué hace `ask` en cada modo de permisos | Paso 0 de H1; aceptación de H0 (5) y de H1 (4, 5) |
| Hook, reglas de permisos y agentes creados a mitad de sesión: si cargan sin reiniciarla | Paso 0 de H1 |
| Plugins de John que interceptan Bash (en esta sesión uno redirigió una llamada) o inyectan contexto en los subagentes | Paso 0 de H1; aceptación de H1 (9) |
| Plan de GitHub: protección de rama y check requerido en repos privados | Aceptación de H1 (7) |
| Versiones de `actions/checkout`, `setup-dotnet`, `setup-python`; Python 3.9 en los runners | T5 y cierre de H1 |
| Salidas reales de `gh pr view`, `gh pr checks --json` y `gh pr merge`: campos, códigos de salida, qué hace `--delete-branch` | Paso 0 de T6C; aceptación de H2 (1) |
| `claude -p` con `acceptEdits`: un `ask` sin nadie que responda es terminal | Paso 0 de H1; escenarios 06 y 07 |
| `/tasks` muestra modelo y esfuerzo por subagente | Aceptación de H2 (3) |
| Comandos .NET contra el SDK fijado; Microsoft.Testing.Platform; librería de arquitectura | H6 |
| Codex: subagentes, ruteo, aprobaciones | H7 |
| Cifras del ecosistema citadas en A7 de v0 | No se comprueban: no afectan al diseño |

## Verificación de punta a punta

1. **Unitarias:** `python3 -m unittest discover -s tests -v` en verde tras cada tarea (11 → 16 → 37 → 52 → 64 → 80 → 88 → 98 → 104 → 110 tests), también con `/usr/bin/python3` (3.9.6). Desde el cierre de H1, `./verify.sh` del propio repo, que incluye `red-first`.
2. **Aceptaciones manuales** de H0, H1 y H2, con sus resultados en `LEARNINGS.md`.
3. **Escenarios:** el 00 con `claude -p "/drydock" --permission-mode dontAsk`; el 06 y el 07 con `acceptEdits` y los comandos preaprobados, comparados con sus líneas base sin el skill (Paso 0 de H2).
4. **Piloto** (H6): un producto .NET 10 pequeño de la idea al servidor.

## Fuentes

Las de v0, más: permisos y modo sin interfaz de Claude Code (`code.claude.com/docs/en/permissions`, `…/headless`) · manual de `gh` (`cli.github.com/manual`) · `dotnet test`, `dotnet format` y filtros de VSTest en Microsoft Learn · documentación de skills, `AGENTS.md` y hooks de Codex · `specify --help` de la versión 1.0.8 instalada. Las citas y la URL de cada hallazgo están en `docs/superpowers/plans/2026-11-15-verification-evidence.json`; los hallazgos de la revisión adversaria, en `2026-11-15-review-checkpoint.json` y `2026-11-15-review-executor.md`, en la misma carpeta.
