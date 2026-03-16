# Kubernetes Adapter — service-status

All commands use `{env.context}` for the kubectl context and `{env.namespaces.apps}` for the application namespace.

## List pods for a specific service

```bash
kubectl --context={env.context} get pods -n {env.namespaces.apps} | grep {service}
```

## List all pods in namespace

```bash
kubectl --context={env.context} get pods -n {env.namespaces.apps} -o wide
```

## Identify unhealthy pods

```bash
kubectl --context={env.context} get pods -n {env.namespaces.apps} | grep -v "Running\|Completed"
```

## Pod details and events

```bash
kubectl --context={env.context} describe pod {pod} -n {env.namespaces.apps} | tail -30
```

## Restart counts

```bash
kubectl --context={env.context} get pods -n {env.namespaces.apps} -o custom-columns=\
NAME:.metadata.name,STATUS:.status.phase,RESTARTS:.status.containerStatuses[0].restartCount,\
AGE:.metadata.creationTimestamp | grep {service}
```

## Resource usage

```bash
kubectl --context={env.context} top pods -n {env.namespaces.apps} | grep {service}
```

## Environment variables (non-secret)

```bash
kubectl --context={env.context} exec -n {env.namespaces.apps} {pod} -- env | grep -iv "pass\|secret\|token\|key" | sort
```

## Check image/version

```bash
kubectl --context={env.context} get pod {pod} -n {env.namespaces.apps} -o jsonpath='{.spec.containers[0].image}'
```

## Deployment status

```bash
kubectl --context={env.context} get deploy -n {env.namespaces.apps} | grep {service}
```

## Rolling restart (ALWAYS ask confirmation first)

```bash
kubectl --context={env.context} rollout restart deployment/{deployment} -n {env.namespaces.apps}
```

## Rollout history

```bash
kubectl --context={env.context} rollout history deployment/{deployment} -n {env.namespaces.apps}
```

## Rollout status (watch)

```bash
kubectl --context={env.context} rollout status deployment/{deployment} -n {env.namespaces.apps}
```
