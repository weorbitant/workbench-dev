# RabbitMQ Adapter — queue-status

## Find broker pod

```bash
kubectl --context={env.context} get pods -n {env.namespaces.infra} | grep {env.services.broker.pod_pattern}
```

## List all queues with details

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_queues -p {env.services.broker.vhost} \
  name messages messages_ready messages_unacknowledged consumers state \
  --formatter table
```

## List queues filtered by name pattern

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_queues -p {env.services.broker.vhost} \
  name messages consumers state \
  --formatter table | grep -i {pattern}
```

## List only DLQs (dead letter queues)

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_queues -p {env.services.broker.vhost} \
  name messages consumers state \
  --formatter table | grep -iE "dlq|dead.letter|\.error"
```

## List queues with messages (non-empty)

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_queues -p {env.services.broker.vhost} \
  name messages consumers \
  --formatter table | awk 'NR==1 || $2 > 0'
```

## List queues with 0 consumers

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_queues -p {env.services.broker.vhost} \
  name messages consumers \
  --formatter table | awk 'NR==1 || $3 == 0'
```

## Queue details (single queue)

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_queues -p {env.services.broker.vhost} \
  name messages messages_ready messages_unacknowledged consumers memory state policy \
  --formatter table | grep {queue_name}
```

## List exchanges

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_exchanges -p {env.services.broker.vhost} \
  name type durable auto_delete \
  --formatter table
```

## List bindings for a queue

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl list_bindings -p {env.services.broker.vhost} \
  source_name destination_name routing_key \
  --formatter table | grep {queue_name}
```

## Cluster status

```bash
kubectl --context={env.context} exec -n {env.namespaces.infra} {broker_pod} -- \
  rabbitmqctl cluster_status --formatter table
```

## Via Management API (if port-forwarded to {env.services.broker.management_port})

To get credentials, use the secret specified in `env.services.broker.credentials_secret` (NOT other secrets that may exist for the same broker — they may have different passwords without vhost permissions).

### List queues
```bash
curl -s -u {user}:{password} http://localhost:{management_port}/api/queues/{vhost_encoded} | jq '.[] | {name, messages, consumers, state}'
```

### Queue details
```bash
curl -s -u {user}:{password} http://localhost:{management_port}/api/queues/{vhost_encoded}/{queue_name_encoded} | jq '{name, messages, messages_ready, messages_unacknowledged, consumers, state}'
```

### Overview (node health)
```bash
curl -s -u {user}:{password} http://localhost:{management_port}/api/overview | jq '{cluster_name, rabbitmq_version, queue_totals, message_stats}'
```
