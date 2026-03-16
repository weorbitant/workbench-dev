---
name: deploy
description: Deploy a merged change to an environment. Verifies the change is merged, finds the build artifact, confirms with the user, triggers the deployment, and verifies the result.
argument-hint: "[PR-number or ref]"
disable-model-invocation: true
allowed-tools:
  - Bash
  - AskUserQuestion
model: sonnet
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `deploy.ci_provider` — determines which adapter to load
- `deploy.image_tag_source` — how to find the image tag (run-id, commit-sha, tag)
- `deploy.migration_tool` — whether migrations need to run
- `environments` — available environments

Also read the reference at `${CLAUDE_PLUGIN_ROOT}/skills/deploy/references/commands.md` for the step-by-step process.

## Step 1 — Load adapter

Read the adapter file at `${CLAUDE_PLUGIN_ROOT}/skills/deploy/adapters/{deploy.ci_provider}.md`.
If the adapter does not exist, tell the user that the CI provider `{deploy.ci_provider}` is not yet supported and stop.

## Step 2 — Identify the change to deploy

If `$ARGUMENTS` contains a PR number:
- Use the adapter to check the PR state (must be merged)
- Extract the merge commit SHA

If `$ARGUMENTS` contains a commit SHA or branch ref:
- Verify it exists and is reachable from the main branch

If nothing is provided, ask the user for a PR number or ref.

## Step 3 — Find the build artifact

Using the adapter's commands and `deploy.image_tag_source`:
- **run-id**: Find the CI run associated with the merge commit, extract the run ID
- **commit-sha**: Use the merge commit SHA directly as the image tag
- **tag**: Find the latest git tag on the merge commit

Verify the build completed successfully before proceeding.

## Step 4 — Check current state

Use the adapter to show:
1. What is currently deployed in the target environment
2. What will change (diff between current and new)

## Step 5 — Confirm deployment

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

## Step 6 — Deploy

Use the adapter's deploy command to trigger the deployment.
Monitor the deployment progress using the adapter's status commands.

## Step 7 — Verify deployment

After deployment completes:
1. Check that the new version is running (use `service-status` adapter commands)
2. Verify health checks pass
3. Check for any immediate errors in logs (brief check)

## Step 8 — Check migrations (if applicable)

If `deploy.migration_tool` is not "none":
- Remind the user to run migrations if needed
- Suggest using the `db-migrate` skill

## Output format

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
  Migrations:     {not needed/pending/completed}
```
