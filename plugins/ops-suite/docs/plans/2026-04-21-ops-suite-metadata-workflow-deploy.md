# ops-suite: Skill Metadata + workflow-deploy Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Update all ops-suite SKILL.md files to follow the `creating-skills` metadata standard (TRIGGER when / SKIP / model), and create the `workflow-deploy` interactive deployment workflow.

**Architecture:** Two independent work blocks. Block A patches frontmatter in 9 existing SKILL.md files. Block B creates 3 new files: `skills/workflow-deploy/SKILL.md`, `skills/workflow-deploy/references/rollback-templates.md`, and `commands/workflow-deploy.md`.

**Tech Stack:** Markdown, YAML frontmatter. No runtime code — all changes are instruction files.

---

## Context

All files live under `plugins/ops-suite/` relative to the repo root.

The metadata standard (from `plugins/creating-skills/skills/creating-skills/SKILL.md`) requires:
- `description` field starting with "Use when..." and containing `TRIGGER when:` and `SKIP:` clauses
- `model` field set to the cheapest model that can handle the task:
  - `haiku` — mechanical steps, bash commands, output formatting
  - `sonnet` — analysis, reasoning, natural language to SQL/query, orchestration

The only model change is `service-logs`: `sonnet` → `haiku`.

---

## Block A — Update Existing Skill Metadata

### Task 1: Update `service-status` metadata

**Files:**
- Modify: `plugins/ops-suite/skills/service-status/SKILL.md`

**Step 1: Replace the description field**

Replace the current frontmatter description line:
```
description: Check service/container status, health, events, and resource usage across environments. Use when asked about "pods", "service status", "check services", "crashloop", "restart", "container health", "service down", "unhealthy".
```

With:
```
description: Check service/container status, health, events, and resource usage across environments. Use when asked about "pods", "service status", "check services", "crashloop", "restart", "container health", "service down", "unhealthy". TRIGGER when: user asks "is X running?", "check pods", "service down", "crashloop", "restart count", "container health", "deployment status", "how many pods?", "pod status". SKIP: log content analysis (use service-logs); database queries (use db-query); queue inspection (use queue-status).
```

**Step 2: Verify**

Read back the file and confirm the `description` field contains both `TRIGGER when:` and `SKIP:`. Confirm `model: haiku` is unchanged.

**Step 3: Commit**

```bash
git add plugins/ops-suite/skills/service-status/SKILL.md
git commit -m "docs(ops-suite): add TRIGGER when/SKIP to service-status"
```

---

### Task 2: Update `service-logs` metadata + model

**Files:**
- Modify: `plugins/ops-suite/skills/service-logs/SKILL.md`

**Step 1: Replace the description field AND the model field**

Replace:
```
description: Search and analyze logs from services and containers. Use when asked about "logs", "errors", "exceptions", "log search", "error messages", "stack trace", "application errors", "debug logs".
```
With:
```
description: Search and analyze logs from services and containers. Use when asked about "logs", "errors", "exceptions", "log search", "error messages", "stack trace", "application errors", "debug logs". TRIGGER when: user asks "any errors?", "check logs", "what's failing?", "show logs", "stack trace", "exceptions in X", "debug logs", "recent errors", "error messages". SKIP: pod health checks (use service-status); database queries (use db-query); queue failure analysis (use queue-triage).
```

Replace:
```
model: sonnet
```
With:
```
model: haiku
```

**Step 2: Verify**

Read back the file. Confirm `model: haiku` and that `description` contains `TRIGGER when:` and `SKIP:`.

**Step 3: Commit**

```bash
git add plugins/ops-suite/skills/service-logs/SKILL.md
git commit -m "docs(ops-suite): add TRIGGER when/SKIP to service-logs, downgrade model to haiku"
```

---

### Task 3: Update `db-query` metadata

**Files:**
- Modify: `plugins/ops-suite/skills/db-query/SKILL.md`

**Step 1: Replace the description field**

