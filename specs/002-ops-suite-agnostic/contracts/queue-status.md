# Interface Contract: queue-status

Every adapter file at `plugins/ops-suite/skills/queue-status/adapters/{technology}.md` MUST
implement all steps below. The adapter YAML frontmatter must declare:

```yaml
implements: [step-a-connect, step-b-list, step-c-format]
```

---

## Step A — Connect

**ID**: `step-a-connect`

**Input**: Broker connection details from config (URL, credentials, region, namespace, etc.)

**Output**: Confirmation that the broker is reachable

**Contract**: Adapter shows the connectivity check command, runs it, and reports the broker
version or cluster name on success. On failure, surfaces the error and stops.

---

## Step B — List

**ID**: `step-b-list`

**Input**: Optional name prefix filter from `$ARGUMENTS`

**Output**: Raw queue list with at minimum: queue name, message count, DLQ flag

**Contract**: Adapter lists ALL queues visible to the configured credentials. If the broker
supports it, include: ready messages, unacknowledged messages, consumer count, queue state.
Identify DLQs by naming convention (`.dlq`, `.dead-letter`, `-DLT`, `$DeadLetterQueue`).

---

## Step C — Format

**ID**: `step-c-format`

**Input**: Raw queue list from Step B

**Output**: Structured report in this exact format:

```
Broker:  {technology} ({broker_endpoint})
Queues:  {total_count} ({dlq_count} DLQs)

| Queue | Messages | Consumers | DLQ? | State |
|-------|----------|-----------|------|-------|
| name  | 0        | 1         | No   | running |
| name.dlq | 42  | 0         | Yes  | running |

Alerts:
- {queue_name}: {message_count} messages with 0 consumers
- {dlq_name}: {message_count} dead-letter messages pending reprocess
```

**Contract**: Table sorted by message count descending. DLQ rows highlighted. Alerts section
lists only actionable conditions (non-empty DLQs, queues with messages and no consumers).

---

## Supported Technologies

| Technology | Adapter file | Status |
|------------|-------------|--------|
| `rabbitmq` | `adapters/rabbitmq.md` | New (migrated from references/) |
| `sqs` | `adapters/sqs.md` | New (this feature) |
| `kafka` | `adapters/kafka.md` | New (this feature) |
| `azure-service-bus` | `adapters/azure-service-bus.md` | New (migrated from references/) |
