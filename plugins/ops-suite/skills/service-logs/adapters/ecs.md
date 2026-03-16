# ECS Adapter — service-logs

ECS logs are typically stored in CloudWatch Logs. Ensure the correct AWS profile and region are configured.

## Find log group for a service

```bash
aws logs describe-log-groups --log-group-name-prefix "/ecs/{service}" --region {env.region} --output table
```

## Recent logs (last 30 minutes)

```bash
aws logs filter-log-events --log-group-name "{log_group}" --start-time $(date -d '-30 minutes' +%s000) --region {env.region} --output text
```

On macOS:
```bash
aws logs filter-log-events --log-group-name "{log_group}" --start-time $(date -v-30M +%s000) --region {env.region} --output text
```

## Search for a specific pattern

```bash
aws logs filter-log-events --log-group-name "{log_group}" --filter-pattern "{pattern}" --start-time $(date -v-1H +%s000) --region {env.region} --output text
```

## Recent errors

```bash
aws logs filter-log-events --log-group-name "{log_group}" --filter-pattern "?ERROR ?Exception ?FATAL" --start-time $(date -v-1H +%s000) --region {env.region} --output text
```

## Follow logs (live tail)

```bash
aws logs tail "{log_group}" --follow --region {env.region}
```

## Logs with specific time range

```bash
aws logs filter-log-events --log-group-name "{log_group}" --start-time {start_epoch_ms} --end-time {end_epoch_ms} --region {env.region} --output text
```
