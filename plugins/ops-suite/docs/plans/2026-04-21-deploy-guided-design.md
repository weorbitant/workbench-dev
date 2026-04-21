# workflow-deploy — Interactive Deployment Workflow

**Date:** 2026-04-21
**Status:** Approved

## Problem

The existing `deploy` skill is linear and non-interactive. The user has no natural participation points during the deployment process — it either runs automatically or requires manual skill-chaining. There is no guided experience that collects context upfront and walks the user through each destructive step.

## Solution

A new `workflow-deploy` command + skill that wraps the existing `deploy` skill with an interactive wizard layer. It does **not** replace `deploy` — the existing skill remains for programmatic/chained use. `workflow-deploy` is the human-facing layer.

## Interaction Model

Two phases: **intake form** (all questions upfront) + **execution with checkpoints** (confirmation only at destructive steps).

### Phase A — Intake Form

Four questions, one at a time via `AskUserQuestion`:

1. PR number or commit ref to deploy
2. Target environment (from config)
3. Does this PR include DB migrations? (`yes / no / auto-detect`)
4. Generate a rollback plan before deploying? (`yes / no`)

### Phase B — Pre-flight (read-only, no confirmation)

- Verify PR is merged + extract image tag
- Show current state of target environment
- If `auto-detect`: check pending migrations
- If rollback plan requested: generate and display using `references/rollback-templates.md`
- Display full deployment plan summary

### Checkpoint 1 — Confirm deploy

```
🚀 Ready to deploy
  Change:      PR #89 — Add payment webhook
  Image tag:   abc1234
  Environment: prod
  Current tag: def5678
  Migrations:  2 pending

Proceed? (yes / no)
```

Applies to **all environments** (dev, staging, prod). The workflow is always interactive.

### Phase C — Deploy

Trigger deployment, monitor CI run progress.
On failure → stop, show logs, suggest rollback.

### Checkpoint 2 — Confirm migrations

Only shown if migrations exist (detected or user said yes).

```
⚠️  2 pending migrations detected
  Run migrations now? (yes / no / show them first)
```

If skipped → warn that service may be unstable.

### Phase D — Post-deploy verification (automatic, no confirmation)

- `service-status` — pod health check
- `service-logs` — errors in last 5 minutes

### Final Report

```
── Deployment Summary ──────────────────────────
  PR:          #89 — Add payment webhook
  Environment: prod
  Image tag:   abc1234
  Duration:    4m 32s

  [✓] Deploy:      3/3 pods running
  [✓] Migrations:  2 applied
  [✓] Health:      healthy
  [✓] Logs:        no errors

  Overall: SUCCESS
────────────────────────────────────────────────
```

## Architecture

```
commands/workflow-deploy.md          ← entry point: /ops-suite:workflow-deploy
skills/workflow-deploy/
  SKILL.md                           ← wizard logic
  references/
    rollback-templates.md            ← rollback plan templates by change type
```

### Relationship to existing skills

```
workflow-deploy
  ├── Wraps: deploy (pre-flight + trigger)
  ├── Chains: db-migrate (if migrations confirmed)
  └── Chains: service-status + service-logs (post-deploy)
```

`workflow-deploy` inherits session state from `/tmp/ops-suite-session/` — does not re-read config or re-ask for already-known values.

## Skill Metadata Standard (applies to all ops-suite skills)

All SKILL.md files must follow the `creating-skills` best practices:

### Description format

```yaml
description: >
  Use when [trigger conditions]. [What it does].
  TRIGGER when: [natural language phrases; semicolon-separated].
  SKIP: [when NOT to trigger — direct to correct skill].
```

### Required changes per skill

| Skill | Model change | Description changes |
|---|---|---|
| `service-status` | haiku ✓ | Add TRIGGER when + SKIP |
| `service-logs` | **sonnet → haiku** | Add TRIGGER when + SKIP |
| `db-query` | sonnet ✓ | Add TRIGGER when + SKIP |
| `db-migrate` | haiku ✓ | Add trigger phrases + TRIGGER when + SKIP |
| `queue-triage` | sonnet ✓ | Add TRIGGER when + SKIP |
| `queue-reprocess` | haiku ✓ | Add trigger phrases + TRIGGER when + SKIP |
| `deploy` | sonnet ✓ | Add trigger phrases + TRIGGER when + SKIP |
| `workflow-deploy` (new) | sonnet | Full description with TRIGGER when + SKIP |

### Target descriptions

**service-status:**
```yaml
description: >
  Use when checking pod/container health, service availability, or deployment state.
  TRIGGER when: user asks "is X running?", "check pods", "service down", "crashloop",
  "restart count", "container health", "check services", "deployment status".
  SKIP: log content analysis (use service-logs); database queries (use db-query).
```

**service-logs:**
```yaml
description: >
  Use when searching or analyzing logs from a service or container.
  TRIGGER when: user asks "any errors?", "check logs", "what's failing?", "stack trace",
  "exceptions", "debug logs", "recent errors in X", "log search".
  SKIP: pod health checks (use service-status); database queries (use db-query).
```

**db-migrate:**
```yaml
description: >
  Use when checking or applying pending database migrations on remote environments.
  TRIGGER when: user asks "run migrations", "apply migrations", "pending schema changes",
  "migration status", "update schema", "db migrate", "schema migration".
  SKIP: querying data (use db-query); checking service health (use service-status).
```

**queue-reprocess:**
```yaml
description: >
  Use when moving failed messages from a dead letter queue back to the main queue.
  TRIGGER when: user asks "reprocess DLQ", "move messages back", "retry failed messages",
  "shovel messages", "republish DLQ", "requeue failed", "process dead letters".
  SKIP: diagnosing why messages failed (use queue-triage first); checking queue counts (use queue-status).
```

**deploy:**
```yaml
description: >
  Use when deploying a specific PR or commit to an environment programmatically or when chained by another skill.
  TRIGGER when: chained by workflow-deploy or another skill; user explicitly invokes /deploy with a ref.
  SKIP: interactive guided deployments (use workflow-deploy instead).
```

**workflow-deploy (new):**
```yaml
description: >
  Use when the user wants a guided, interactive deployment workflow with checkpoints at each destructive step.
  TRIGGER when: user asks "deploy PR #X", "guided deploy", "walk me through deploying",
  "deploy workflow", "interactive deploy", "deploy with checks", "step by step deploy",
  "deploy to prod", "ship PR".
  SKIP: non-interactive or chained deploys (use deploy directly).
```

## Design Decisions

| Decision | Rationale |
|---|---|
| Named `workflow-deploy`, not `deploy-guided` | Clearer intent — it's a complete workflow, not just a "guided" variant |
| Command + skill structure | Command is thin entry point; skill holds the logic (standard ops-suite pattern) |
| Checkpoints on all environments | The workflow is always interactive; safety gates (from v2) apply to non-guided flows |
| Questions upfront, not inline | Avoids interrupting execution mid-flight for predictable inputs |
| Wraps existing `deploy`, doesn't replace | Keeps the programmatic skill for chaining (e.g. `deploy-full` pipeline) |
| Migrations as optional checkpoint | User may know no migrations are needed; `auto-detect` is the safe default |
| `service-logs` model → haiku | Executes bash commands + formats output; no complex reasoning needed |

## Out of Scope (for now)

- Guided workflows for other ops skills (queue-reprocess, db-migrate standalone)
- Rollback wizard (generate plan but not execute interactively)
- Multi-service deploys
