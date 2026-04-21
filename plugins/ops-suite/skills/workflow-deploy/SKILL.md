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

Note: `disable-model-invocation` is intentionally absent. Unlike the `deploy` skill (which is programmatic/chained only), this skill is designed to be auto-invoked by natural language triggers like "deploy PR #X". Every destructive operation is gated behind `AskUserQuestion`, so auto-invocation is safe.

## Phase A — Intake Form

Load configuration from `/tmp/ops-suite-session/config.json` (or `config.yaml` if not cached).
Extract `environments` list for question 2.
Extract `{service}` from config (the primary service name — used in Phase C/D for health checks and logs).

Ask these four questions one at a time using `AskUserQuestion`:

1. "What PR number or commit ref do you want to deploy?"
2. "Which environment? Available: {list from config}"
3. "Does this PR include DB migrations? (yes / no / auto-detect)"
4. "Generate a rollback plan before deploying? (yes / no)"

Store answers as: `{ref}`, `{env_name}`, `{migrations}`, `{rollback}`.

## Phase B — Pre-flight (read-only, no confirmation needed)

Load the CI adapter file at `../deploy/adapters/{deploy.ci_provider}.md` and extract:
- The commands to verify and trigger a deployment
- The rollback command (`{ci_rollback_command}`) — used if a rollback plan is requested

Then:

1. Verify `{ref}` is merged and extract the image tag
2. Get the currently deployed tag in `{env_name}` (what will change)
3. If `{migrations}` is `auto-detect`: check for pending migrations using the db-migrate adapter
4. If `{rollback}` is `yes`: generate rollback plan using `references/rollback-templates.md`
   — select the correct template based on whether migrations are included
   — fill `{ci_rollback_command}` with the value extracted from the CI adapter above

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
