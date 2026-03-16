# Docker Compose Adapter — port-forward

Docker Compose services typically expose ports directly. This adapter helps find and verify exposed ports.

## List services and their ports

```bash
docker compose ps --format "table {{.Name}}\t{{.Ports}}"
```

## Check if a port is already exposed

```bash
docker compose port {service} {container_port}
```

## Check if local port is in use

```bash
lsof -i :{local_port} 2>/dev/null
```

## Verify connection (TCP check)

```bash
nc -z localhost {local_port} 2>/dev/null && echo "Connection OK" || echo "Connection FAILED"
```

## Verify connection (HTTP health check)

```bash
curl -s -o /dev/null -w '%{http_code}' http://localhost:{local_port}/health
```

## If port is not exposed, use docker exec to create a tunnel

For database access:
```bash
docker compose exec -d {service} socat TCP-LISTEN:{exposed_port},fork TCP:localhost:{internal_port}
```

## Retrieve environment variable (credential)

```bash
docker compose exec {service} printenv {VAR_NAME}
```

Note: In Docker Compose, ports are usually mapped in the docker-compose.yml file. If the port is not exposed, consider adding a port mapping to the compose file or using `docker compose exec` for ad-hoc access.
