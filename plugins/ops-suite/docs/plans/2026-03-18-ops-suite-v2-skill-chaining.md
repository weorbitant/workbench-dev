# Ops-Suite v2: Skill Chaining & Auto-Invocation

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform ops-suite from isolated skills into a composable pipeline system where skills call each other, auto-invoke without manual `/` triggers, and dangerous operations gate on environment (dev=auto, prod=confirm).

**Architecture:** Introduce a shared `runtime/` layer with connection pooling, environment safety gates, and a chaining mechanism that lets one skill invoke another mid-execution. Replace `disable-model-invocation` with per-environment safety policies.

**Tech Stack:** Markdown skill definitions, bash hooks, YAML config

---

## Context: What Went Wrong This Session

During a real incident on `mp-service-obligations-api` in dev, we ran 6 skills manually in sequence:

```
service-logs → found 2 errors (missing table + missing column)
service-status → confirmed pods healthy, no restarts
db-migrate → applied 4 pending migrations (fixed root cause)
service-logs → confirmed 0 errors post-migration
db-query → checked assignment table (empty, expected)
queue-triage → found 3 DLQs with 390K+ messages
queue-reprocess → purged 1, shoveled 390K back
```

**Problems observed:**

1. **Every skill re-loaded config.yaml** — 6 times for the same file
2. **Every skill re-established connections** — port-forward created/killed 3 times
3. **Skills couldn't call each other** — deploy suggests "run db-migrate" but can't invoke it
4. **Manual invocation only** — had to `/ops-suite:service-logs` each time instead of the model detecting "user wants logs"
5. **`disable-model-invocation` is binary** — blocks auto-invoke entirely instead of gating on environment
6. **No pipeline concept** — deploy should auto-chain: deploy → migrate → verify-health → check-logs
7. **Credentials fetched repeatedly** — RabbitMQ and DB passwords retrieved multiple times
8. **No shared connection state** — port-forward killed between skills, then recreated

---

## Improvement Areas

### A. Skill Chaining
### B. Smart Auto-Invocation (replace disable-model-invocation)
### C. Deterministic Pipelines (deploy, incident-triage)
### D. Shared Runtime (connections, credentials, config)

---

## Task 1: Shared Runtime — Connection & Config Cache

**Goal:** Skills share config, connections, and credentials within a session instead of re-loading each time.

**Files:**
- Create: `runtime/README.md`
- Create: `runtime/session-state.md`
- Modify: every `SKILL.md` Step 0

### Step 1: Design the session state format

Create `runtime/session-state.md` — a reference document that skills include to manage shared state via `/tmp/ops-suite-session/`.

```markdown
# Session State Management

Skills share state through files in `/tmp/ops-suite-session/`.

## State files

| File | Content | Written by | Read by |
|------|---------|-----------|---------|
| `config.json` | Parsed config.yaml as JSON | First skill to run | All skills |
| `env.json` | Selected environment + resolved config | Any skill that selects env | All skills |
| `credentials.json` | Retrieved credentials (DB, broker) | port-forward, db-migrate, db-query | All DB/broker skills |
| `port-forwards.json` | Active port-forwards `{service: {pid, localPort}}` | port-forward, any skill that creates one | All skills |
| `last-triage.json` | Last queue-triage results | queue-triage | queue-reprocess |

## Lifecycle

- Created by `session-start.sh` hook (mkdir + parse config)
- Cleaned up when session ends or user runs `/ops-suite:cleanup`
- Skills check for existing state before creating new connections

## Port-forward reuse

Before creating a port-forward, check `port-forwards.json`:
1. If entry exists for the service, check if PID is still alive (`kill -0 $PID`)
2. If alive, reuse the existing port
3. If dead, remove entry and create new

## Credential caching

Credentials are cached in `credentials.json` for the session:
- Key: `{env_name}:{service}` (e.g., `dev:database`, `dev:broker`)
- Value: `{user, password}` (never logged or displayed)
- Skills check cache before running kubectl get secret
```

### Step 2: Create session-start.sh improvements

Modify `hooks/session-start.sh` to initialize the session state directory and parse config.yaml into JSON.

### Step 3: Update every SKILL.md Step 0

Replace the current "Read config.yaml" with:

```markdown
## Step 0 — Load configuration

Check if `/tmp/ops-suite-session/config.json` exists.
If yes, read it (pre-parsed by session hook).
If no, read the plugin's `config.yaml` and cache it to `/tmp/ops-suite-session/config.json`.
```