Replace:
```
description: Execute read-only queries against databases. Connects to the target environment's database, runs SQL queries, and formats results. Use when asked about "query database", "db query", "SQL", "check data", "database lookup", "count records", "find rows".
```
With:
```
description: Execute read-only queries against databases. Connects to the target environment's database, runs SQL queries, and formats results. Use when asked about "query database", "db query", "SQL", "check data", "database lookup", "count records", "find rows". TRIGGER when: user asks "query X table", "count records", "find rows where", "SQL query", "check the data", "how many X?", "look up Y in the database", "run a query". SKIP: running migrations (use db-migrate); service health checks (use service-status).
```

**Step 2: Verify**

Read back the file. Confirm `model: sonnet` is unchanged and `description` contains `TRIGGER when:` and `SKIP:`.

**Step 3: Commit**

```bash
git add plugins/ops-suite/skills/db-query/SKILL.md
git commit -m "docs(ops-suite): add TRIGGER when/SKIP to db-query"
```

---

### Task 4: Update `db-migrate` metadata

**Files:**
- Modify: `plugins/ops-suite/skills/db-migrate/SKILL.md`

**Step 1: Replace the description field**

Replace:
```
description: Run database migrations on remote environments. Identifies pending migrations, connects to the target database, runs the migration command, and verifies the result.
```
With:
```
description: Run database migrations on remote environments. Identifies pending migrations, connects to the target database, runs the migration command, and verifies the result. Use when asked about "run migrations", "apply migrations", "pending schema changes", "migration status", "update schema", "db migrate". TRIGGER when: user asks "run migrations", "apply migrations", "pending migrations", "migration status", "update schema", "schema migration", "check migrations", "are there pending migrations?". SKIP: querying data (use db-query); checking service health (use service-status).
```

**Step 2: Verify**

Read back the file. Confirm `model: haiku` is unchanged and `description` contains `TRIGGER when:` and `SKIP:`.

**Step 3: Commit**

```bash
git add plugins/ops-suite/skills/db-migrate/SKILL.md
git commit -m "docs(ops-suite): add trigger phrases and TRIGGER when/SKIP to db-migrate"
```

---

### Task 5: Update `queue-triage` metadata

**Files:**
- Modify: `plugins/ops-suite/skills/queue-triage/SKILL.md`

**Step 1: Replace the description field**

Replace:
```
description: Diagnose why messages are failing in dead letter queues. Surveys DLQs, fetches sample messages, analyzes failure patterns, inspects consumer code, and produces a root cause report. Use when asked about "DLQ triage", "dead letter diagnosis", "failed messages", "message failures", "queue errors".
```
With:
```
description: Diagnose why messages are failing in dead letter queues. Surveys DLQs, fetches sample messages, analyzes failure patterns, inspects consumer code, and produces a root cause report. Use when asked about "DLQ triage", "dead letter diagnosis", "failed messages", "message failures", "queue errors". TRIGGER when: user asks "why are messages failing?", "triage DLQ", "dead letter queue has messages", "failed messages", "diagnose queue errors", "DLQ analysis", "what's wrong with the queue?". SKIP: moving messages back (use queue-reprocess); general queue counts (use queue-status).
```

**Step 2: Verify**

Read back the file. Confirm `model: sonnet` is unchanged.

**Step 3: Commit**

```bash
git add plugins/ops-suite/skills/queue-triage/SKILL.md
git commit -m "docs(ops-suite): add TRIGGER when/SKIP to queue-triage"
```

---

### Task 6: Update `queue-reprocess` metadata

**Files:**
- Modify: `plugins/ops-suite/skills/queue-reprocess/SKILL.md`

**Step 1: Replace the description field**

Replace:
```
description: Move failed messages from dead letter queues back to their main queue for reprocessing. Creates a shovel or uses the Management API to move messages. Always recommends triaging first.
```
With:
```
description: Move failed messages from dead letter queues back to their main queue for reprocessing. Creates a shovel or uses the Management API to move messages. Always recommends triaging first. TRIGGER when: user asks "reprocess DLQ", "move messages back", "retry failed messages", "shovel messages", "republish DLQ", "requeue failed", "process dead letters", "move DLQ to main queue". SKIP: diagnosing why messages failed (use queue-triage first); checking queue counts (use queue-status).
```

**Step 2: Verify**

