---
name: scaffold-skill
description: Use when creating a new skill from scratch in this repo. Scaffolds the directory structure and pre-filled SKILL.md from a natural language description. TRIGGER when: user says "create a new skill", "scaffold skill", "nueva skill", "crear skill", "add skill to X plugin", "quiero una skill que haga". SKIP: editing an existing skill (use the creating-skills guide); learning about skill authoring (use creating-skills).
argument-hint: "[skill-name] [plugin]"
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
model: sonnet
---

## Phase 0 — Discover plugins

List available plugins in this repo:

```bash
ls ${CLAUDE_PLUGIN_ROOT}/../
```

Store the result as `{available_plugins}` (directory names only, ignore non-plugin dirs).

If `$ARGUMENTS` contains both a skill name and a plugin name that matches one of `{available_plugins}`, extract them and skip to Phase 2.

## Phase 1 — Two intake questions

Ask each question separately using `AskUserQuestion`.

**Question 1:**
```
¿En qué plugin va esta skill y cómo se llama?

Plugins disponibles: {available_plugins}

Formato: plugin/nombre-en-kebab-case
Ejemplo: ops-suite/check-alerts
```

Store as `{plugin}` and `{skill_name}`.

**Question 2:**
```
Describe en 1-2 frases qué hace esta skill y cuándo se usa.
Ejemplo: "Consulta el estado de los pods en un entorno y alerta si hay crashloops.
Se usa cuando el usuario pregunta si un servicio está caído."
```

Store as `{description_raw}`.

## Phase 2 — Infer decisions

From `{skill_name}` and `{description_raw}`, infer the following fields without asking the user:

### model
- Keywords → `sonnet`: "analyze", "diagnose", "cross-reference", "evaluate", "triage", "compare",
  "report", "feasibility", "review", "analizar", "evaluar", "diagnóstico"
- Keywords → `haiku`: "list", "check", "status", "count", "show", "display", "get",
  "listar", "verificar", "estado", "contar"
- Default: `sonnet`

### disable-model-invocation
- `true` if description contains any of: "deploy", "send message", "enviar mensaje",
  "run migration", "ejecutar migración", "reprocess", "reprocesar", "delete", "eliminar",
  "publish", "publicar", "commit", "push", "create ticket", "crear ticket"
- Default: `false`

### needs_adapters
- `true` if description mentions: "kubernetes", "docker", "ecs", "rabbitmq", "kafka",
  "azure service bus", "sqs", "jira", "linear", "github issues", "figma", "penpot",
  "confluence", "notion", "postgresql", "mysql", "github actions", "gitlab ci",
  "different providers", "technology-agnostic", "múltiples tecnologías"
- Default: `false`

### needs_references
- `true` if description implies complex output: "detailed report", "template", "format",
  "multiple sections", "informe detallado", "plantilla", "largo output"
- Default: `false`

### allowed-tools
Start with `[AskUserQuestion]` always. Then add:
- `Bash` if: "bash", "commands", "run", "execute", "kubectl", "cli", "script", "comandos"
- `Read, Grep, Glob` if: "search codebase", "find", "read files", "codebase", "buscar código"
- `Write` if: "create files", "write", "scaffold", "generate", "crear archivos"

### argument-hint
Infer from description:
- Mentions ticket/issue → `"[TICKET-KEY]"`
- Mentions environment → `"[environment]"`
- Mentions service → `"[service-name] [environment]"`
- Mentions PR/commit → `"[PR-number] [environment]"`
- Nothing specific → `""`

### trigger_phrases
Generate 3-4 natural language phrases a user would say to trigger this skill.
Base them on the description, not the name.

### skip_guidance
Generate one SKIP clause pointing to the most likely overlapping skill in `{plugin}`.

## Phase 3 — Confirmation card

Display the summary using `AskUserQuestion`:

```
Skill a crear: {plugin}/skills/{skill_name}/
─────────────────────────────────────────────
  model:                    {model}
  disable-model-invocation: {true|false}
  adapters/:                {sí|no}
  references/:              {sí|no}
  allowed-tools:            [{tools}]
  argument-hint:            "{argument_hint}"

TRIGGER phrases inferidas:
  - "{phrase_1}"
  - "{phrase_2}"
  - "{phrase_3}"

Description generada:
  "{full_description_with_trigger_skip}"

¿Ajustar algo? (no / [campo: nuevo valor])
```