### Step 4: Commit

```bash
git add runtime/ hooks/
git commit -m "feat(runtime): add shared session state for config, connections, and credentials"
```

---

## Task 2: Skill Chaining Mechanism

**Goal:** Skills can invoke other skills mid-execution using `ops-suite:<skill-name>` references, following the same convention as the superpowers plugin.

**Files:**
- Create: `runtime/chaining.md`
- Modify: `skills/deploy/SKILL.md`
- Modify: `skills/queue-triage/SKILL.md`
- Modify: `skills/queue-reprocess/SKILL.md`

### Step 1: Design the chaining reference

Create `runtime/chaining.md`:

```markdown
# Skill Chaining

Skills can invoke other skills by referencing them with the `ops-suite:<skill-name>` convention.

## Syntax

In any SKILL.md step, use one of these patterns:

### Direct action (invoke immediately)
```
Use ops-suite:db-migrate with arguments: {env_name}.
Use session state from /tmp/ops-suite-session/ — do not re-ask for environment or re-load config.
After completing that skill, return here and continue with the next step.
```

### Required sub-skill (must complete before continuing)
```
**REQUIRED SUB-SKILL:** Use ops-suite:service-status to verify health before proceeding.
```

### Conditional chain (invoke only if condition is met)
```
If errors suggest database issues, use ops-suite:db-query to check entity state.
```

## Chaining rules

1. The chained skill inherits session state (config, env, connections from `/tmp/ops-suite-session/`)
2. The chained skill does NOT re-ask for environment if already selected
3. The chained skill respects the same safety gates as if invoked directly
4. Chain depth is max 3 (prevent infinite loops)
5. If a chained skill fails, the calling skill must handle the failure (stop or warn)

## Common chains

| From | To | When |
|------|-----|------|
| deploy | db-migrate | After deployment if migration_tool != "none" |
| deploy | service-status | After deployment to verify health |
| deploy | service-logs | After deployment to check for errors |
| queue-triage | service-logs | To find consumer errors |
| queue-triage | service-status | To check if consumer is running |
| queue-triage | db-query | To verify entity state in database |
| queue-reprocess | queue-triage | Pre-flight: ensure triage was done |
| service-status | service-logs | When unhealthy pod found |
```

### Step 2: Update deploy SKILL.md to chain

Replace Step 7-8 with:

```markdown
## Step 7 — Post-deploy verification pipeline

Run the following skills in sequence. Each skill inherits session state — do not re-ask for environment or re-load config.

1. **REQUIRED SUB-SKILL:** Use ops-suite:service-status with arguments: {service} {env_name}.
   - If unhealthy → abort and report
2. Use ops-suite:service-logs with arguments: {service} {env_name}.
   - Check for errors in last 5 minutes
   - If errors found → report but continue
3. If `deploy.migration_tool` != "none":
   Use ops-suite:db-migrate with arguments: {env_name}.
4. Use ops-suite:service-logs with arguments: {service} {env_name}.
   - Final error check after migrations
```

### Step 3: Update queue-reprocess to chain triage

Replace Step 3 (pre-flight) with:

```markdown
## Step 3 — Pre-flight: auto-triage

Check `/tmp/ops-suite-session/last-triage.json`.

If it exists and is less than 10 minutes old for the same DLQ:
- Skip triage, use cached results
- Show: "Using triage from {minutes} ago: {summary}"

If it does not exist or is stale:
- **REQUIRED SUB-SKILL:** Use ops-suite:queue-triage with arguments: {queue_name} {env_name}.
- Results are cached automatically in `/tmp/ops-suite-session/last-triage.json`
```

### Step 4: Update queue-triage to chain service-logs and db-query

Replace Step 8 (check consumer logs) with:

```markdown
## Step 8 — Check consumer context

1. Use ops-suite:service-logs with arguments: {consumer_service} {env_name}.
   - Focus on errors related to the DLQ entities
2. If failure mode is "entity not found" or "database issue":
   Use ops-suite:db-query with arguments: {env_name}.
   - Formulate a query to check if the affected entity exists
```

### Step 5: Commit

```bash
git add runtime/chaining.md skills/
git commit -m "feat(chaining): add ops-suite:<name> convention for skill-to-skill invocation"
```

---

## Task 3: Environment-Aware Safety Gates (Replace disable-model-invocation)