Read back the file. Confirm `model: haiku` and `disable-model-invocation: true` are unchanged.

**Step 3: Commit**

```bash
git add plugins/ops-suite/skills/queue-reprocess/SKILL.md
git commit -m "docs(ops-suite): add trigger phrases and TRIGGER when/SKIP to queue-reprocess"
```

---

### Task 7: Update `queue-status` metadata

**Files:**
- Modify: `plugins/ops-suite/skills/queue-status/SKILL.md`

**Step 1: Replace the description field**

Replace:
```
description: Check message queue status, list queues, monitor DLQ counts and consumers. Use when asked about "queues", "queue status", "DLQ", "dead letter", "consumers", "messages pending", "message broker", "rabbitmq", "queue health".
```
With:
```
description: Check message queue status, list queues, monitor DLQ counts and consumers. Use when asked about "queues", "queue status", "DLQ", "dead letter", "consumers", "messages pending", "message broker", "rabbitmq", "queue health". TRIGGER when: user asks "how are the queues?", "queue status", "any DLQ messages?", "check queues", "messages pending", "consumer count", "queue health", "rabbitmq status", "are there messages in the DLQ?". SKIP: diagnosing DLQ failures (use queue-triage); moving messages back (use queue-reprocess).
```

**Step 2: Verify**

Read back the file. Confirm `model: haiku` is unchanged.

**Step 3: Commit**

```bash
git add plugins/ops-suite/skills/queue-status/SKILL.md
git commit -m "docs(ops-suite): add TRIGGER when/SKIP to queue-status"
```

---

### Task 8: Update `port-forward` metadata

**Files:**
- Modify: `plugins/ops-suite/skills/port-forward/SKILL.md`

**Step 1: Replace the description field**

Replace:
```
description: Establish local connections to cluster services like databases, brokers, and APIs. Use when asked about "port-forward", "connect to database", "local connection", "tunnel", "forward port", "access service locally".
```
With:
```
description: Establish local connections to cluster services like databases, brokers, and APIs. Use when asked about "port-forward", "connect to database", "local connection", "tunnel", "forward port", "access service locally". TRIGGER when: user asks "port-forward to X", "connect to database locally", "tunnel to service", "forward port", "access service locally", "open local connection to X". SKIP: checking service health (use service-status); running queries (use db-query).
```

**Step 2: Verify**

Read back the file. Confirm `model: haiku` is unchanged.

**Step 3: Commit**

```bash
git add plugins/ops-suite/skills/port-forward/SKILL.md
git commit -m "docs(ops-suite): add TRIGGER when/SKIP to port-forward"
```

---

### Task 9: Update `deploy` metadata

**Files:**
- Modify: `plugins/ops-suite/skills/deploy/SKILL.md`

**Step 1: Replace the description field**

Replace:
```
description: Deploy a merged change to an environment. Verifies the change is merged, finds the build artifact, confirms with the user, triggers the deployment, and verifies the result.
```
With:
```
description: Deploy a merged change to an environment. Verifies the change is merged, finds the build artifact, confirms with the user, triggers the deployment, and verifies the result. TRIGGER when: chained by workflow-deploy or another skill; user explicitly invokes /deploy with a specific PR number, commit SHA, or ref. SKIP: interactive guided deployments (use workflow-deploy instead — it wraps this skill with an intake form and checkpoints).
```

**Step 2: Verify**

Read back the file. Confirm `model: sonnet` and `disable-model-invocation: true` are unchanged.

**Step 3: Commit**

```bash
git add plugins/ops-suite/skills/deploy/SKILL.md
git commit -m "docs(ops-suite): add TRIGGER when/SKIP to deploy, point interactive use to workflow-deploy"
```

---

## Block B — Create `workflow-deploy`

### Task 10: Create `references/rollback-templates.md`

**Files:**
- Create: `plugins/ops-suite/skills/workflow-deploy/references/rollback-templates.md`

**Step 1: Create the file**

