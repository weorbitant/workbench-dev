# Kubernetes Adapter — configure

Used by the `configure` skill when `orchestrator = kubernetes`.

## Detect contexts

```bash
kubectl config get-contexts 2>/dev/null
```

List all contexts. For each selected environment, ask which context maps to it.

## Detect namespaces

```bash
kubectl get namespaces --context={ctx} \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null
```

Ask the user to identify:
1. **Apps namespace** — where application deployments run
2. **Infra namespace** — where shared services run (broker, DB proxy, etc.)
   Suggest `shared-infra` if present in the list.

## Detect broker service

```bash
kubectl get svc -n {infra_ns} --context={ctx} \
  -o name 2>/dev/null | grep -i rabbit | head -1
```

Use as default suggestion for the broker service name.

## Detect database service

```bash
kubectl get svc -n {infra_ns} --context={ctx} \
  -o name 2>/dev/null | grep -iE 'pgbouncer|postgres|mysql' | head -1
```

Use as default suggestion for the database service name.

## Detect primary service

```bash
kubectl get deployments -n {apps_ns} --context={ctx} \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | head -4
```

Offer up to 4 results as options for the primary service name.

## Local port-forward ports

Suggest sequential defaults starting at `16432`:
- dev → 16432
- staging → 16433
- prod → 16434

Ask the user to confirm or provide a custom port per environment.

## Service registry entry format

```yaml
{name}:
  namespace: {ns}
  service: svc/{svc}
  port: {port}
  verify: "curl -s -o /dev/null -w '%{http_code}' http://localhost:{port}/health"
```