**Goal:** Replace the binary `disable-model-invocation` flag with environment-aware safety. Dev = auto-execute, Prod = always confirm.

**Files:**
- Create: `runtime/safety.md`
- Modify: `config.yaml` and `config.example.yaml`
- Modify: `skills/deploy/SKILL.md`
- Modify: `skills/db-migrate/SKILL.md`
- Modify: `skills/queue-reprocess/SKILL.md`
- Modify: all command `.md` files in `commands/`

### Step 1: Add safety policy to config

Add to `config.yaml`:

```yaml
safety:
  # Per-environment safety level
  # auto: execute without confirmation (dev, staging)
  # confirm: always ask before destructive operations (prod)
  # locked: refuse destructive operations entirely
  environments:
    dev: auto
    prod: confirm

  # Operations that are always gated regardless of environment
  always_confirm:
    - purge_queue
    - rollback_migration
    - force_push
```

### Step 2: Create safety reference

Create `runtime/safety.md`:

```markdown
# Safety Gates

## Environment Safety Levels

| Level | Behavior | Use for |
|-------|----------|---------|
| `auto` | Execute without confirmation | dev, staging |
| `confirm` | Ask user before destructive ops | prod |
| `locked` | Refuse destructive ops entirely | shared-prod, financial |

## What counts as destructive

| Operation | Destructive? | Gate |
|-----------|-------------|------|
| Read logs | No | Never gated |
| Check status | No | Never gated |
| Run SELECT query | No | Never gated |
| Port-forward | No | Never gated |
| Run migrations | Yes | Environment gate |
| Deploy | Yes | Environment gate |
| Reprocess DLQ | Yes | Environment gate |
| Purge DLQ | Yes | Always confirm |
| Write query (UPDATE/DELETE) | Yes | Always confirm |
| Rollback migration | Yes | Always confirm |

## How to use in SKILL.md

Before any destructive operation, check the safety level:

1. Read safety policy from session state
2. If `auto` → proceed, log the action
3. If `confirm` → show confirmation prompt, wait for user
4. If `locked` → refuse and explain why

Format for confirmation prompts:
```
[PROD] This will {action_description}.
  Target: {resource}
  Impact: {what_changes}
  Proceed? (yes/no)
```

The `[PROD]` prefix makes it visually clear this is a production operation.
```

### Step 3: Remove disable-model-invocation from skills

Modify all three SKILL.md files (deploy, db-migrate, queue-reprocess):
- Remove `disable-model-invocation: true` from frontmatter
- Add safety gate step before destructive operations

Modify all command `.md` files:
- Remove `disable-model-invocation: true` from commands/deploy.md, commands/db-migrate.md, commands/queue-reprocess.md

### Step 4: Commit

```bash
git add runtime/safety.md config.yaml config.example.yaml skills/ commands/
git commit -m "feat(safety): replace disable-model-invocation with environment-aware safety gates"
```

---

## Task 4: Deterministic Pipelines

**Goal:** Create composite skills that orchestrate multiple skills in a deterministic sequence.

**Files:**
- Create: `skills/deploy-full/SKILL.md`
- Create: `skills/incident-triage/SKILL.md`
- Create: `commands/deploy-full.md`
- Create: `commands/incident-triage.md`

### Step 1: Create deploy-full pipeline skill

Create `skills/deploy-full/SKILL.md`:

```markdown
---
name: deploy-full
description: Full deployment pipeline — deploy, migrate, verify health, check logs. Use when deploying changes that include database migrations or when you want a complete verified deployment.
argument-hint: "[PR-number] [environment]"
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
model: sonnet
---

## Overview

This is a pipeline skill that chains multiple skills in sequence.
Each step must pass before the next one runs. If any step fails,
the pipeline stops and reports the failure point.

## Pipeline Steps

### Step 1 — Deploy
**REQUIRED SUB-SKILL:** Use ops-suite:deploy with arguments: {pr_number} {env_name}.

If deployment fails → STOP. Report failure.

### Step 2 — Run migrations
Use ops-suite:db-migrate with arguments: {env_name}.

If no pending migrations → skip with "No migrations needed".
If migration fails → STOP. Report failure. Suggest rollback.

### Step 3 — Verify health
Use ops-suite:service-status with arguments: {service} {env_name}.

Wait 30 seconds after migration for pods to stabilize.
If unhealthy → STOP. Report failure. Suggest rollback.

### Step 4 — Check logs
Use ops-suite:service-logs with arguments: {service} {env_name}.

Check last 5 minutes of logs for errors.
If errors found → WARN but do not stop (may be transient).

### Step 5 — Check DLQs
Use ops-suite:queue-status with arguments: {env_name}.

Check if any DLQs for this service gained new messages since deployment.
If new DLQ messages → WARN and suggest ops-suite:queue-triage.

### Step 6 — Report

```
Deployment Pipeline Summary:
  PR:          #{pr_number}
  Environment: {env_name}

  [PASS] Deploy:     image {tag} rolled out
  [PASS] Migrate:    {n} migrations applied / skipped
  [PASS] Health:     {replicas}/{replicas} pods running
  [WARN] Logs:       {n} errors found (or "clean")
  [PASS] Queues:     no new DLQ messages (or "{n} new")

  Overall: SUCCESS / SUCCESS WITH WARNINGS / FAILED at step {n}