```markdown
# Rollback Templates

Used by workflow-deploy to generate a rollback plan before deployment.
Select the template that matches the deployment type and fill in the values.

## Template: Code-only (no migrations)

```
Rollback Plan
─────────────────────────────────────────────
  If deploy fails or service is unhealthy:

  1. Trigger rollback via CI:
     Previous image tag: {current_tag}
     Run: {ci_rollback_command from adapter}

  2. Verify health:
     /ops-suite:service-status {service} {env_name}

  3. Check logs are clean:
     /ops-suite:service-logs {service} {env_name}
```

## Template: Includes database migrations

```
Rollback Plan
─────────────────────────────────────────────
  ⚠️  This deployment includes database migrations.
  Rollback requires two steps: code + migrations.

  CASE A — Deploy fails BEFORE migrations run:
    1. Trigger rollback via CI (previous tag: {current_tag}).
    No migration rollback needed.

  CASE B — Deploy fails AFTER migrations run:
    1. Roll back code:
       Trigger rollback via CI (previous tag: {current_tag}).
    2. Roll back migrations (CAUTION — may affect data):
       /ops-suite:db-migrate {env_name}  → select rollback option
    3. Verify: /ops-suite:service-status {service} {env_name}
    4. Logs:   /ops-suite:service-logs {service} {env_name}

  ⚠️  If migrations created new columns with data already written,
      rolling back may cause data loss. Confirm with team first.
```

## Template: Not requested

```
No rollback plan generated (not requested).
To generate one, run /ops-suite:workflow-deploy again and answer "yes" to rollback plan.
```
```

**Step 2: Verify**

Read back the file. Confirm it has 3 templates: code-only, migrations, not-requested.

---

### Task 11: Create `skills/workflow-deploy/SKILL.md`

**Files:**
- Create: `plugins/ops-suite/skills/workflow-deploy/SKILL.md`

**Step 1: Create the file**

```markdown
---
name: workflow-deploy
description: Interactive deployment workflow with guided intake form and checkpoints at each destructive step. Use when the user wants to deploy a PR or commit with a step-by-step guided experience. TRIGGER when: user asks "deploy PR #X", "guided deploy", "walk me through deploying", "deploy workflow", "interactive deploy", "deploy with checks", "step by step deploy", "deploy to prod", "ship PR", "release PR #X". SKIP: non-interactive or chained deploys (use deploy directly).
argument-hint: ""
allowed-tools:
  - Bash
  - AskUserQuestion
  - Read
model: sonnet
---

## Overview

Interactive deployment workflow: collect all inputs upfront via intake form, then execute with explicit checkpoints before each destructive operation. Checkpoints apply to **all environments** (dev, staging, prod) — this workflow is always interactive.

## Phase A — Intake Form

Load configuration from `/tmp/ops-suite-session/config.json` (or `config.yaml` if not cached).
Extract `environments` list for question 2.

Ask these four questions one at a time using `AskUserQuestion`:

1. "What PR number or commit ref do you want to deploy?"
2. "Which environment? Available: {list from config}"
3. "Does this PR include DB migrations? (yes / no / auto-detect)"
4. "Generate a rollback plan before deploying? (yes / no)"

Store answers as: `{ref}`, `{env_name}`, `{migrations}`, `{rollback}`.

## Phase B — Pre-flight (read-only, no confirmation needed)

Using the CI adapter from the deploy skill (`adapters/{deploy.ci_provider}.md`):

1. Verify `{ref}` is merged and extract the image tag
2. Get the currently deployed tag in `{env_name}` (what will change)
3. If `{migrations}` is `auto-detect`: check for pending migrations using the db-migrate adapter
4. If `{rollback}` is `yes`: generate rollback plan using `references/rollback-templates.md`
   — select the correct template based on whether migrations are included

Display the deployment plan summary:

```
Deployment Plan
───────────────────────────────────────────────
  Change:      {ref} — {pr_title}
  Image tag:   {image_tag}
  Environment: {env_name}
  Current tag: {current_tag}
  Migrations:  {N pending / none}
  Rollback:    {shown above / not requested}
```

## Checkpoint 1 — Confirm deploy

Ask using `AskUserQuestion`:

```
🚀 Ready to deploy to {env_name}.
  Change: {ref} — {pr_title}
  From:   {current_tag}  →  {image_tag}
  Migrations: {N pending / none}

