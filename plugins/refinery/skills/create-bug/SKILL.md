---
name: create-bug
description: "Use when creating a well-structured bug report with root cause analysis. Use when user says 'create bug', 'report bug', 'log bug', 'new bug', or describes a defect."
argument-hint: "[brief description]"
allowed-tools:
  - AskUserQuestion
  - ToolSearch
model: sonnet
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `issue_tracker` — determines which adapter to load
- Issue tracker-specific config (e.g., `jira.default_project`, `jira.default_bug_epic`)

## Step 1 — Load adapter

Read the adapter file at `${CLAUDE_PLUGIN_ROOT}/skills/create-bug/adapters/{issue_tracker}.md`.
If the adapter does not exist, tell the user that `{issue_tracker}` is not yet supported and stop.

All tool-specific calls come from the adapter. Do not invent tool calls.

## Step 2 — Gather information

If `$ARGUMENTS` contains a brief description, use it as the starting point. Otherwise, ask.

Gather the following through conversation:

1. **What is broken?** — The observable defect (what the user sees)
2. **Where does it happen?** — Service, module, endpoint, or screen
3. **Environment** — dev, staging, prod
4. **Steps to reproduce** — if known
5. **Expected behavior** — what should happen
6. **Evidence** — error logs, screenshots, HTTP status codes, stack traces
7. **Severity assessment** — blocking users? data loss? workaround exists?

Do NOT ask all questions at once. Start with what the user already provided and only ask for what is missing. Be conversational.

## Step 3 — Root cause analysis

Based on the gathered information, analyze and propose:

1. **Probable root cause** — what is likely failing and why
2. **Required fix** — what needs to change at a high level
3. **Impact** — what is affected (users, data, other services)

Present this analysis to the user for validation before creating the ticket.

## Step 4 — Find parent epic

Use the adapter's **search** command to find the configured bug epic (from config).
If the configured epic does not exist or is not set, ask the user if they want to:
- Create the bug without a parent epic
- Specify a different parent epic

## Step 5 — Build bug description

Use this template for the bug description body:

```
## Descripción
{Clear explanation of the defect — what happens, when, and the observable impact}

## Evidencia
- **Entorno:** {environment}
- **Servicio/Módulo:** {service or module name}
- **Error observado:** {error message, HTTP status, stack trace snippet}
- **Pasos para reproducir:**
  1. {step 1}
  2. {step 2}
  3. {step 3}

## Causa raíz
{Analysis of why this is happening — the technical root cause}

## Fix requerido
{What needs to change to resolve the issue}

## Impacto
- **Usuarios afectados:** {scope — all users, specific role, specific flow}
- **Severidad:** {critical / high / medium / low}
- **Workaround:** {exists? describe it, or "No hay workaround conocido"}
```

## Step 6 — Build summary

Format the ticket summary as:
```
{service}: {what is broken and the visible effect}
```

Examples:
- `auth-service: login fails with 500 for users with special characters in email`
- `payments: duplicate charges created when retry button is clicked rapidly`
- `dashboard: performance metrics chart shows empty state despite data existing`

## Step 7 — Create the bug

Show the user the complete bug (summary + description) for approval.

Once approved, use the adapter's **create issue** command with:
- Type: Bug
- Summary: from Step 6
- Description: from Step 5
- Parent: from Step 4 (if found)
- Project: from config

## Step 8 — Post-creation

After creation:
1. Display the created ticket key and URL
2. Ask if the user wants to:
   - **Assign it** to someone (use adapter's search for user + edit command)
   - **Set priority** (use adapter's edit command)
   - **Add labels** (use adapter's edit command)
   - **Create another bug** (restart from Step 2)
