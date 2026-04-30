---
name: service-logs
description: Search and analyze logs from services and containers. Use when asked about "logs", "errors", "exceptions", "log search", "error messages", "stack trace", "application errors", "debug logs". TRIGGER when: user asks "any errors?", "check logs", "what's failing?", "show logs", "stack trace", "exceptions in X", "debug logs", "recent errors", "error messages". SKIP: pod health checks (use service-status); database queries (use db-query); queue failure analysis (use queue-triage).
allowed-tools: Bash AskUserQuestion
metadata:
  argument-hint: "[service-name] [environment]"
  model: haiku
---

## Step 0 — Load configuration

Check if `/tmp/ops-suite-session/config.json` exists:
- If yes, read it (pre-parsed by session-start hook).
- If no, read the plugin's `config.yaml`, parse it, and write to `/tmp/ops-suite-session/config.json` for other skills to reuse.
If neither exists, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `orchestrator` — determines which adapter to load
- `environments` — available environments and their connection details

## Step 1 — Load adapter

Read the adapter file at `adapters/{orchestrator}.md` (in this skill's directory).
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

Based on the error patterns found, suggest specific next steps:

- If errors include "does not exist", "column ... does not exist", "relation ... does not exist":
  ```
  → Run `/ops-suite:db-migrate {env_name}` to check and apply pending migrations.
  ```
- If errors include DLQ or message processing failures:
  ```
  → Run `/ops-suite:queue-triage {env_name}` to diagnose failed messages.
  ```
- If errors include connection failures or timeouts:
  ```
  Use ops-suite:service-status with arguments: {service} {env_name}.
  Use session state from /tmp/ops-suite-session/ — do not re-ask for environment.
  ```
