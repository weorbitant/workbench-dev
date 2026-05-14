<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 2.0.0 (MAJOR — complete redefinition of project purpose and principles)
Modified principles:
  I.  Automation-First → Plugin-First
  II. Composability → Context-Aware Execution
  III. Declarative Specifications Before Implementation → Report-Oriented Output (retained, renamed)
  IV. Observability → Read Before Act (retained concept, narrowed focus)
  V.  Idempotency and Safety → retained, extended with credential safety
Added sections: none
Removed sections: none (restructured)
Templates requiring updates:
  ✅ .specify/templates/plan-template.md — reviewed; no changes needed
  ✅ .specify/templates/spec-template.md — reviewed; no changes needed
  ✅ .specify/templates/tasks-template.md — reviewed; no changes needed
Follow-up TODOs:
  - None. All placeholders resolved.
-->

# Orbitant Workbench Constitution

## Core Principles

### I. Plugin-First

Every daily work operation — ticket review, sprint analysis, service monitoring,
database inspection, report generation — MUST be delivered as a discrete Claude Code
skill or plugin. There are no ad-hoc scripts, no one-off commands, no manual processes
that cannot be invoked as a skill.

A capability that cannot be invoked with a single `/command` has not been delivered.

### II. Context-Aware Execution

Every plugin MUST detect its operating context before acting. Context includes:
the project management system in use (Jira, Linear, GitHub Issues…), the deployment
environment (cluster namespace, cloud provider, region), and the data store type
(PostgreSQL, MySQL, Redis…). Plugins MUST NOT hardcode connection details or
assume a fixed stack.

- Context detection runs automatically at plugin startup.
- If context cannot be determined, the plugin MUST ask — never guess silently.
- Detected context MUST be reusable across plugins within the same session.

### III. Report-Oriented Output

Every plugin that gathers or analyses information MUST produce a structured,
human-readable report as its primary output. Raw data dumps are not acceptable.

- Reports MUST include: summary headline, key metrics, actionable insights,
  and a recommended next action.
- Structured formats (Markdown tables, JSON when consumed by another plugin)
  MUST be used consistently.
- Insights MUST be surfaced proactively — plugins identify anomalies and risks
  without being asked to look for them specifically.

### IV. Read Before Act

Plugins that modify state (create tickets, trigger deployments, run migrations)
MUST first read and summarise the current state, then require explicit confirmation
before making any change.

- Read-only plugins run freely and may be auto-invoked by agents.
- Write plugins MUST display a confirmation prompt with a summary of the change
  and its scope before executing.
- Destructive operations (delete, scale-to-zero, drop) MUST require a typed
  confirmation phrase, not just a yes/no.

### V. Credential and Secret Safety

Secrets, tokens, connection strings, and credentials MUST never appear in plugin
output, reports, logs, or committed files.

- All credentials MUST be read from environment variables or a local secrets file
  listed in `.gitignore`.
- Plugin output that includes connection details MUST redact sensitive fields.
- If a plugin cannot find required credentials, it MUST fail with a clear message
  explaining where to set them — never fall back to prompting for inline input.

## Technology Stack

Plugins are Claude Code skills (Markdown + YAML frontmatter). Complex operations
are orchestrated via agents dispatched with the `Agent` tool.

**Primary runtime**: Claude Code (claude-sonnet-4-6 or higher)
**Plugin storage**: `plugins/` (this repo), installed to `.claude/skills/` or via
  `.claude-plugin` manifest for distribution
**Spec artifacts**: `.specify/memory/`, `specs/`
**Integrations**: Jira, GitHub, Kubernetes (`kubectl`), cloud CLIs (`gcloud`, `aws`)
**Output format**: Markdown (human reports), JSON (machine-readable inter-plugin data)

All plugins MUST follow the established frontmatter schema:
`name`, `description`, `model` (optional), `invocation` (optional),
`disable-model-invocation: true` for destructive plugins.

## Development Workflow

1. **Specify** (`/speckit-specify`) — Capture plugin capability and acceptance criteria.
2. **Clarify** (`/speckit-clarify`) — Resolve integrations, context detection, and
   output format ambiguities.
3. **Plan** (`/speckit-plan`) — Design context detection, data fetching, and report
   structure.
4. **Tasks** (`/speckit-tasks`) — Break into atomic, parallelizable implementation
   tasks.
5. **Implement** (`/speckit-implement`) — Build the plugin.
6. **Checklist** (`/speckit-checklist`) — Validate against acceptance criteria before
   merge.

Feature branches MUST follow `feat/<plugin-name>` or `fix/<plugin-name>`.
Direct commits to `main` are prohibited. All merges go through a PR.

## Governance

This constitution supersedes all informal practices. Amendments require:
1. A documented rationale (what changed and why).
2. Version bump per semantic versioning rules (MAJOR/MINOR/PATCH).
3. Propagation check across all `.specify/templates/` files.
4. Commit message: `docs: amend constitution to vX.Y.Z (<summary>)`.

All PRs MUST verify compliance with the five Core Principles before merge.
Principle violations MUST be resolved, not suppressed.
Any new integration (external API, cloud provider, project tool) MUST be declared
in the Technology Stack section before a plugin depending on it is merged.

**Version**: 2.0.0 | **Ratified**: 2026-05-14 | **Last Amended**: 2026-05-14
