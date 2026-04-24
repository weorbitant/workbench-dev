---
name: queue-triage
description: Diagnose why messages are failing in dead letter queues and produce a root cause report. Use when asked about "DLQ triage", "dead letter diagnosis", "why are messages failing", "queue errors". SKIP: moving messages back (use queue-reprocess); general counts (use queue-status).
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

## Step 3 — Identify queue type and survey

Determine whether the target queue is a DLQ or a main queue:
- **DLQ indicators**: name contains `.dead_letter`, `.dlq`, or `.error`
- **Main queue**: everything else

### If target is a DLQ (or no specific queue given):

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

Then continue to Step 4.

### If target is a main queue (e.g. 0 consumers, messages piling up):

This is a **missing consumer** investigation. Skip Steps 4-5 and go directly to Step 6 (Inspect consumer code), focusing on:
1. Is the consumer service running? (Use ops-suite:service-status)
2. Does the code actually subscribe to this queue? (Step 6)
3. Was the subscription recently removed? (Step 6b — git history)

After completing the code inspection, skip to Step 9 to produce the report.

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

1. **Find the subscription config**: Search for the queue name in config files (e.g. `grep -r "queue_name" src/config/`). Identify the subscription name mapped to this queue.
2. **Verify subscribe() call exists**: Search for `subscribe('{subscription_name}'` in the codebase. Compare all subscriptions declared in config vs actual `subscribe()` calls — any mismatch means orphaned config.
3. **Find the consumer handler**: Locate the subscriber class (typically in `application/amqp/`) and read its `onApplicationBootstrap()` method to see which subscriptions are actually registered.
4. **Check error handling patterns**: Look for try/catch, reject, or nack logic in the handler.
5. **Check if the error matches a known code path**: Cross-reference with the failure mode from Step 5.

## Step 6b — Check git history for removed handlers

If the consumer code is missing or the subscribe() call doesn't exist:

1. **Check git log for the subscriber file**: `git log --all --oneline -- {subscriber_file_path}`
2. **Look for deletion commits**: `git log --all --oneline --diff-filter=D -- {subscriber_directory}/`
3. **Inspect the deletion commit**: `git show {commit_hash} -- {file_path}` to see what was removed
4. **Identify root cause**: Was it an intentional removal (refactor) or accidental? Check the commit message and surrounding changes.

This step is critical when the subscription exists in config but no code subscribes to it.

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
