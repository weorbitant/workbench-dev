# RabbitMQ Adapter — queue-triage

## Find broker pod

```bash
kubectl --context={env.context} get pods -n {env.namespaces.infra} | grep {env.services.broker.pod_pattern}
```

## List DLQs with messages

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_queues -p {env.services.broker.vhost} \
  name messages consumers state \
  --formatter table | grep -iE "dlq|dead.letter|\.error" | awk '$2 > 0'
```

## Get queue message count

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_queues -p {env.services.broker.vhost} \
  name messages \
  --formatter table | grep {queue_name}
```

## Peek messages (non-destructive)

### Option A — kubectl exec with rabbitmqadmin (preferred, no port-forward needed)

Check if rabbitmqadmin is available on the broker pod:
```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- which rabbitmqadmin 2>/dev/null
```

If available, peek messages directly:
```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqadmin get queue={queue_name} count=5 ackmode=ack_requeue_true \
  --vhost={env.services.broker.vhost} --format=long
```

### Option B — Management API via port-forward (fallback)

**IMPORTANT**: Execute each step as a separate command. Do NOT combine port-forward + curl in one command.

**Step 1 — Get credentials** from RABBITMQ_URL in the consumer service:
```bash
kubectl --context={env.context} exec -n {env.namespaces.apps} {consumer_pod} -- \
  env 2>/dev/null | grep RABBITMQ_URL | head -1
```
Extract user:password from the URL (`amqp://user:password@host/vhost`).

**Step 2 — Port-forward** (run in background):
```bash
kubectl --context={env.context} port-forward -n {env.namespaces.infra} {broker_pod} {env.services.broker.management_port}:{env.services.broker.management_port} &
```

**Step 3 — Fetch messages** (ackmode=ack_requeue_true preserves them):
```bash
curl -s -u {user}:{password} \
  -X POST http://localhost:{env.services.broker.management_port}/api/queues/{vhost_encoded}/{queue_name_encoded}/get \
  -H 'content-type: application/json' \
  -d '{"count":5,"ackmode":"ack_requeue_true","encoding":"auto"}' | jq '.'
```

## Extract death headers from messages

```bash
curl -s -u {user}:{password} \
  -X POST http://localhost:{env.services.broker.management_port}/api/queues/{vhost_encoded}/{queue_name_encoded}/get \
  -H 'content-type: application/json' \
  -d '{"count":5,"ackmode":"ack_requeue_true","encoding":"auto"}' | \
  jq '.[] | {
    routing_key: .routing_key,
    death_reason: .properties.headers["x-first-death-reason"],
    death_queue: .properties.headers["x-first-death-queue"],
    death_exchange: .properties.headers["x-first-death-exchange"],
    timestamp: .properties.timestamp,
    payload_size: (.payload | length),
    payload_preview: (.payload | if length > 200 then .[:200] + "..." else . end)
  }'
```

## Get full message details (single message)

```bash
curl -s -u {user}:{password} \
  -X POST http://localhost:{env.services.broker.management_port}/api/queues/{vhost_encoded}/{queue_name_encoded}/get \
  -H 'content-type: application/json' \
  -d '{"count":1,"ackmode":"ack_requeue_true","encoding":"auto"}' | jq '.[0]'
```

## Dump messages to file for bulk analysis

```bash
curl -s -u {user}:{password} \
  -X POST http://localhost:{env.services.broker.management_port}/api/queues/{vhost_encoded}/{queue_name_encoded}/get \
  -H 'content-type: application/json' \
  -d '{"count":50,"ackmode":"ack_requeue_true","encoding":"auto"}' > /tmp/dlq_messages.json
```

## Check queue bindings (to find source exchange and routing)

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_bindings -p {env.services.broker.vhost} \
  source_name destination_name routing_key \
  --formatter table | grep {queue_name}
```

## Check queue policy (DLQ configuration)

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_policies -p {env.services.broker.vhost} \
  --formatter table | grep {queue_pattern}
```

## Consumer service logs (find related errors)

```bash
kubectl --context={env.context} logs -l app={consumer_service} -n {env.namespaces.apps} --tail=200 | grep -iE "error|exception|reject|nack"
```

## Consumer service logs with context

```bash
kubectl --context={env.context} logs -l app={consumer_service} -n {env.namespaces.apps} --tail=500 | grep -B3 -A3 -i "{entity_id}"
```
