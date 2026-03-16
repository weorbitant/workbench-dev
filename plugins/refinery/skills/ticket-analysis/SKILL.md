---
name: ticket-analysis
description: "Use when performing a comprehensive ticket analysis across design, documentation, data model, and technical feasibility. Use when user says 'analyze ticket', 'ticket analysis', 'análisis de ticket', or needs deep understanding before implementation."
argument-hint: "[TICKET-KEY or URL]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Agent
  - AskUserQuestion
  - ToolSearch
  - Edit
  - Write
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `issue_tracker` — determines which adapter to load
- `design_tool` — figma, penpot, or none
- `docs_sources` — array of documentation sources
- `ticket_analysis.ui_keywords` — keywords that indicate UI work
- Communication config for sending results

## Step 1 — Load adapter

Read the adapter file at `${CLAUDE_PLUGIN_ROOT}/skills/ticket-analysis/adapters/{issue_tracker}.md`.
If the adapter does not exist, tell the user that `{issue_tracker}` is not yet supported and stop.

## Core principles

1. **Zero assumptions** — Never infer what the ticket does not explicitly state. If something is unclear, mark it as a question.
2. **Traceability** — Every finding must reference its source (ticket field, design screen, doc page, code file).
3. **Fixed structure** — Always output the 8 sections defined in the output format, even if some are empty.

## Phase 1 — Fetch and parse ticket

Use the adapter's **fetch ticket** command to retrieve `{key}`.

Extract:
- Title, description, acceptance criteria, status, type, assignee, labels
- **URLs** — all URLs in description and comments (design links, doc links, API specs)
- **Data terms** — entity names, field names, table names mentioned
- **Referenced tickets** — other ticket keys mentioned (pattern: `[A-Z]+-\d+`)
- **Comments** — all comments, in chronological order

## Phase 1b — Classify ticket type

Based on title, description, and labels, classify the ticket as one of:

| Type | Indicators |
|------|-----------|
| `business-feature` | User-facing value, UI work, business rules |
| `technical-infra` | Infrastructure, refactoring, performance, DevOps |
| `bug-fix` | Defect, error, unexpected behavior |
| `data-integration` | Data migration, API integration, ETL, sync |

The classification determines which Phase 2 agents to launch.

## Phase 2 — Parallel analysis

Launch up to 4 agents in parallel based on ticket type and available tools. Each agent is a sub-analysis.

### Agent A: Design analysis
**Launch when:** `{config.design_tool}` is not "none" AND (ticket has design URLs OR title/description matches any `{config.ticket_analysis.ui_keywords}`)

Use the `analyze-design` skill approach:
- Fetch the design using the design tool
- Extract data fields, states, actions
- Compare with ticket description

### Agent B: Documentation analysis
**Launch when:** `{config.docs_sources}` is not empty

Use the `analyze-docs` skill approach:
- Search each documentation source for key terms from the ticket
- Extract relevant business rules, definitions, existing specs

### Agent C: Data model analysis
**Launch when:** ticket mentions entities, fields, tables, or database operations

Use the `analyze-data-model` skill approach:
- Search codebase for mentioned entities
- Map fields, relationships, validations
- Identify gaps between ticket and existing model

### Agent D: Technical feasibility
**Launch when:** ticket involves code changes

Use the `analyze-feasibility` skill approach:
- Check existing patterns in codebase
- Identify affected modules
- Assess implementation complexity

## Phase 3 — Cross-reference

Combine results from all agents. For each data point (field, rule, state, action):

Build a cross-reference table:

| Dato | Ticket | Diseño | Documentación | Código | Estado |
|------|--------|--------|---------------|--------|--------|
| {field} | {present/absent} | {present/absent} | {present/absent} | {present/absent} | {status} |

Status values:
- ✅ **Claro** — consistent across all sources
- ❓ **Dudoso** — present in some sources but inconsistent or incomplete
- ❌ **No existe** — mentioned in ticket but not found in any other source

## Phase 4 — Build questions

Group all questions by audience:

- **Product / PO** — business rules, scope, priority
- **Design / UX** — visual behavior, states, interactions
- **Tech Lead** — architecture, approach, data model
- **QA** — test scenarios, edge cases
- **Data Team** — data sources, transformations, validations

Each question must:
1. State what is unclear
2. Reference the source that triggered it
3. Suggest options when possible

## Phase 5 — Define scope

Based on all gathered information, classify each requirement:

- **SE ENTREGA** — fully defined, design exists, data model supports it, technically feasible
- **NO SE ENTREGA** — explicitly out of scope or not mentioned in ticket
- **BLOQUEADO** — cannot implement without answers to blocking questions

## Phase 6 — Next steps

Define concrete next steps:
1. Questions that must be answered before starting
2. Technical spikes needed
3. Design clarifications needed
4. Dependencies to unblock
5. Suggested subtask breakdown

## Phase 7 — Output

Read the output format at [references/output-format.md](references/output-format.md).

Build the report using the fixed 8-section structure defined there. Never skip sections — if a section has no findings, write "No se encontraron hallazgos en esta sección."

## Phase 8 — Offer actions

1. **Comment on ticket** — Post a summary of findings and questions using the adapter's comment command
2. **Update ticket** — Add scope definition and questions to ticket description
3. **Create subtasks** — Break down into implementation subtasks using the adapter
4. **Send to team** — If communication tool is configured, send summary to team channel
5. **Export** — Display for copying
