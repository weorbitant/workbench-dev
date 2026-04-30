# Azure Service Bus Adapter — queue-status

All commands use the Azure CLI (`az`). Ensure you are authenticated and have the correct subscription selected.

## List all queues in a namespace

```bash
az servicebus queue list --namespace-name {env.services.broker.name} --resource-group {env.resource_group} --output table
```

## Get queue details

```bash
az servicebus queue show --name {queue_name} --namespace-name {env.services.broker.name} --resource-group {env.resource_group} --output json | jq '{name, status, messageCount: .countDetails.activeMessageCount, deadLetterCount: .countDetails.deadLetterMessageCount, transferDeadLetterCount: .countDetails.transferDeadLetterMessageCount}'
```

## List queues with message counts

```bash
az servicebus queue list --namespace-name {env.services.broker.name} --resource-group {env.resource_group} --query '[].{Name:name, Active:countDetails.activeMessageCount, DLQ:countDetails.deadLetterMessageCount, Status:status}' --output table
```

## List topics

```bash
az servicebus topic list --namespace-name {env.services.broker.name} --resource-group {env.resource_group} --output table
```

## List subscriptions for a topic

```bash
az servicebus topic subscription list --topic-name {topic_name} --namespace-name {env.services.broker.name} --resource-group {env.resource_group} --output table
```

## Get subscription details (including DLQ count)

```bash
az servicebus topic subscription show --name {subscription_name} --topic-name {topic_name} --namespace-name {env.services.broker.name} --resource-group {env.resource_group} --query '{Name:name, Active:countDetails.activeMessageCount, DLQ:countDetails.deadLetterMessageCount, Status:status}' --output table
```

## Namespace health

```bash
az servicebus namespace show --name {env.services.broker.name} --resource-group {env.resource_group} --query '{Name:name, Status:status, Sku:sku.name, Location:location}' --output table
```