Proceed? (yes / no)
```

If no → stop. Tell the user: "Deployment cancelled. No changes were made."

## Phase C — Deploy

Trigger deployment using the CI adapter (same commands as deploy skill Step 7).
Show progress as the CI run proceeds.

On failure:
- Stop immediately
- Show last 20 lines of CI output
- Say: "Deployment failed at the CI step. Run /ops-suite:service-logs {service} {env_name} to investigate."
- If rollback plan was generated, display it now

## Checkpoint 2 — Confirm migrations

Show only if migrations exist (detected in Phase B or user answered "yes" in intake).

Ask using `AskUserQuestion`:

```
⚠️  {N} pending migration(s) detected.
  Run migrations now? (yes / no / show them first)
```

If "show them first": list migration file names from the db-migrate adapter, then ask again.
If no → warn: "Migrations skipped. Service may be unstable. Run /ops-suite:db-migrate {env_name} when ready."
If yes → use ops-suite:db-migrate with arguments: {env_name}. Use session state from `/tmp/ops-suite-session/` — do not re-ask for environment or credentials.

## Phase D — Post-deploy verification (automatic, no confirmation)

Run these automatically after deploy (and after migrations if applied). Do not ask.

1. Use ops-suite:service-status with arguments: {service} {env_name}.
   Use session state — do not re-ask for environment.

2. Use ops-suite:service-logs with arguments: {service} {env_name}.
   Use session state — do not re-ask for environment.
   Focus on last 5 minutes of logs.

## Final Report

```
── Deployment Summary ──────────────────────────────
  PR:          {ref} — {pr_title}
  Environment: {env_name}
  Image tag:   {image_tag}
  Duration:    {duration}

  [✓/✗] Deploy:      {N/N pods running / failed}
  [✓/✗/–] Migrations: {N applied / skipped / none needed}
  [✓/✗] Health:      {healthy / degraded}
  [✓/✗] Logs:        {no errors / N errors found}

  Overall: SUCCESS / SUCCESS WITH WARNINGS / FAILED at {phase}
────────────────────────────────────────────────────
```

If errors found in logs, add relevant suggestions:
- DB errors → `→ Run /ops-suite:db-migrate {env_name}` if migrations were skipped
- Message processing errors → `→ Run /ops-suite:queue-triage {env_name}`
```

**Step 2: Verify**

Read back the file. Confirm:
- `model: sonnet`
- `description` contains `TRIGGER when:` and `SKIP:`
- Phases A → B → Checkpoint 1 → C → Checkpoint 2 → D → Report are all present

---

### Task 12: Create `commands/workflow-deploy.md`

**Files:**
- Create: `plugins/ops-suite/commands/workflow-deploy.md`

**Step 1: Create the file**

```markdown
---
description: "Interactive deployment workflow: guided intake → pre-flight → deploy → migrations → verification."
---

Invoke the ops-suite:workflow-deploy skill and follow it exactly as presented to you.
```

**Step 2: Verify**

Read back the file. Confirm it has a `description` frontmatter field and the invoke instruction.

**Step 3: Commit Block B**

```bash
git add plugins/ops-suite/skills/workflow-deploy/ plugins/ops-suite/commands/workflow-deploy.md
git commit -m "feat(ops-suite): add workflow-deploy interactive deployment workflow"
```

---

## Verification Checklist

After all tasks are complete, verify:

- [ ] All 9 SKILL.md files have `TRIGGER when:` in their `description` field
- [ ] All 9 SKILL.md files have `SKIP:` in their `description` field
- [ ] `service-logs` uses `model: haiku`
- [ ] `deploy` still has `disable-model-invocation: true`
- [ ] `queue-reprocess` still has `disable-model-invocation: true`
- [ ] `skills/workflow-deploy/SKILL.md` exists with all 6 phases
- [ ] `skills/workflow-deploy/references/rollback-templates.md` exists with 3 templates
- [ ] `commands/workflow-deploy.md` exists

```bash
# Quick sanity check
grep -l "TRIGGER when" plugins/ops-suite/skills/*/SKILL.md | wc -l
# Expected: 9
```
