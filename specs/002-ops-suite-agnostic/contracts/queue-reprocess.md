# Interface Contract: queue-reprocess

Every adapter file at `plugins/ops-suite/skills/queue-reprocess/adapters/{technology}.md`
MUST implement all steps below. The adapter YAML frontmatter must declare:

```yaml
implements: [step-a-connect, step-b-list-dlqs, step-c-reprocess]
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

**Contract**: Same as queue-triage Step B — List DLQs.

---

## Step C — Reprocess

**ID**: `step-c-reprocess`

**Input**: `dlq_name`, `target_queue` (the source queue to re-enqueue into), confirmation
from user (SKILL.md body collects this before calling the adapter)

**Output**: Confirmation of how many messages were moved; any errors

**Contract**: Adapter moves messages from the DLQ back to the source queue using the
technology's native redrive/replay mechanism:
- SQS: `aws sqs start-message-move-task` (native 2023+ API)
- Kafka: `kafka-consumer-groups.sh --reset-offsets --execute` on DLQ topic (consumer MUST
  be stopped first; adapter MUST run `--dry-run` and show output before `--execute`)
- Azure Service Bus: Python SDK (`azure-servicebus` + `azure-identity`) — adapter MUST warn
  if `python3` or `azure-servicebus` package is not available and provide install command
- RabbitMQ: existing adapter pattern (shovel or re-enqueue via management API)

**Safety requirement** (Principle IV): SKILL.md body must display the DLQ name, target
queue name, and message count, then require explicit user confirmation before Step C runs.

---

## Supported Technologies

| Technology | Adapter file | Status |
|------------|-------------|--------|
| `rabbitmq` | `adapters/rabbitmq.md` | Existing |
| `sqs` | `adapters/sqs.md` | New (this feature) |
| `kafka` | `adapters/kafka.md` | New (this feature) |
| `azure-service-bus` | `adapters/azure-service-bus.md` | New (this feature) |
