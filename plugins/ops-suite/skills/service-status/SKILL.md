---
name: service-status
description: Check service/container status, health, events, and resource usage across environments. Use when asked about "pods", "service status", "check services", "crashloop", "restart", "container health", "service down", "unhealthy".
argument-hint: "[service-name] [environment]"
allowed-tools:
  - Bash
  - AskUserQuestion
model: haiku
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `orchestrator` — determines which adapter to load
- `environments` — available environments and their connection details

## Step 1 — Load adapter

Read the adapter file at `${CLAUDE_PLUGIN_ROOT}/skills/service-status/adapters/{orchestrator}.md`.
If the adapter does not exist, tell the user that the orchestrator `{orchestrator}` is not yet supported and stop.

All technology-specific commands come from the adapter. Do not invent commands.

## Step 2 — Determine target environment

If `$ARGUMENTS` contains an environment name (e.g. "dev", "prod"), use it.
Otherwise, list the available environments from config and ask the user which one to target.

Store the selected environment config as `env`.

## Step 3 — Determine target service

If `$ARGUMENTS` contains a service name, use it as `{service}`.
If no service is specified, list all services/pods in the environment using the adapter's "list all" command and let the user pick, or show the full overview.

## Step 4 — Check status

Run the following checks using adapter commands, in order:

1. **List pods/containers** for the service (or all if no service specified)
2. **Identify unhealthy** pods/containers (not Running/Completed)
3. **Check restart counts** for the target service
4. **Resource usage** (CPU/memory) for the target service
5. **Deployment status** for the target service

If any pod is in CrashLoopBackOff, Error, or has high restart counts (>3):
- Run the "pod details and events" command to get recent events
- Run the "check image/version" command to verify the deployed version
- Run the "rollout history" command to see recent changes

## Step 5 — Diagnose issues (if found)

For each unhealthy service:
1. Show the events from the describe output
2. Check if it is an OOMKilled (resource limit), ImagePullBackOff (wrong image), or CrashLoopBackOff (application error)
3. Suggest next steps:
   - OOMKilled → suggest increasing memory limits
   - ImagePullBackOff → verify image tag exists
   - CrashLoopBackOff → suggest checking logs with `service-logs` skill
   - Pending → check node resources or scheduling constraints

## Step 6 — Remediation (if requested)

**IMPORTANT: ALWAYS ask the user for explicit confirmation before performing any restart or rollout.**

If the user confirms:
- Use the adapter's "rolling restart" command
- Monitor the rollout status
- Verify pods are healthy after restart

## Output format

Present results as a clear summary:

```
Environment: {env_name}
Service: {service}
Status: {healthy/degraded/down}

Pods:
  NAME                    STATUS    RESTARTS   AGE
  ...

Resource Usage:
  NAME                    CPU       MEMORY
  ...

Issues Found:
  - {issue description and recommended action}
```
