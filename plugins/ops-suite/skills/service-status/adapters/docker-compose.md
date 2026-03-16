# Docker Compose Adapter — service-status

All commands assume docker compose is available in the project directory.

## List containers for a specific service

```bash
docker compose ps {service}
```

## List all containers

```bash
docker compose ps
```

## Identify unhealthy containers

```bash
docker compose ps --filter "status=exited" --filter "status=restarting" --filter "status=dead"
```

## Container details and events

```bash
docker inspect {container} --format '{{json .State}}' | jq .
```

## Restart counts

```bash
docker inspect {container} --format '{{.RestartCount}}'
```

## Resource usage

```bash
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep {service}
```

## Environment variables (non-secret)

```bash
docker compose exec {service} env | grep -iv "pass\|secret\|token\|key" | sort
```

## Check image/version

```bash
docker compose images {service}
```

## Service restart (ALWAYS ask confirmation first)

```bash
docker compose restart {service}
```

## Recreate service (ALWAYS ask confirmation first)

```bash
docker compose up -d --force-recreate {service}
```
