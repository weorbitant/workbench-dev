# ECS Adapter — port-forward

ECS port-forwarding uses AWS Systems Manager (SSM) Session Manager.

## Prerequisites

Ensure:
- AWS CLI v2 is installed
- Session Manager plugin is installed: `session-manager-plugin`
- The ECS task has SSM agent enabled

## Find running tasks for a service

```bash
aws ecs list-tasks --cluster {env.cluster} --service-name {service} --desired-status RUNNING --region {env.region} --query 'taskArns[0]' --output text
```

## Get task details (runtime ID)

```bash
aws ecs describe-tasks --cluster {env.cluster} --tasks {task_arn} --region {env.region} --query 'tasks[0].containers[0].runtimeId' --output text
```

## Start port-forward session via SSM

```bash
aws ssm start-session --target ecs:{env.cluster}_{task_id}_{runtime_id} --document-name AWS-StartPortForwardingSession --parameters '{"portNumber":["{remote_port}"],"localPortNumber":["{local_port}"]}' --region {env.region}
```

## Check if local port is in use

```bash
lsof -i :{local_port} 2>/dev/null
```

## Verify connection (TCP check)

```bash
nc -z localhost {local_port} 2>/dev/null && echo "Connection OK" || echo "Connection FAILED"
```

## Alternative: Use ECS Exec for ad-hoc access

```bash
aws ecs execute-command --cluster {env.cluster} --task {task_arn} --container {container_name} --interactive --command "/bin/sh" --region {env.region}
```
