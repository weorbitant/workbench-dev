# RabbitMQ Adapter — queue-reprocess

## Find broker pod

```bash
kubectl --context={env.context} get pods -n {env.namespaces.infra} | grep {env.services.broker.pod_pattern}
```

## Port-forward to Management API

```bash
kubectl --context={env.context} port-forward -n {env.namespaces.infra} {broker_pod} {env.services.broker.management_port}:{env.services.broker.management_port} &
```

## List DLQs with messages

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_queues -p {env.services.broker.vhost} \
  name messages consumers \
  --formatter table | grep -iE "dlq|dead.letter|\.error" | awk '$2 > 0'
```

## Check DLQ message count

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_queues -p {env.services.broker.vhost} \
  name messages \
  --formatter table | grep {dlq_name}
```

## Check target queue consumers

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_queues -p {env.services.broker.vhost} \
  name messages consumers \
  --formatter table | grep {target_queue}
```

## Check if shovel plugin is enabled

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmq-plugins list | grep rabbitmq_shovel
```

## Peek at sample message (to find target queue from headers)

```bash
curl -s -u {user}:{password} \
  -X POST http://localhost:{env.services.broker.management_port}/api/queues/{vhost_encoded}/{dlq_name_encoded}/get \
  -H 'content-type: application/json' \
  -d '{"count":1,"ackmode":"ack_requeue_true","encoding":"auto"}' | \
  jq '.[0].properties.headers["x-first-death-queue"]'
```

## Method 1: Create a temporary shovel (preferred)

```bash
curl -s -u {user}:{password} \
  -X PUT http://localhost:{env.services.broker.management_port}/api/parameters/shovel/{vhost_encoded}/reprocess-{dlq_name} \
  -H 'content-type: application/json' \
  -d '{
    "value": {
      "src-protocol": "amqp091",
      "src-uri": "amqp:///{vhost}",
      "src-queue": "{dlq_name}",
      "dest-protocol": "amqp091",
      "dest-uri": "amqp:///{vhost}",
      "dest-queue": "{target_queue}",
      "src-prefetch-count": 100,
      "ack-mode": "on-confirm",
      "src-delete-after": "queue-length"
    }
  }'
```

## Monitor shovel progress

```bash
curl -s -u {user}:{password} \
  http://localhost:{env.services.broker.management_port}/api/shovels/{vhost_encoded} | \
  jq '.[] | select(.name == "reprocess-{dlq_name}") | {name, state, src_queue: .value.src_queue, dest_queue: .value.dest_queue}'
```

## Check shovel status

```bash
curl -s -u {user}:{password} \
  http://localhost:{env.services.broker.management_port}/api/shovels/{vhost_encoded} | \
  jq '.[] | select(.name == "reprocess-{dlq_name}") | .state'
```

## Remove shovel after completion

```bash
curl -s -u {user}:{password} \
  -X DELETE http://localhost:{env.services.broker.management_port}/api/parameters/shovel/{vhost_encoded}/reprocess-{dlq_name}
```

## Method 2: Move via Management API (message by message)

Fetch and republish each message:

```bash
# Fetch one message (consuming it)
MSG=$(curl -s -u {user}:{password} \
  -X POST http://localhost:{env.services.broker.management_port}/api/queues/{vhost_encoded}/{dlq_name_encoded}/get \
  -H 'content-type: application/json' \
  -d '{"count":1,"ackmode":"ack_requeue_false","encoding":"auto"}')

# Extract payload and routing key
PAYLOAD=$(echo "$MSG" | jq -r '.[0].payload')
ROUTING_KEY=$(echo "$MSG" | jq -r '.[0].routing_key')

# Republish to the default exchange with the target queue as routing key
curl -s -u {user}:{password} \
  -X POST http://localhost:{env.services.broker.management_port}/api/exchanges/{vhost_encoded}/amq.default/publish \
  -H 'content-type: application/json' \
  -d "{
    \"properties\": {},
    \"routing_key\": \"{target_queue}\",
    \"payload\": $(echo "$PAYLOAD" | jq -Rs .),
    \"payload_encoding\": \"string\"
  }"
```

## Method 3: Republish clean (strip death headers)

Use this when messages have problematic headers that cause issues on reprocessing:

```bash
# Fetch message
MSG=$(curl -s -u {user}:{password} \
  -X POST http://localhost:{env.services.broker.management_port}/api/queues/{vhost_encoded}/{dlq_name_encoded}/get \
  -H 'content-type: application/json' \
  -d '{"count":1,"ackmode":"ack_requeue_false","encoding":"auto"}')

PAYLOAD=$(echo "$MSG" | jq -r '.[0].payload')
ROUTING_KEY=$(echo "$MSG" | jq -r '.[0].routing_key')
EXCHANGE=$(echo "$MSG" | jq -r '.[0].properties.headers["x-first-death-exchange"] // "amq.default"')

# Republish with clean headers to original exchange
curl -s -u {user}:{password} \
  -X POST http://localhost:{env.services.broker.management_port}/api/exchanges/{vhost_encoded}/{exchange_encoded}/publish \
  -H 'content-type: application/json' \
  -d "{
    \"properties\": {\"content_type\": \"application/json\"},
    \"routing_key\": \"$ROUTING_KEY\",
    \"payload\": $(echo "$PAYLOAD" | jq -Rs .),
    \"payload_encoding\": \"string\"
  }"
```

## Purge DLQ (ALWAYS ask confirmation first, irreversible)

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl purge_queue -p {env.services.broker.vhost} {dlq_name}
```

Or via Management API:
```bash
curl -s -u {user}:{password} \
  -X DELETE http://localhost:{env.services.broker.management_port}/api/queues/{vhost_encoded}/{dlq_name_encoded}/contents
```
