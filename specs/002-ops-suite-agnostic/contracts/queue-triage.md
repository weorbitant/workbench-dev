# Interface Contract: queue-triage

Every adapter file at `plugins/ops-suite/skills/queue-triage/adapters/{technology}.md` MUST
implement all steps below. The adapter YAML frontmatter must declare:

```yaml
implements: [step-a-connect, step-b-list-dlqs, step-c-peek, step-d-analyze]
```

---

## Step A — Connect

**ID**: `step-a-connect`

**Input**: Broker connection details from config

**Output**: Confirmation that the broker is reachable

**Contract**: Same as queue-status Step A — Connect.

---

## Step B — List DLQs

**ID**: `step-b-list-dlqs`

**Input**: Optional queue name pattern from `$ARGUMENTS`

**Output**: List of DLQs with non-zero message count

**Contract**: Adapter returns only queues matching the DLQ naming convention for this
technology. Each row must include: queue name, message count, associated source queue name
(if determinable from convention).

---

## Step C — Peek

**ID**: `step-c-peek`

**Input**: `queue_name`, `count` (default 5)

**Output**: Sample messages from the specified DLQ, non-destructively

**Contract**: Adapter reads messages WITHOUT consuming them (ack-requeue, peek mode, or
equivalent). Shows: payload preview (≤200 chars), routing key or message ID, error headers
if available, timestamp. MUST NOT remove messages from the queue.

---

## Step D — Analyze

**ID**: `step-d-analyze`

**Input**: Sample messages from Step C

**Output**: Triage summary with error classification

**Contract**: Adapter extracts error indicators (x-death headers, exception type in payload,
error code). Groups messages by error pattern. Output format:

```
DLQ: {queue_name} — {count} messages

Error breakdown:
| Pattern | Count | Sample message ID |
|---------|-------|------------------|
| {error} | N     | {id}              |

Recommended action: {action}
```

---

## Supported Technologies

| Technology | Adapter file | Status |
|------------|-------------|--------|
| `rabbitmq` | `adapters/rabbitmq.md` | Existing |
| `sqs` | `adapters/sqs.md` | New (this feature) |
| `kafka` | `adapters/kafka.md` | New (this feature) |
| `azure-service-bus` | `adapters/azure-service-bus.md` | New (this feature) |
