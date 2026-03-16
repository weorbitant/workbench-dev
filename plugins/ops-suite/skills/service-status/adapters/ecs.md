# ECS Adapter — service-status

All commands use AWS CLI. Ensure the correct AWS profile and region are configured.

## List services in cluster

```bash
aws ecs list-services --cluster {env.cluster} --region {env.region} --output table
```

## Describe a specific service

```bash
aws ecs describe-services --cluster {env.cluster} --services {service} --region {env.region} --output table
```

## List tasks for a service

```bash
aws ecs list-tasks --cluster {env.cluster} --service-name {service} --region {env.region} --output table
```

## Describe tasks (health and status)

```bash
aws ecs describe-tasks --cluster {env.cluster} --tasks {task_arn} --region {env.region} --query 'tasks[*].{TaskArn:taskArn,Status:lastStatus,Health:healthStatus,StoppedReason:stoppedReason}' --output table
```

## Check running count vs desired

```bash
aws ecs describe-services --cluster {env.cluster} --services {service} --region {env.region} --query 'services[0].{Desired:desiredCount,Running:runningCount,Pending:pendingCount}' --output table
```

## Recent events for a service

```bash
aws ecs describe-services --cluster {env.cluster} --services {service} --region {env.region} --query 'services[0].events[:10]' --output table
```

## Force new deployment (ALWAYS ask confirmation first)

```bash
aws ecs update-service --cluster {env.cluster} --service {service} --force-new-deployment --region {env.region}
```

## Check task definition (image version)

```bash
aws ecs describe-task-definition --task-definition {task_definition} --region {env.region} --query 'taskDefinition.containerDefinitions[*].{Name:name,Image:image}' --output table
```