```
```

### Step 2: Create incident-triage pipeline skill

Create `skills/incident-triage/SKILL.md`:

```markdown
---
name: incident-triage
description: Full incident triage pipeline — check status, logs, queues, database. Use when something is broken and you need to understand what is happening across the stack.
argument-hint: "[service-name] [environment]"
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
model: sonnet
---

## Overview

Automated incident triage that checks all layers of the stack
and produces a consolidated report.

## Pipeline Steps

### Step 1 — Service health
Use ops-suite:service-status with arguments: {service} {env_name}.

Capture: pod states, restart counts, resource usage.

### Step 2 — Recent errors
Use ops-suite:service-logs with arguments: {service} {env_name}.

Capture: error count, error types, frequency pattern.

### Step 3 — Queue health
Use ops-suite:queue-status with arguments: {env_name}.

Capture: DLQ message counts for this service.

### Step 4 — DLQ triage (if DLQs have messages)
For each DLQ with messages > 0 for this service:
Use ops-suite:queue-triage with arguments: {dlq_name} {env_name}.

Capture: failure mode, root cause, sample messages.

### Step 5 — Database check (if errors suggest DB issues)
If error patterns include "does not exist", "connection refused", "timeout":
Use ops-suite:db-query with arguments: {env_name}.

Run: table existence check, migration status, connection test.

### Step 6 — Consolidated report

```
Incident Triage Report
======================
Service:     {service}
Environment: {env_name}
Timestamp:   {now}

Layer Status:
  Pods:      {healthy/degraded/down} ({details})
  Errors:    {count} in last {duration} ({trend})
  Queues:    {n} DLQs with messages ({total} msgs)
  Database:  {connected/issues} ({details})

Root Cause Analysis:
  Most likely: {description based on evidence}

  Evidence:
    1. {evidence from logs}
    2. {evidence from queues}
    3. {evidence from DB}

Recommended Actions:
  1. {highest priority action}
  2. {second action}
  3. {third action}
```
```

### Step 3: Create command files

Create `commands/deploy-full.md`:
```markdown
---
description: "Full deployment pipeline: deploy → migrate → verify → check logs & queues."
---

Invoke the ops-suite:deploy-full skill and follow it exactly as presented to you
```

Create `commands/incident-triage.md`:
```markdown
---
description: "Full incident triage: status → logs → queues → DLQ analysis → DB check."
---

Invoke the ops-suite:incident-triage skill and follow it exactly as presented to you
```

### Step 4: Commit

```bash
git add skills/deploy-full/ skills/incident-triage/ commands/
git commit -m "feat(pipelines): add deploy-full and incident-triage composite skills"
```

---

## Task 5: Auto-Invocation — Model Detects Intent

**Goal:** The model should invoke ops-suite skills automatically when the user's intent matches, without needing `/ops-suite:xxx`. The SessionStart hook should instruct the model to do this.

**Files:**
- Modify: `hooks/session-start.sh`
- Modify: `hooks/hooks.json`

### Step 1: Enhance session-start hook output

The `additionalContext` should include intent-matching rules, not just a skill table:

