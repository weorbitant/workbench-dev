---
name: deploy-status
description: Show deployment status across environments — current deployed commit, author, timestamp, PR, and drift between envs. Use when asked about "deploy status", "what is deployed", "what version is in prod", "is prod up to date", "show deployments", "current commit per env", "deployment overview", "env diff", "qué hay desplegado", "estado de los deploys". TRIGGER when: user asks "what's deployed in X", "deploy status", "is staging behind prod", "show me deploys", "last deploy of [service]", "deployment diff between envs", "qué versión hay en prod". SKIP: deploying new versions (use deploy or workflow-deploy); pod health (use service-status); logs (use service-logs).
allowed-tools: Bash AskUserQuestion
metadata:
  argument-hint: "[service-name] [environment]"
  model: haiku
---

## Step 0 — Load configuration

Check if `/tmp/ops-suite-session/config.json` exists:
- If yes, read it (pre-parsed by session-start hook).
- If no, read `${XDG_CONFIG_HOME:-$HOME/.config}/ops-suite/config.yaml` (preferred) or the plugin's `config.yaml` (legacy), parse it, and write to `/tmp/ops-suite-session/config.json` for other skills to reuse.
If neither exists, tell the user to run `/ops-suite:configure` (or copy `config.example.yaml` to `~/.config/ops-suite/config.yaml` and fill in their values). Stop here.

Extract:
- `orchestrator` — determines which orchestrator reference to load (how to read deployed image tag)
- `deploy.ci_provider` — determines which CI reference to load (how to map image tag → commit info)
- `deploy.image_tag_source` — `run-id`, `commit-sha`, or `tag`
- `deploy.repo` — GitHub/GitLab repo for CI lookups
- `service` — default service name if `$ARGUMENTS` does not provide one
- `environments` — list of envs to query

## Step 1 — Load references

Read both reference files (in this skill's directory):
- `references/{orchestrator}.md` — commands to extract the running image tag from the orchestrator
- `references/{ci_provider}.md` — commands to map image tag → commit metadata

If either file does not exist, tell the user that `{orchestrator}` or `{ci_provider}` is not yet supported and stop.

## Step 2 — Determine scope

**Service**: if `$ARGUMENTS` contains a service name, use it. Otherwise, use `config.service`.

**Environments**: if `$ARGUMENTS` contains an environment name, query only that env. Otherwise, query **all** environments in `config.environments`.

This skill is **read-only**. Never trigger a deploy or rollback — only report.

## Step 3 — Extract deployed image tag per environment

For each target environment, run the orchestrator reference's "get deployment image tag" command. Capture:
- `image_tag` (the tag part of `image:tag`, used as input for Step 4)
- `replicas` (desired vs ready)
- `last_update` (timestamp of last rollout, if available)
- `condition` (Available / Progressing / Degraded)

Run env queries in parallel where possible (one Bash call per env, dispatched together).

If a deployment is missing in an env, mark it as `NOT DEPLOYED` and continue with the rest — do not abort.

## Step 4 — Resolve image tag → commit metadata

For each unique `image_tag` collected in Step 3, run the CI reference's "resolve image tag" command. Capture:
- `commit_sha` (short, 7 chars)
- `commit_message` (first line, truncated to 60 chars)
- `author`
- `deployed_at` (timestamp of the build / deploy run)
- `pr_number` and `pr_title` (if the commit corresponds to a merged PR)

Cache results: if two envs run the same `image_tag`, query the CI only once.

If the CI lookup fails for a tag (e.g. run not found, deleted), mark its fields as `unknown` and continue.

## Step 5 — Detect drift between envs

Compare commits across envs to detect drift:

| Condition | Flag |
|-----------|------|
| All envs run the same commit | `IN SYNC` |
| Lower env (dev/staging) is ahead of higher env (prod) | `PROD BEHIND` |
| Higher env is ahead of lower env (rare, manual prod hotfix) | `PROD AHEAD` |
| Two envs run different commits and neither is an ancestor of the other | `DIVERGED` |

To check ancestry between two commits, use:
```
gh api repos/{repo}/compare/{base}...{head} --jq '.status'
```
Values: `identical`, `ahead`, `behind`, `diverged`.

## Step 6 — Report

Present results in this exact format:

```
Service:    {service}
Repo:       {deploy.repo}
Generated:  {now ISO-8601}
```

### Per-environment table

```
Deploy Status — {service}:

| Env     | Commit  | PR     | Author    | Deployed At         | Replicas | Condition  | Image Tag  |
|---------|---------|--------|-----------|---------------------|----------|------------|------------|
| dev     | abc1234 | #142   | sito      | 2026-04-30 09:15    | 3/3      | Available  | 8123456789 |
| staging | abc1234 | #142   | sito      | 2026-04-30 11:42    | 3/3      | Available  | 8123456789 |
| prod    | def5678 | #138   | alfonso   | 2026-04-29 16:00    | 5/5      | Available  | 8098765432 |
```

Truncate `commit_message` is **not** shown in the table — keep the table compact. Show messages in the drift section below if useful.

### Drift section

If all envs are `IN SYNC`, show:
```
Drift: all environments in sync (commit abc1234)
```

Otherwise, list each pair of out-of-sync envs:
```
Drift detected:
  prod is BEHIND staging:
    def5678 → abc1234 (4 commits)
    Latest: PR #142 — feat(billing): add proration on plan change
  staging is IN SYNC with dev (abc1234)
```

To list commits between two SHAs:
```
gh api repos/{repo}/compare/{base}...{head} --jq '.commits[] | {sha: .sha[0:7], msg: .commit.message | split("\n")[0]}'
```
Show at most the 5 most recent commits in the drift section; if more, show count and truncate.

### Summary

```
Summary:
  Environments queried: {count}
  In sync:              {count}
  Drifted:              {count}
  Not deployed:         {count}
```

## Notes

- This skill is read-only. Do **not** invoke `deploy`, `rollback`, or any chained mutating skill. If the user wants to act on the result, suggest they run `/ops-suite:deploy {env}` themselves.
- If the user explicitly asks for a single env (via `$ARGUMENTS`), skip the drift section — drift only makes sense across multiple envs.
- All timestamps in UTC unless the source system says otherwise.
