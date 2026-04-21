---
name: deploy
description: Deploy a merged change to an environment. Verifies the change is merged, finds the build artifact, confirms with the user, triggers the deployment, and verifies the result. TRIGGER when: chained by workflow-deploy or another skill; user explicitly invokes /deploy with a specific PR number, commit SHA, or ref. SKIP: interactive guided deployments (use workflow-deploy instead — it wraps this skill with an intake form and checkpoints).
argument-hint: "[PR-number or ref] [environment]"
disable-model-invocation: true
allowed-tools:
  - Bash
  - AskUserQuestion
model: sonnet
---

## Step 0 — Load configuration

Check if `/tmp/ops-suite-session/config.json` exists:
- If yes, read it (pre-parsed by session-start hook).
- If no, read the plugin's `config.yaml`, parse it, and write to `/tmp/ops-suite-session/config.json` for other skills to reuse.
If neither exists, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `deploy.ci_provider` — determines which adapter to load
- `deploy.image_tag_source` — how to find the image tag (run-id, commit-sha, tag)
- `deploy.migration_tool` — whether migrations need to run
- `environments` — available environments

Also read the reference at `references/commands.md` (in this skill's directory) for the step-by-step process.

## Step 1 — Load adapter

Read the adapter file at `adapters/{deploy.ci_provider}.md` (in this skill's directory).
If the adapter does not exist, tell the user that the CI provider `{deploy.ci_provider}` is not yet supported and stop.

## Step 2 — Identify the change to deploy

If `$ARGUMENTS` contains a PR number:
- Use the adapter to check the PR state (must be merged)
- Extract the merge commit SHA

If `$ARGUMENTS` contains a commit SHA or branch ref:
- Verify it exists and is reachable from the main branch

If nothing is provided, ask the user for a PR number or ref.

## Step 3 — Determine target environment

If `$ARGUMENTS` contains an environment name, use it.
Otherwise, list available environments from config and ask the user.

**IMPORTANT: If the CI workflow auto-deploys to dev on merge (check the build run for a `deploy-dev` job),
inform the user that dev was already deployed automatically. Then:**

1. **Ask the user to confirm dev is healthy** before proceeding to prod.
2. **Do NOT deploy to prod** until the user explicitly confirms dev is working.
3. If the user asks to deploy directly to prod without verifying dev, warn them and ask for confirmation.

**Never chain merge → prod deploy without explicit approval for each environment.**

## Step 4 — Find the build artifact

Using the adapter's commands and `deploy.image_tag_source`:
- **run-id**: Find the CI run associated with the merge commit, extract the run ID
- **commit-sha**: Use the merge commit SHA directly as the image tag
- **tag**: Find the latest git tag on the merge commit

Verify the build completed successfully before proceeding.

## Step 5 — Check current state

Use the adapter to show:
1. What is currently deployed in the target environment
2. What will change (diff between current and new)

## Step 6 — Confirm deployment

**ALWAYS ask the user for explicit confirmation before deploying.**

Display:
```
Ready to deploy:
  Change:      PR #{pr_number} — {pr_title}
  Image tag:   {image_tag}
  Target:      {environment}
  Current tag: {current_tag}

Proceed? (yes/no)
```

## Step 7 — Deploy

Use the adapter's deploy command to trigger the deployment.
Monitor the deployment progress using the adapter's status commands.

## Step 8 — Post-deploy verification

After deployment completes, run the following read-only checks automatically:

1. Use ops-suite:service-status with arguments: {service} {env_name}.
   Use session state from `/tmp/ops-suite-session/` — do not re-ask for environment.
   - If unhealthy → report immediately

2. Use ops-suite:service-logs with arguments: {service} {env_name}.
   Check for errors in last 5 minutes.
   - If errors found → report but continue

## Step 9 — Report and suggest next steps

```
Deployment Summary:
  PR:          #{pr_number} — {pr_title}
  Environment: {environment}
  Image tag:   {image_tag}
  Status:      {success/failed}
  Duration:    {time}

Post-deploy checks:
  Service health: {ok/degraded}
  Error check:    {clean/errors found}
```

If `deploy.migration_tool` is not "none", add:

```
Next steps:
  → Run `/ops-suite:db-migrate {env_name}` to check and apply pending migrations.
```
