---
name: queue-triage
description: Diagnose why messages are failing in dead letter queues. Surveys DLQs, fetches sample messages, analyzes failure patterns, inspects consumer code, and produces a root cause report. Use when asked about "DLQ triage", "dead letter diagnosis", "failed messages", "message failures", "queue errors".
argument-hint: "[queue-name] [environment]"
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
model: sonnet
---

## Step 0 — Load configuration

Check if `/tmp/ops-suite-session/config.json` exists:
- If yes, read it (pre-parsed by session-start hook).
- If no, read the plugin's `config.yaml`, parse it, and write to `/tmp/ops-suite-session/config.json` for other skills to reuse.
If neither exists, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `message_broker` — determines which adapter to load
- `orchestrator` — for connecting to the broker
- `environments` — connection details

Also read the reference at `references/known-patterns.md` (in this skill's directory) for common failure patterns.

## Step 1 — Load adapter

Read the adapter file at `adapters/{message_broker}.md` (in this skill's directory).
If the adapter does not exist, tell the user that the message broker `{message_broker}` is not yet supported and stop.

## Step 2 — Determine target environment

If `$ARGUMENTS` contains an environment name, use it. Otherwise ask the user.
Store the selected environment config as `env`.

## Step 3 — Survey DLQs

Use the adapter's "list DLQs" command to find all dead letter queues with messages.
If `$ARGUMENTS` contains a specific queue name, focus on that queue.

Present the DLQ overview:
```
DLQs with messages:
| DLQ Name                 | Messages | Original Queue       |
|--------------------------|----------|----------------------|
| {dlq_name}               | {count}  | {source_queue}       |
```

If there are multiple DLQs, ask the user which one to triage first.

## Step 4 — Fetch sample messages

Use the adapter's "peek messages" command to get 3-5 sample messages without consuming them.

For each message, extract:
- Headers (especially `x-death`, `x-first-death-reason`, `x-first-death-queue`)
- Routing key
- Payload (body)
- Timestamp

## Step 5 — Analyze failure patterns

Classify failures using the decision tree:

| Indicator | Likely Failure Mode |
|-----------|-------------------|
| `x-first-death-reason: rejected` | Consumer explicitly rejected the message |
| `x-first-death-reason: expired` | Message TTL exceeded, consumer too slow or down |
| Malformed JSON in body | Serialization error from producer |
| Missing required fields | Schema mismatch between producer and consumer |
| Valid payload, same error repeated | Consumer bug or external dependency failure |
| Messages from different producers | Shared failure (e.g., database down) |
| All messages have same entity ID | Entity-specific data issue |

Use the `analyze_messages.py` script for bulk analysis if there are many messages:
```bash
python3 scripts/analyze_messages.py {messages_file}
```

## Step 6 — Inspect consumer code (if accessible)

If the codebase is available:
1. Find the consumer handler for the affected queue
2. Look for error handling patterns
3. Check if the error matches a known code path

## Step 7 — Verify external state

Based on the failure analysis, use read-only skills to gather context automatically:

- **Database issues**: Use ops-suite:db-query with arguments: {env_name}.
  Formulate a query to check if the affected entity exists.
- **Service down**: Use ops-suite:service-status with arguments: {consumer_service} {env_name}.
- **Schema mismatch**: Compare message format with consumer DTO expectations.
- **Rate limiting**: Check if an external API is returning 429s.

Use session state from `/tmp/ops-suite-session/` — do not re-ask for environment.

## Step 8 — Check consumer logs

Use ops-suite:service-logs with arguments: {consumer_service} {env_name}.
Focus on errors related to the DLQ entities. Use session state — do not re-ask for environment.

## Step 9 — Produce report

Present the triage report:

```
Queue Triage Report
===================

Queue:       {dlq_name}
Environment: {env_name}
Messages:    {total_count}
Time range:  {earliest_timestamp} — {latest_timestamp}

Failure Mode: {classification}
Root Cause:   {description}

Evidence:
  - {evidence_point_1}
  - {evidence_point_2}
  - {evidence_point_3}

Sample Message:
  Headers: {relevant_headers}
  Routing Key: {routing_key}
  Body (truncated): {first_200_chars}

Recommendation:
  1. {action_1}
  2. {action_2}
  3. {action_3}

Reprocessable: {yes/no/partial}
  {explanation of whether messages can be safely reprocessed after fix}
```

If messages are reprocessable, add:

```
Next steps:
  → Run `/ops-suite:queue-reprocess {dlq_name} {env_name}` to move messages back to the main queue.
```

If the root cause is a missing migration, add:

```
Next steps:
  → Run `/ops-suite:db-migrate {env_name}` to apply pending migrations.
  → Then run `/ops-suite:queue-reprocess {dlq_name} {env_name}` to reprocess failed messages.
```

Save triage results to `/tmp/ops-suite-session/last-triage.json` for use by ops-suite:queue-reprocess.
