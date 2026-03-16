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

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `message_broker` — determines which adapter to load
- `orchestrator` — for connecting to the broker
- `environments` — connection details

Also read the reference at `${CLAUDE_PLUGIN_ROOT}/skills/queue-triage/references/known-patterns.md` for common failure patterns.

## Step 1 — Load adapter

Read the adapter file at `${CLAUDE_PLUGIN_ROOT}/skills/queue-triage/adapters/{message_broker}.md`.
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
python3 ${CLAUDE_PLUGIN_ROOT}/skills/queue-triage/scripts/analyze_messages.py {messages_file}
```

## Step 6 — Inspect consumer code (if accessible)

If the codebase is available:
1. Find the consumer handler for the affected queue
2. Look for error handling patterns
3. Check if the error matches a known code path

## Step 7 — Verify external state

Based on the failure analysis:
- **Database issues**: Check if the referenced entities exist in the database
- **Service down**: Check if the consumer service is running (`service-status`)
- **Schema mismatch**: Compare message format with consumer expectations
- **Rate limiting**: Check if an external API is returning 429s

## Step 8 — Check consumer logs

Use `service-logs` patterns to find related errors:
```
kubectl --context={env.context} logs -l app={consumer_service} -n {env.namespaces.apps} --tail=200 | grep -i "error\|exception\|reject"
```

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
