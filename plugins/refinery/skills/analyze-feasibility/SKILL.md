---
name: analyze-feasibility
description: "Use when evaluating whether a technical approach is feasible against the current codebase. Use when user says 'analyze feasibility', 'is this feasible', 'evaluar factibilidad', 'technical analysis', or asks whether an approach will work."
argument-hint: "[technical approach or ticket]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, this skill can still operate on the codebase directly. Log a warning but continue.

No specific config is required — this skill works directly on the codebase.

## Step 1 — Parse argument

From `$ARGUMENTS`, extract the technical approach or ticket reference to evaluate.
If no argument provided, ask the user what they want to assess.

The input can be:
- A description of a technical approach ("Add caching layer for user queries")
- A ticket key (fetch it using the issue tracker adapter if available)
- A technical question ("Can we use WebSockets for real-time notifications?")

## Step 2 — Understand the proposal

Break down the proposal into concrete technical actions:
1. What needs to be created (new files, modules, services)
2. What needs to be modified (existing code changes)
3. What needs to be integrated (external services, libraries, APIs)
4. What data changes are required (new tables, field changes, migrations)

Present this breakdown to the user for confirmation before proceeding.

## Step 3 — Check dependencies

Search `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, or equivalent for:
1. Required libraries that already exist
2. Required libraries that need to be added
3. Version conflicts with existing dependencies
4. Deprecated or unmaintained dependencies being proposed

```
Glob: **/package.json, **/requirements.txt, **/go.mod, **/Cargo.toml, **/pom.xml
```

## Step 4 — Assess architecture fit

Search the codebase for existing patterns:

1. **Module structure** — How is the code organized? Does the proposal fit?
   - Glob: `src/*/`, `app/*/`, `lib/*/`
   - Look for established conventions (feature-based, layer-based, domain-driven)

2. **Existing patterns** — Are there similar implementations?
   - Grep: for pattern names, similar features, analogous implementations
   - If found, the proposal should follow the same pattern

3. **Configuration patterns** — How are configs managed?
   - Grep: `ConfigModule`, `config/`, `env`, settings patterns

4. **Error handling** — What pattern exists?
   - Grep: custom error classes, error handlers, try-catch patterns

5. **Testing patterns** — How are tests structured?
   - Glob: `**/*.test.*`, `**/*.spec.*`, `**/__tests__/**`

## Step 5 — Identify implementation gaps

For each action in the proposal, assess:

| Acción | Patrón existente | Gap | Esfuerzo estimado |
|--------|-----------------|-----|-------------------|
| {action} | {existing pattern or "none"} | {what's missing} | {low/medium/high} |

Gaps include:
- Missing abstractions that need to be created
- Missing infrastructure (queues, caches, databases)
- Missing test infrastructure
- Missing CI/CD pipeline steps

## Step 6 — Assess risks

Evaluate risks on two dimensions:

### Technical risks
- **Breaking changes** — Will this change existing contracts or APIs?
- **Performance impact** — Will this degrade performance? Where?
- **Data integrity** — Can this corrupt or lose data?
- **Rollback complexity** — How hard is it to undo if something goes wrong?
- **Testing gaps** — Areas that are hard to test

### Business risks
- **Scope creep** — Will this require touching more code than expected?
- **Timeline impact** — How does this affect delivery estimates?
- **Dependency on others** — Does this require work from other teams?
- **User impact** — Will users experience disruption during rollout?

## Step 7 — Present trade-offs

When multiple approaches exist, present them as options:

```
━━ OPCIÓN A: {approach_name} ━━━━━━━━━━━━━━━━
Pro:
  + {advantage_1}
  + {advantage_2}
Contra:
  - {disadvantage_1}
  - {disadvantage_2}
Esfuerzo: {low/medium/high}
Riesgo: {low/medium/high}

━━ OPCIÓN B: {approach_name} ━━━━━━━━━━━━━━━━
Pro:
  + {advantage_1}
Contra:
  - {disadvantage_1}
Esfuerzo: {low/medium/high}
Riesgo: {low/medium/high}
```

## Step 8 — Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ FEASIBILITY ANALYSIS: {proposal_summary}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━ VEREDICTO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{✅ Factible | ⚠️ Factible con reservas | 🚫 No factible}
{One paragraph explaining the verdict}

━━ DEPENDENCIAS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Existentes: {list of deps already available}
Necesarias: {list of deps to add}
Conflictos: {list of conflicts, or "Ninguno"}

━━ AJUSTE ARQUITECTÓNICO ━━━━━━━━━━━━━━━━━━━━━
{Assessment of how well this fits existing patterns}

Patrones relevantes encontrados:
- {pattern_1} en {file_path}
- {pattern_2} en {file_path}

━━ GAPS DE IMPLEMENTACIÓN ━━━━━━━━━━━━━━━━━━━━
{gap table from Step 5}

━━ RIESGOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Técnicos:
- {risk_1}: {mitigation}
- {risk_2}: {mitigation}

Negocio:
- {risk_1}: {mitigation}
- {risk_2}: {mitigation}

━━ OPCIONES (if applicable) ━━━━━━━━━━━━━━━━━━
{trade-off comparison from Step 7}

━━ RECOMENDACIÓN ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{Final recommendation with reasoning}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