If the user responds with corrections (e.g., `model: haiku` or `adapters: sí`), apply them
and show the updated card again. Repeat until the user answers `no`.

## Phase 4 — Generate files

### Always: `skills/{skill_name}/SKILL.md`

Write to `${CLAUDE_PLUGIN_ROOT}/../{plugin}/skills/{skill_name}/SKILL.md`:

```markdown
---
name: {skill_name}
description: {full_description_with_trigger_skip}
argument-hint: "{argument_hint}"
{disable_model_invocation_line}allowed-tools:
{allowed_tools_lines}model: {model}
---

## Step 0 — Load configuration

Check if `/tmp/{plugin}-session/config.json` exists:
- If yes, read it (pre-parsed by session hook).
- If no, read `${CLAUDE_PLUGIN_ROOT}/config.yaml`. If it does not exist, tell the user to
  copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

{adapter_step}

## Step N — [Describe main logic here]

TODO: replace this step with the actual logic.

{output_format}
{confirmation_block}
```

Where:
- `{disable_model_invocation_line}` = `disable-model-invocation: true\n` if destructive, else empty
- `{allowed_tools_lines}` = one `  - Tool\n` per tool
- `{adapter_step}` = Step 1 adapter block (see below) if `needs_adapters`, else empty
- `{output_format}` = output format section (see below) if not destructive
- `{confirmation_block}` = confirmation block (see below) if `disable-model-invocation: true`

**Adapter step (if needs_adapters):**
```markdown
## Step 1 — Load adapter

Read the adapter file at `adapters/{adapter_key}.md` (in this skill's directory).
If it does not exist, tell the user that `{adapter_key}` is not yet supported and stop.

All technology-specific commands come from the adapter. Do not invent commands.
```
Where `{adapter_key}` is inferred from config (e.g., `{orchestrator}`, `{message_broker}`, `{issue_tracker}`).

**Output format section:**
```markdown
## Output format

Present results as:

\`\`\`
[TODO: define output format]
\`\`\`
```

**Confirmation block (if destructive):**
```markdown
**ALWAYS ask for explicit confirmation before proceeding.**

Use `AskUserQuestion`:
\`\`\`
[TODO: describe what the user needs to confirm]

Proceed? (yes / no)
\`\`\`
```

---

### Always: `commands/{skill_name}.md`

Write to `${CLAUDE_PLUGIN_ROOT}/../{plugin}/commands/{skill_name}.md`:

```markdown
---
description: "{first sentence of description}"
{disable_model_invocation_line}---

Invoke the {plugin}:{skill_name} skill and follow it exactly as presented to you
```

---

### If needs_adapters: `skills/{skill_name}/adapters/example.md`

Write to `${CLAUDE_PLUGIN_ROOT}/../{plugin}/skills/{skill_name}/adapters/example.md`:

```markdown
# Example Adapter — {skill_name}

Replace this file with `{technology}.md` (e.g., `kubernetes.md`, `jira.md`).
All commands use `{config.X.Y}` placeholders — never hardcode environment-specific values.

## [Command section name]

\`\`\`bash
# command with {config.environments.{env_name}.context} placeholders
\`\`\`
```

---

### If needs_references: create `skills/{skill_name}/references/` directory

```bash
mkdir -p ${CLAUDE_PLUGIN_ROOT}/../{plugin}/skills/{skill_name}/references
```

---

## Phase 5 — Report

Display:

```
✓ Skill scaffolded: {plugin}/skills/{skill_name}/

Files created:
  {plugin}/skills/{skill_name}/SKILL.md
  {plugin}/commands/{skill_name}.md
{optional_adapters_line}
{optional_references_line}

Next steps:
  1. Edit SKILL.md — replace "Step N" with the actual logic
  2. Run the triggering test: ask Claude something that should activate it (without /invoking it)
  3. Run the functional test: invoke with /{plugin}:{skill_name}
```
