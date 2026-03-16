# Docker Compose Adapter — service-logs

## Recent errors (last 200 lines, filtered)

```bash
docker compose logs {service} --tail=200 | grep -iE "error|exception|fail|fatal|panic"
```

## Recent logs (last N lines, unfiltered)

```bash
docker compose logs {service} --tail={lines}
```

## Logs since a time period

```bash
docker compose logs {service} --since={duration}
```

Example durations: `1h`, `30m`, `2h`, `24h`

## Search for a specific pattern

```bash
docker compose logs {service} --tail=500 | grep -i "{pattern}"
```

## Context around errors

```bash
docker compose logs {service} --tail=500 | grep -B5 -A5 -i "{pattern}"
```

## Follow logs (live tail)

```bash
docker compose logs {service} -f --tail=50
```

## Logs with timestamps

```bash
docker compose logs {service} --timestamps --tail=200
```

## Count errors by type

```bash
docker compose logs {service} --tail=1000 | grep -iE "error|exception" | sort | uniq -c | sort -rn | head -20
```
