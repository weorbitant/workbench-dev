---
name: queue-status
description: Check message queue status, list queues, monitor DLQ counts and consumers. Use when asked about "queues", "queue status", "DLQ", "dead letter", "consumers", "messages pending", "message broker", "rabbitmq", "queue health". TRIGGER when: user asks "how are the queues?", "queue status", "any DLQ messages?", "check queues", "messages pending", "consumer count", "queue health", "rabbitmq status", "are there messages in the DLQ?". SKIP: diagnosing DLQ failures (use queue-triage); moving messages back (use queue-reprocess).
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
- `message_broker` — determines which adapter to load
- `orchestrator` — for accessing the broker (if running in a cluster)
- `environments` — connection details including broker service info

## Step 1 — Load adapter

Read the adapter file at `references/{message_broker}.md` (in this skill's directory).
If the adapter does not exist, tell the user that the message broker `{message_broker}` is not yet supported and stop.

## Step 2 — Determine target environment

If `$ARGUMENTS` contains an environment name, use it. Otherwise ask the user.
Store the selected environment config as `env`.

## Step 3 — Connect to the broker

Use the orchestrator to execute commands on the broker pod/container, or connect via the management API if port-forwarded.

For Kubernetes, find the broker pod:
```
kubectl --context={env.context} get pods -n {env.namespaces.infra} | grep {env.services.broker.pod_pattern}
```

## Step 4 — List queues and status

Run the adapter's "list queues" command to get all queues with:
- Queue name
- Message count (ready + unacked)
- Consumer count
- State (running, idle, etc.)

If `$ARGUMENTS` contains a service name, filter queues by that service.

## Step 5 — Analyze and flag issues

Flag the following conditions:

| Condition | Severity | Action |
|-----------|----------|--------|
| DLQ with messages > 0 | Warning | Auto-chain to `queue-triage` (see below) |
| Queue with 0 consumers | Warning | Check if consumer service is running |
| Queue with growing message count | Warning | Consumer may be slow or stuck |
| Queue in "down" or "stopped" state | Critical | Investigate immediately |

## Step 6 — Report

Present results in this format:

```
Environment: {env_name}
Broker:      {env.services.broker.name}
Vhost:       {env.services.broker.vhost}
```

### If a service filter was provided:

Show only queues matching that service:

```
Queue Status — {service_name}:
| Queue Name              | Messages | Consumers | State   | Flags    |
|-------------------------|----------|-----------|---------|----------|
| {queue_name}            | {count}  | {count}   | running |          |
| {queue_name}.dlq        | {count}  | 0         | running | DLQ MSG  |
| {queue_name}            | {count}  | 0         | running | NO CONS  |
```

### If no service filter was provided:

Show **all queues** grouped by service prefix (the part before the first `:`), sorted by total messages descending within each group. Show the full list — do not truncate.

```
Queue Status — All Services ({total_queue_count} queues):

── {service_prefix} ──
| Queue Name              | Messages | Consumers | State   | Flags    |
|-------------------------|----------|-----------|---------|----------|
| {queue_name}            | {count}  | {count}   | running |          |
| {queue_name}.dlq        | {count}  | 0         | running | DLQ MSG  |

── {service_prefix_2} ──
| ...                     | ...      | ...       | ...     | ...      |
```

Then show a **Top DLQs across platform** section for DLQs with messages > 0, sorted descending:

```
Top DLQs (platform-wide):
| DLQ Name                                    | Messages   | Flags    |
|---------------------------------------------|------------|----------|
| {dlq_name}                                  | {count}    | CRITICAL |
| {dlq_name}                                  | {count}    | WARNING  |
```

Use CRITICAL (> 100k messages) and WARNING (1–100k messages).

### Summary (always shown):

```
Summary:
  Total queues: {count}
  Queues with messages: {count}
  DLQs with messages: {count}
  Queues with 0 consumers: {count}
```

If any DLQs have messages, automatically triage the first one:

Use ops-suite:queue-triage with arguments: {dlq_name} {env_name}.
Use session state from /tmp/ops-suite-session/ — do not re-ask for environment.
