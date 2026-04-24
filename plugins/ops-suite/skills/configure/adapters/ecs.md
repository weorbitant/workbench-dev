# ECS Adapter — configure

Used by the `configure` skill when `orchestrator = ecs`.

## Prerequisites

Requires AWS CLI configured with appropriate credentials:
```bash
aws sts get-caller-identity 2>/dev/null
```

If this fails, tell the user to run `aws configure` or set `AWS_PROFILE` first.

## Environments

Ask per environment:
1. > "**{env_name}** — AWS region?" (e.g. `eu-west-1`, `us-east-1`)
2. > "**{env_name}** — ECS cluster name?"

Store as `{env.region}` and `{env.cluster}`.

## Detect services

Run silently:
```bash
aws ecs list-services --cluster {env.cluster} --region {env.region} \
  --query 'serviceArns[*]' --output text 2>/dev/null | tr '\t' '\n' | \
  sed 's|.*/||' | head -10
```

Show detected services to the user as context.

## Broker

ECS brokers are typically external (Amazon SQS, Amazon MQ, or MSK). Ask:
- If broker = `sqs`: ask for the SQS queue name prefix and AWS region
- If broker = `rabbitmq` (Amazon MQ): ask for the broker endpoint and credentials secret ARN
- If broker = `kafka` (MSK): ask for the bootstrap servers

## Database

RDS or Aurora is typical. Ask per environment:
1. > "**{env_name}** — RDS endpoint or Secrets Manager ARN for DB credentials?"
2. > "**{env_name}** — Database port?" (default: 5432 / 3306)
3. > "**{env_name}** — Default database name?"

## Primary service

Ask:
> "Primary application service name?" (list detected ECS services as options)

## Local port-forward

ECS does not support kubectl port-forward natively. For local DB access, the
`port-forward` skill uses SSM Session Manager or an SSH tunnel. Ask:
> "**{env_name}** — Local port for database access via SSM tunnel?" (default: 15432)

## Service registry entry format

```yaml
{name}:
  cluster: {cluster}
  service: {ecs_service_name}
  region: {region}
  port: {port}
```
