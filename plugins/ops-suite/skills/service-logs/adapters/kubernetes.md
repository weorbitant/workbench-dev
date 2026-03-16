# Kubernetes Adapter — service-logs

All commands use `{env.context}` for the kubectl context and `{env.namespaces.apps}` for the application namespace.

## Find pods for a service

```bash
kubectl --context={env.context} get pods -n {env.namespaces.apps} | grep {service}
```

## Recent errors (last 200 lines, filtered)

```bash
kubectl --context={env.context} logs {pod} -n {env.namespaces.apps} --tail=200 | grep -iE "error|exception|fail|fatal|panic"
```

## Recent logs (last N lines, unfiltered)

```bash
kubectl --context={env.context} logs {pod} -n {env.namespaces.apps} --tail={lines}
```

## Logs since a time period

```bash
kubectl --context={env.context} logs {pod} -n {env.namespaces.apps} --since={duration}
```

Example durations: `1h`, `30m`, `2h`, `24h`

## Search for a specific pattern

```bash
kubectl --context={env.context} logs {pod} -n {env.namespaces.apps} --tail=500 | grep -i "{pattern}"
```

## Context around errors (5 lines before and after)

```bash
kubectl --context={env.context} logs {pod} -n {env.namespaces.apps} --tail=500 | grep -B5 -A5 -i "{pattern}"
```

## Entity-specific errors

```bash
kubectl --context={env.context} logs {pod} -n {env.namespaces.apps} --tail=1000 | grep -i "{entity_id}"
```

## Follow logs (live tail)

```bash
kubectl --context={env.context} logs {pod} -n {env.namespaces.apps} -f --tail=50
```

## All pods logs (all replicas of a deployment)

```bash
kubectl --context={env.context} logs -l app={service} -n {env.namespaces.apps} --tail=100
```

Note: The label selector `app={service}` is a convention. Adjust the label key if your deployments use a different selector (e.g. `app.kubernetes.io/name`).

## Previous container logs (after a restart/crash)

```bash
kubectl --context={env.context} logs {pod} -n {env.namespaces.apps} --previous --tail=100
```

## Logs with timestamps

```bash
kubectl --context={env.context} logs {pod} -n {env.namespaces.apps} --timestamps --tail=200
```

## Count errors by type

```bash
kubectl --context={env.context} logs {pod} -n {env.namespaces.apps} --tail=1000 | grep -iE "error|exception" | sort | uniq -c | sort -rn | head -20
```
