---
name: queue-reprocess
description: Move failed messages from dead letter queues back to their main queue. Use when asked about "reprocess DLQ", "retry failed messages", "move DLQ messages", "republish dead letters". SKIP: diagnosing failures first (use queue-triage); checking counts (use queue-status).
allowed-tools: Bash Read AskUserQuestion
metadata:
  argument-hint: "[queue-name] [environment]"
  model: haiku
  disable-model-invocation: "true"
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

## Step 1 — Load adapter

Read the adapter file at `adapters/{message_broker}.md` (in this skill's directory).
If the adapter does not exist, tell the user that the message broker `{message_broker}` is not yet supported and stop.

## Step 2 — Determine target environment

If `$ARGUMENTS` contains an environment name, use it. Otherwise ask the user.
Store the selected environment config as `env`.

## Step 3 — Pre-flight: check triage

Check `/tmp/ops-suite-session/last-triage.json`:

If it exists and is less than 10 minutes old for the same DLQ:
- Skip triage, use cached results.
- Show: "Using triage from {minutes} ago: {summary}"

If it does not exist or is stale:
- Show: "This DLQ has not been triaged recently. Reprocessing without fixing the root cause will likely send messages back to the DLQ."
- Suggest: `→ Run /ops-suite:queue-triage {dlq_name} {env_name} first.`
- Ask: "Continue anyway? (yes/no)"

## Step 4 — Identify DLQ and target queue

If `$ARGUMENTS` contains a queue name, use it.
Otherwise, list DLQs with messages and let the user pick:

```
DLQs with messages:
| DLQ Name                 | Messages | Target Queue         |
|--------------------------|----------|----------------------|
| {dlq_name}               | {count}  | {target_queue}       |
```

Determine the target (main) queue by:
1. Checking `x-first-death-queue` header from a sample message
2. Removing the DLQ suffix (e.g., `.dlq`, `.dead-letter`, `.error`)
3. Asking the user to confirm the target queue

## Step 5 — Verify prerequisites

Use the adapter to check:
1. The DLQ exists and has messages
2. The target queue exists and has consumers
3. The required plugin/feature is available (e.g., shovel plugin for RabbitMQ)

If the target queue has 0 consumers, warn the user that messages will just pile up.

## Step 6 — Confirm reprocessing

**ALWAYS ask for explicit confirmation before moving messages.**

Display:
```
Ready to reprocess:
  Source DLQ:    {dlq_name}
  Target queue:  {target_queue}
  Messages:      {count}
  Method:        {shovel/move/republish}

This will move {count} messages back to {target_queue}. Proceed? (yes/no)
```

## Step 7 — Move messages

Use the adapter's preferred method (in order of preference):
1. **Shovel** — Create a temporary shovel to move messages (RabbitMQ)
2. **Move** — Use the Management API move feature
3. **Republish clean** — Fetch, strip death headers, republish to target exchange

### Monitor progress

After starting the move:
1. Check the DLQ message count periodically
2. Check the target queue message count
3. Verify messages are being consumed (not just accumulating)

## Step 8 — Verify completion

Once the DLQ is empty (or the expected count has been moved):
1. Confirm the DLQ message count is 0 (or reduced by expected amount)
2. Check the target queue for any new DLQ entries (messages failing again)
3. Check consumer logs for errors

## Step 9 — Cleanup

1. Remove the temporary shovel (if created)
2. Kill any port-forward processes
3. Report the result

## Step 10 — Purge (if needed)

If messages are not reprocessable (e.g., malformed payloads, already processed):

**ALWAYS ask for explicit confirmation before purging.**

```
Purge {count} messages from {dlq_name}? This is irreversible. (yes/no)
```

## Output format

```
Reprocessing Summary:
  DLQ:           {dlq_name}
  Target:        {target_queue}
  Environment:   {env_name}
  Messages moved: {count}
  Method:        {method}
  Status:        {success/partial/failed}

Post-move check:
  DLQ remaining: {count}
  Target queue:  {count} messages, {consumers} consumers
  New DLQ entries: {count} (messages that failed again)

Cleanup:
  - Shovel removed: {yes/no/n/a}
  - Port-forward killed: {yes/no/n/a}
```
