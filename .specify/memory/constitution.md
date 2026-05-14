<!--
SYNC IMPACT REPORT
==================
Version change: N/A (initial) → 1.0.0
Added sections: Core Principles (I–V), Technology Stack, Development Workflow, Governance
Removed sections: N/A (initial creation)
Templates requiring updates:
  ✅ .specify/templates/plan-template.md — reviewed; no changes needed
  ✅ .specify/templates/spec-template.md — reviewed; no changes needed
  ✅ .specify/templates/tasks-template.md — reviewed; no changes needed
Follow-up TODOs:
  - None. All placeholders resolved.
-->

# Orbitant Workbench Constitution

## Core Principles

### I. Automation-First

Every recurring work process — ticket definition, requirements gathering, deployment
operations, code review, planning — MUST have an automated path via a skill, agent,
or workflow before it is considered done. Manual-only steps are technical debt.

Automation is the product. If a process can only be executed by a human reading
instructions, it has not been delivered.

### II. Composability

Skills, agents, and workflows MUST be modular units that compose cleanly.
A skill does one thing well. An agent orchestrates skills. A workflow sequences agents.

- No monolithic automation scripts that mix multiple concerns.
- Each skill MUST be independently invocable and testable in isolation.
- Shared logic MUST be extracted into reusable primitives, not copy-pasted.

### III. Declarative Specifications Before Implementation

Every automated process MUST be fully specified (user scenarios, acceptance criteria,
edge cases) before implementation begins. Specification is not overhead — it is the
design artifact that makes automation trustworthy.

- The speckit lifecycle (specify → clarify → plan → tasks → implement) is MANDATORY
  for all non-trivial automations.
- Shortcuts that skip spec or plan stages MUST be explicitly justified and documented.

### IV. Observability

Every automated operation MUST produce traceable, human-readable output. Failures MUST
surface immediately with actionable error messages — never silent failures.

- Structured output (JSON or Markdown) preferred for machine-readable results.
- All agents and workflows MUST log their intent before acting and their result after.
- Destructive or irreversible operations MUST require explicit confirmation.

### V. Idempotency and Safety

Automated operations MUST be safe to re-run. Running the same skill or workflow twice
MUST NOT produce unintended side effects.

- Operations that modify shared state (branches, deployments, tickets) MUST check
  current state before acting.
- Reversibility MUST be considered at design time; rollback paths MUST be documented
  for deployment operations.
- Secrets and credentials MUST never appear in skill outputs, logs, or committed files.

## Technology Stack

Skills are Markdown files with YAML frontmatter, executed by Claude Code via the
`Skill` tool. Agents are Claude Code subagents dispatched via the `Agent` tool.
Workflows are sequences of skills and agents defined in `.specify/workflows/`.

**Primary runtime**: Claude Code (claude-sonnet-4-6 or higher by default)
**Skill storage**: `.claude/skills/` (project-level), `~/.claude/skills/` (user-level)
**Workflow definitions**: `.specify/workflows/`
**Spec artifacts**: `.specify/memory/`, `specs/`
**Extensions**: `.specify/extensions/` (git, integrations, etc.)

All skills MUST follow the established frontmatter schema:
`name`, `description`, `model` (optional), and `invocation` (optional).

## Development Workflow

1. **Specify** (`/speckit-specify`) — Capture user scenarios and acceptance criteria.
2. **Clarify** (`/speckit-clarify`) — Resolve ambiguities before design.
3. **Plan** (`/speckit-plan`) — Design the technical approach and research dependencies.
4. **Tasks** (`/speckit-tasks`) — Break the plan into atomic, parallelizable tasks.
5. **Implement** (`/speckit-implement`) — Execute tasks; run skills/agents as needed.
6. **Checklist** (`/speckit-checklist`) — Validate against acceptance criteria before merge.

Feature branches MUST follow the convention `feat/<name>` or `fix/<name>`.
Direct commits to `main` are prohibited. All merges MUST go through a PR.

## Governance

This constitution supersedes all informal practices. Amendments require:
1. A documented rationale (what changed and why).
2. Version bump per semantic versioning rules (MAJOR/MINOR/PATCH).
3. Propagation check across all `.specify/templates/` files.
4. Commit message: `docs: amend constitution to vX.Y.Z (<summary>)`.

All PRs MUST verify compliance with the five Core Principles before merge.
Principle violations MUST be resolved, not suppressed.
Complexity introduced beyond what Principle II (Composability) allows MUST be
justified in the PR description.

**Version**: 1.0.0 | **Ratified**: 2026-05-14 | **Last Amended**: 2026-05-14
