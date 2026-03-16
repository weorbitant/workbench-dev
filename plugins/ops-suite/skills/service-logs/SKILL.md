---
name: service-logs
description: Search and analyze logs from services and containers. Use when asked about "logs", "errors", "exceptions", "log search", "error messages", "stack trace", "application errors", "debug logs".
argument-hint: "[service-name] [environment]"
allowed-tools:
  - Bash
  - AskUserQuestion
model: sonnet
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `orchestrator` — determines which adapter to load
- `environments` — available environments and their connection details

## Step 1 — Load adapter

Read the adapter file at `${CLAUDE_PLUGIN_ROOT}/skills/service-logs/adapters/{orchestrator}.md`.
If the adapter does not exist, tell the user that the orchestrator `{orchestrator}` is not yet supported and stop.

## Step 2 — Determine target

If `$ARGUMENTS` contains an environment name, use it. Otherwise ask the user.
If `$ARGUMENTS` contains a service name, use it. Otherwise list available services and ask.

Store selected environment config as `env` and service name as `{service}`.

## Step 3 — Retrieve and analyze logs

Start with recent errors (last 200 lines with error/exception filtering):

1. **Recent errors** — Use adapter command for recent error logs
2. **Count and classify** — Group errors by type/message
3. **Frequency analysis** — Determine if errors are increasing, steady, or sporadic

If the user asks about a specific pattern or entity:
4. **Pattern search** — Use adapter command to grep for specific patterns
5. **Context around errors** — Get lines before/after each match for context

If the user wants live monitoring:
6. **Follow logs** — Use adapter command to tail/follow logs (warn that this runs indefinitely)

## Step 4 — Cross-pod analysis (if applicable)

If the service has multiple replicas:
1. Get logs from all pods/containers using the adapter's "all replicas" command
2. Compare error patterns across replicas
3. Note if errors are isolated to one replica or widespread

## Step 5 — Check previous container (if crash detected)

If a container recently restarted, use the adapter's "previous container logs" command to capture the crash output.

## Step 6 — Report findings

Present results in this format:

```
Service: {service}
Environment: {env_name}
Time range: last {duration}

Error Summary:
  Total errors: {count}
  Unique error types: {count}

Error Breakdown:
  1. {error_type} — {count} occurrences — {frequency pattern}
     Sample: {first occurrence snippet}
  2. ...

Affected Entities:
  - {entity_id}: {error_type} at {timestamp}
  - ...

Pattern:
  {description of when errors started, frequency trend, correlation with events}

Recommended Next Steps:
  - {action items based on findings}
```
