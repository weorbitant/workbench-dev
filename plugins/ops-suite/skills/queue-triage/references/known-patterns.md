# queue-triage — Known Failure Patterns

Use this decision tree to classify DLQ failures.

## Decision Tree

```
Message in DLQ
├── Check x-first-death-reason
│   ├── "rejected"
│   │   ├── All messages same entity → Entity-specific data issue
│   │   ├── All messages same error → Consumer bug
│   │   ├── Messages from multiple producers → Shared dependency failure
│   │   └── Intermittent pattern → Transient failure (network, timeout)
│   ├── "expired"
│   │   ├── Consumer running with 0 unacked → Consumer not subscribed to queue
│   │   ├── Consumer not running → Service down
│   │   └── Consumer running but slow → Performance issue or backpressure
│   └── "maxlen"
│       └── Queue reached max length → Consumer too slow, increase capacity
├── Check message payload
│   ├── Malformed JSON → Producer serialization bug
│   ├── Missing required fields → Schema version mismatch
│   ├── Unexpected field types → Schema evolution without consumer update
│   └── Valid payload → Issue is in processing logic, not data
└── Check timestamps
    ├── All recent (< 1 hour) → Active incident
    ├── Spread over days → Chronic issue, likely data-dependent
    └── Burst at specific time → Correlate with deployment or external event
```

## Main Queue Patterns (non-DLQ)

These patterns apply when the target is a main queue, not a DLQ.

```
Main queue with issues
├── 0 consumers + messages piling up
│   ├── Consumer service not running → Service down
│   ├── Consumer service running, subscribe() call missing → Code was removed or never added
│   │   ├── Subscription config exists but no subscribe() call → Orphaned config after refactor
│   │   └── Neither config nor subscribe() → Queue is legacy, can be purged
│   └── Consumer service running, subscribe() exists → Connection issue (check AMQP logs)
├── 0 consumers + 0 messages
│   └── Usually benign — queue exists but no traffic. Verify if consumer is expected.
└── Has consumers but messages growing
    ├── Consumer is slow → Performance issue, check resource usage
    └── Consumer is rejecting silently → Check consumer logs for errors
```

### 7. Missing consumer (subscription removed)
**Symptoms**: Main queue with 0 consumers, messages accumulating. Consumer service pods are healthy and running.
**Cause**: A refactor or feature change removed the `subscribe()` call but left the queue declaration and config. Common during service rewrites.
**Investigation**: Compare subscription config entries vs actual `subscribe()` calls in code. Check `git log` for the subscriber file to find when the handler was deleted.
**Fix**: Either re-add the consumer handler (if the subscription is still needed) or remove the orphaned queue and config (if it's no longer needed).

## Common Root Causes (DLQ)

### 1. Entity not found in database
**Symptoms**: Consumer rejects message, logs show "not found" or "does not exist"
**Cause**: Race condition between producer and consumer, or data was deleted
**Fix**: Check if entity exists, fix data or add retry logic with delay

### 2. External service unavailable
**Symptoms**: Multiple queues affected, timeout errors in consumer logs
**Cause**: Downstream service is down or rate-limiting
**Fix**: Check external service health, wait for recovery, then reprocess

### 3. Schema mismatch
**Symptoms**: Deserialization errors, "unexpected property" or "missing field" errors
**Cause**: Producer was updated without updating consumer, or vice versa
**Fix**: Align schemas, deploy fix, then reprocess

### 4. Duplicate processing guard
**Symptoms**: Consumer rejects with "already processed" or unique constraint violation
**Cause**: Message was already processed but not acked, then redelivered
**Fix**: Usually safe to purge these DLQ messages

### 5. Resource exhaustion
**Symptoms**: OOM or timeout errors in consumer
**Cause**: Message triggers expensive operation (large payload, complex computation)
**Fix**: Increase resources or optimize consumer, then reprocess

### 6. Configuration error
**Symptoms**: Failures started after a deployment
**Cause**: Missing environment variable, wrong endpoint, expired credentials
**Fix**: Fix configuration, redeploy consumer, then reprocess

## Reprocessing Decision

| Root Cause | Safe to Reprocess? | Notes |
|------------|-------------------|-------|
| Entity not found | After data fix | Verify entity exists first |
| External service down | After recovery | Wait for service to be healthy |
| Schema mismatch | After fix deployed | Both producer and consumer must agree |
| Duplicate guard | Purge instead | Messages were already processed |
| Resource exhaustion | After scaling | May fail again if not enough resources |
| Configuration error | After fix deployed | Simple reprocess after fix |
| Malformed payload | No | Producer must resend correct messages |
| Missing consumer (main queue) | Automatic after fix | Once subscribe() is restored, queued messages will be consumed naturally. No manual reprocessing needed |
| Orphaned queue (no longer needed) | Purge | Remove config, delete queue via rabbitmqadmin |
