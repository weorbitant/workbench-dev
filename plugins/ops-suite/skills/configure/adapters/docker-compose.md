# Docker Compose Adapter — configure

Used by the `configure` skill when `orchestrator = docker-compose`.

## Environments

Docker Compose typically has a single environment (local), but may have multiple
compose files for different profiles. Ask the user:

1. > "What environment names do you want to configure?" (e.g. `local`, `dev`, `ci`)
2. > "What is the path to the compose file for **{env_name}**?" (e.g. `docker-compose.yml`, `docker-compose.dev.yml`)

Store as `{env.compose_file}`.

## Broker detection

Run silently:
```bash
grep -i 'rabbitmq\|redis\|kafka\|sqs' {env.compose_file} 2>/dev/null | head -5
```

Ask:
> "**{env_name}** — Broker service name in compose file?" (suggest detected or ask)

## Database detection

Run silently:
```bash
grep -iE 'postgres|mysql|mongo' {env.compose_file} 2>/dev/null | head -5
```

Ask:
> "**{env_name}** — Database service name in compose file?" (suggest detected)
> "**{env_name}** — Database port?" (default: 5432 / 3306 / 27017)
> "**{env_name}** — Default database name?"

## Primary service

Run silently:
```bash
grep -E '^  [a-z]' {env.compose_file} 2>/dev/null | head -4
```

Ask:
> "Primary application service name?" (list detected services as options)

## Service registry entry format

```yaml
{name}:
  service: {compose_service_name}
  port: {port}
  verify: "curl -s -o /dev/null -w '%{http_code}' http://localhost:{port}/health"
```

## Local ports

Docker Compose typically maps ports directly via the compose file. Ask:
> "**{env_name}** — Local port for database access?" (default: 5432)
