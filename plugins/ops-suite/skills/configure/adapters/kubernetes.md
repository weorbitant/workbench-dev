# Kubernetes Adapter — configure

Used by the `configure` skill when `orchestrator = kubernetes`.

## Detect contexts

Ask the user:
> "Do you want me to run `kubectl config get-contexts` to list available contexts?"
- If yes: run `kubectl config get-contexts 2>/dev/null` and list the results as options.
- If no: ask the user to type the context name(s) manually.

For each selected environment, ask which context maps to it.

## Detect namespaces

Ask the user:
> "Do you want me to run `kubectl get namespaces --context={ctx}` to list available namespaces?"
- If yes: run `kubectl get namespaces --context={ctx} -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null` and list the results.
- If no: ask the user to type the namespace names manually.

Ask the user to identify:
1. **Apps namespace** — where application deployments run
2. **Infra namespace** — where shared services run (broker, DB proxy, etc.)
   Suggest `shared-infra` if present in the list.

## Detect broker service

Ask the user:
> "Do you want me to run `kubectl get svc -n {infra_ns} --context={ctx}` to detect the broker service?"
- If yes: run `kubectl get svc -n {infra_ns} --context={ctx} -o name 2>/dev/null | grep -i rabbit | head -1` and use as default suggestion.
- If no: ask the user to type the service name manually.

## Detect database service

Ask the user:
> "Do you want me to run `kubectl get svc -n {infra_ns} --context={ctx}` to detect the database service?"
- If yes: run `kubectl get svc -n {infra_ns} --context={ctx} -o name 2>/dev/null | grep -iE 'pgbouncer|postgres|mysql' | head -1` and use as default suggestion.
- If no: ask the user to type the service name manually.

## Detect primary service

Ask the user:
> "Do you want me to run `kubectl get deployments -n {apps_ns} --context={ctx}` to list available deployments?"
- If yes: run `kubectl get deployments -n {apps_ns} --context={ctx} -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | head -4` and offer up to 4 results as options.
- If no: ask the user to type the service name manually.

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