```markdown
## ops-suite — Auto-Invocation Rules

When the user's message matches these patterns, invoke the corresponding skill
automatically via the Skill tool. Do NOT ask "should I run X?" — just run it.
Destructive operations are gated by environment safety policy, not by invocation.

| User Intent | Invoke | Example triggers |
|-------------|--------|------------------|
| Check if service is working | ops-suite:service-status | "is X running?", "check pods", "how's the service?" |
| See what errors are happening | ops-suite:service-logs | "any errors?", "what's failing?", "check logs" |
| Run database queries | ops-suite:db-query | "query X", "how many Y?", "check the data" |
| Check queue health | ops-suite:queue-status | "how are the queues?", "any DLQ messages?" |
| Diagnose DLQ failures | ops-suite:queue-triage | "why are messages failing?", "triage DLQ" |
| Reprocess failed messages | ops-suite:queue-reprocess | "reprocess DLQ", "move messages back" |
| Deploy a change | ops-suite:deploy-full | "deploy PR #X", "push to prod" |
| Run migrations | ops-suite:db-migrate | "run migrations", "update schema" |
| Something is broken | ops-suite:incident-triage | "X is broken", "500 errors", "service down" |
| Connect to a service | ops-suite:port-forward | "connect to DB", "port-forward" |

### Chaining: if a skill's output suggests another skill, invoke it automatically.
Example: service-logs finds "table does not exist" → offer db-migrate.
```

### Step 2: Commit

```bash
git add hooks/
git commit -m "feat(auto-invoke): add intent-matching rules to session-start hook"
```

---

## Task 6: Update Config for PgBouncer Namespace Fix

**Goal:** Fix the PgBouncer namespace discovered during this session (it's in `plataformadato`, not `shared-infra`).

**Files:**
- Modify: `config.yaml`
- Modify: `config.example.yaml`

### Step 1: Add per-service namespace override

The current config assumes all infra is in `env.namespaces.infra`. But PgBouncer was in the apps namespace. Add support:

```yaml
environments:
  dev:
    context: "dev"
    namespaces:
      apps: "plataformadato"
      infra: "shared-infra"
    services:
      broker:
        name: "dev-test-afianza-rabbit-ha"  # Fixed: actual pod prefix
        namespace: "shared-infra"            # NEW: explicit namespace per service
        management_port: 15672
        amqp_port: 5672
        vhost: "data_platform"
        pod_pattern: "dev-test-afianza-rabbit-ha-*"  # Fixed: actual pattern
        credentials:                         # NEW: where to find credentials
          secret_name: "dev-test-afianza-rabbit-ha-secret"
          secret_namespace: "shared-infra"
          user_key: "afianza-username"
          password_key: "afianza-password"
      database:
        name: "pd-infra-pgbouncer"
        namespace: "plataformadato"          # NEW: override — NOT in shared-infra
        port: 6432
        default_db: "mp-service-obligations-api-dev"
        credentials:
          secret_name: "mp-service-obligations-api-secrets"
          secret_namespace: "plataformadato"
          user_key: ~                        # hardcoded: postgres
          password_key: "POSTGRES_PASSWORD"
          default_user: "postgres"
```

### Step 2: Update all adapters to use `{service.namespace}` fallback

In every adapter that uses `{env.namespaces.infra}`, change to:
```
{service.namespace || env.namespaces.infra}
```

### Step 3: Commit

```bash
git add config.yaml config.example.yaml
git commit -m "fix(config): add per-service namespace and credential references"
```

---

## Summary: What Changes

| Before (v1) | After (v2) |
|---|---|
| Skills are isolated, user chains manually | Skills chain via `ops-suite:<name>` references |
| `disable-model-invocation` blocks auto-invoke | Environment safety gates (dev=auto, prod=confirm) |
| Deploy suggests "run migrations" | `deploy-full` pipeline auto-chains deploy→migrate→verify |
| No incident workflow | `incident-triage` auto-chains status→logs→queues→DB |
| Config re-read 6 times per session | Session state cached in `/tmp/ops-suite-session/` |
| Port-forwards created/killed repeatedly | Port-forward pool shared across skills |
| Credentials fetched repeatedly | Credential cache per session |
| PgBouncer namespace hardcoded wrong | Per-service namespace override |
| RabbitMQ credentials trial-and-error | Credential source in config |

## Dependency Graph

```
Task 1 (Session State) ← foundation for everything
  ↓
Task 2 (Chaining) ← depends on shared state
  ↓
Task 3 (Safety Gates) ← depends on chaining model
  ↓
Task 4 (Pipelines) ← depends on chaining + safety
  ↓
Task 5 (Auto-Invocation) ← depends on safety gates

Task 6 (Config Fix) ← independent, can be done anytime
```
