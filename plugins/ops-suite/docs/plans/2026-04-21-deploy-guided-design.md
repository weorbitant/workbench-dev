# Deploy Guided — Interactive Deployment Wizard

**Date:** 2026-04-21
**Status:** Approved

## Problem

The existing `deploy` skill is linear and non-interactive. The user has no natural participation points during the deployment process — it either runs automatically or requires manual skill-chaining. There is no guided experience that collects context upfront and walks the user through each destructive step.

## Solution

A new `deploy-guided` skill that wraps the existing `deploy` skill with an interactive wizard layer. It does **not** replace `deploy` — the existing skill remains for programmatic/chained use. `deploy-guided` is the human-facing layer.

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
- If rollback plan requested: generate and display
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

Applies to **all environments** (dev, staging, prod). The wizard is always interactive.

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
commands/deploy-guided.md          ← slash command entry point
skills/deploy-guided/
  SKILL.md                         ← wizard logic
```

### Relationship to existing skills

```
deploy-guided
  ├── Wraps: deploy (pre-flight + trigger)
  ├── Chains: db-migrate (if migrations confirmed)
  └── Chains: service-status + service-logs (post-deploy)
```

`deploy-guided` inherits session state from `/tmp/ops-suite-session/` — does not re-read config or re-ask for already-known values.

## Design Decisions

| Decision | Rationale |
|---|---|
| Checkpoints on all environments | The wizard is always interactive; safety gates (from v2) apply to non-guided flows |
| Questions upfront, not inline | Avoids interrupting execution mid-flight for predictable inputs |
| Wraps existing `deploy`, doesn't replace | Keeps the programmatic skill for chaining (e.g. `deploy-full` pipeline) |
| Migrations as optional checkpoint | User may know no migrations are needed; `auto-detect` is the safe default |

## Out of Scope (for now)

- Guided workflows for other ops skills (queue-reprocess, db-migrate standalone)
- Rollback wizard (generate plan but not execute interactively)
- Multi-service deploys
