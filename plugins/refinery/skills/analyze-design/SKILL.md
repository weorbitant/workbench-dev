---
name: analyze-design
description: "Use when extracting data fields, UI states, actions, and flows from a design. Use when user says 'analyze design', 'analizar diseño', 'review design', 'extract from figma', or shares a design URL."
argument-hint: "[design-url]"
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
  - ToolSearch
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `design_tool` — figma, penpot, or none

If `design_tool` is "none", tell the user no design tool is configured and stop.

## Step 1 — Load adapter

Read the adapter file at `${CLAUDE_PLUGIN_ROOT}/skills/analyze-design/adapters/{design_tool}.md`.
If the adapter does not exist, tell the user that `{design_tool}` is not yet supported and stop.

All tool-specific calls come from the adapter. Do not invent tool calls.

## Step 2 — Parse design URL

From `$ARGUMENTS`, extract the design URL.
If no URL provided, ask the user for one.

Use the adapter's URL-parsing rules to extract the necessary identifiers (file key, node IDs, etc.).

## Step 3 — Fetch design

Use the adapter's commands to:
1. Get the design context / metadata
2. Get a screenshot or visual representation of the design

If the design has multiple screens/frames, list them and ask the user which one(s) to analyze, or analyze all if the user confirms.

## Step 4 — Extract data fields

For EVERY input field, dropdown, text display, or data-bound element in the design, extract:

| Campo | Tipo | Obligatorio | Validación visible | Valor por defecto | Pregunta |
|-------|------|-------------|-------------------|-------------------|----------|
| {field_name} | {text/number/date/select/checkbox/...} | {yes/no/unclear} | {what constraints are visible} | {if any} | {what is not clear} |

### Interrogation framework for each field:
- What data type does this field expect?
- Is it required or optional? (look for asterisks, bold labels)
- What validation rules apply? (visible constraints, format hints)
- What is the source of this data? (user input, system-generated, from API)
- What happens when the value is empty?
- What happens when the value is invalid?
- Are there predefined options? If dropdown/select, what are the options?

## Step 5 — Extract table columns

For every table or list in the design:

| Columna | Tipo de dato | Ordenable | Filtrable | Acción |
|---------|-------------|-----------|-----------|--------|
| {column} | {type} | {yes/no/unclear} | {yes/no/unclear} | {click action if any} |

Questions per table:
- What is the data source?
- What is the default sort order?
- Is there pagination? What page size?
- What happens when the table is empty?
- Can rows be selected? What bulk actions exist?

## Step 6 — Extract actions (buttons, links, interactions)

For every button, link, or interactive element:

| Acción | Trigger | Resultado esperado | Confirmación | Pregunta |
|--------|---------|-------------------|--------------|----------|
| {action_name} | {click/hover/submit} | {what should happen} | {needs confirmation dialog?} | {what is unclear} |

## Step 7 — Detect states

Check if the design covers these states. Mark each as detected or missing:

- **Empty state** — no data to display
- **Loading state** — data is being fetched
- **Error state** — something went wrong
- **Success state** — action completed successfully
- **Partial state** — some data loaded, some failed
- **Pagination** — more data than fits on one screen
- **Permission denied** — user lacks access
- **First-time / onboarding** — first use experience
- **Offline** — no network connection

## Step 8 — Detect implicit flows

Look for flows that are implied but not explicitly shown:
- Form submission → what happens on success? On failure?
- Delete action → is there a confirmation? Can it be undone?
- Navigation → where does the back button go?
- Multi-step process → what are all the steps? Can you go back?
- Concurrent editing → what if two users edit simultaneously?

## Step 9 — Output

Present results in this format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 DESIGN ANALYSIS: {design_name}
   Tool: {design_tool} | Screens: {count}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━ DATOS ENCONTRADOS ━━━━━━━━━━━━━━━━━━━━━━━━━
{data fields table from Step 4}

━━ TABLAS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{table columns from Step 5}

━━ ACCIONES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{actions table from Step 6}

━━ ESTADOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Empty state: {description}
  ✅ Loading state: {description}
  ❌ Error state: NOT FOUND
  ❌ Permission denied: NOT FOUND
  ...

━━ FLUJOS IMPLÍCITOS ━━━━━━━━━━━━━━━━━━━━━━━━━
1. {flow_description}
2. {flow_description}

━━ PREGUNTAS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. {question with context}
2. {question with context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
