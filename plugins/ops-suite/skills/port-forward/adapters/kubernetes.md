# Kubernetes Adapter — port-forward

All commands use `{env.context}` for the kubectl context.

## Search for services in a namespace

```bash
kubectl --context={env.context} get svc -n {env.namespaces.apps} | grep {service}
```

## Search for services in infra namespace

```bash
kubectl --context={env.context} get svc -n {env.namespaces.infra} | grep {service}
```

## List all services (to help user find the right one)

```bash
kubectl --context={env.context} get svc -n {namespace}
```

## Find pods for a service

```bash
kubectl --context={env.context} get pods -n {namespace} | grep {service}
```

## Check if local port is in use

```bash
lsof -i :{local_port} 2>/dev/null
```

## Port-forward a service (background)

```bash
kubectl --context={env.context} port-forward svc/{service} {local_port}:{remote_port} -n {namespace} &
```

## Port-forward a specific pod (background)

```bash
kubectl --context={env.context} port-forward {pod} {local_port}:{remote_port} -n {namespace} &
```

## Verify connection (TCP check)

```bash
nc -z localhost {local_port} 2>/dev/null && echo "Connection OK" || echo "Connection FAILED"
```

## Verify connection (HTTP health check)

```bash
curl -s -o /dev/null -w '%{http_code}' http://localhost:{local_port}/health
```

## Retrieve secret (generic pattern)

```bash
kubectl --context={env.context} get secret {secret_name} -n {namespace} -o jsonpath='{.data.{key}}' | base64 -d
```

## List secrets in namespace

```bash
kubectl --context={env.context} get secrets -n {namespace} | grep {service}
```

## Kill existing port-forward

```bash
lsof -ti :{local_port} | xargs kill 2>/dev/null
```

## Database connection string templates

PostgreSQL:
```
postgresql://{user}:{password}@localhost:{local_port}/{database}
```

RabbitMQ Management UI:
```
http://localhost:{local_port}
```

Generic HTTP service:
```
http://localhost:{local_port}
```
