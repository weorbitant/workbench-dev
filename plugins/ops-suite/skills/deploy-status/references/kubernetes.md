# Kubernetes Orchestrator Reference — deploy-status

All commands assume the deployment shares its name with the service. If your cluster uses a different convention, adjust the deployment name accordingly.

## Get deployed image tag

Returns the full `image:tag` of the first container.

```bash
kubectl --context={env.context} get deployment {service} -n {env.namespaces.apps} \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
```

Split on the last `:` to separate `image` from `tag`. The `tag` is what you pass to the CI reference in Step 4.

If the command fails with `NotFound`, the service is **not deployed** in that environment — record `NOT DEPLOYED` and continue.

## Get full deployment metadata (one call)

Returns image, replicas, conditions, and last-update timestamp in a single JSON blob.

```bash
kubectl --context={env.context} get deployment {service} -n {env.namespaces.apps} -o json \
  --ignore-not-found \
  | jq '{
      image:     .spec.template.spec.containers[0].image,
      desired:   .spec.replicas,
      ready:     (.status.readyReplicas // 0),
      available: (.status.availableReplicas // 0),
      condition: ([.status.conditions[]? | select(.type=="Available") | .status] | first // "Unknown"),
      progressing: ([.status.conditions[]? | select(.type=="Progressing") | .reason] | first // ""),
      last_update: ([.status.conditions[]? | select(.type=="Progressing") | .lastUpdateTime] | first // "")
    }'
```

Empty output means the deployment was not found.

## Map condition fields to the report

| Field combination | Report value |
|-------------------|--------------|
| `condition == "True"` | `Available` |
| `condition == "False"` and `progressing == "ProgressDeadlineExceeded"` | `Degraded` |
| `condition == "False"` (other) | `Unhealthy` |
| `condition == "Unknown"` or empty | `Unknown` |

## Replicas string

Format `ready/desired` (e.g. `3/3`). If `ready < desired`, prepend a warning flag in the report row.

## Get rollout history (optional, for richer drift output)

```bash
kubectl --context={env.context} rollout history deployment/{service} -n {env.namespaces.apps} \
  --revision=$(kubectl --context={env.context} get deployment {service} -n {env.namespaces.apps} \
    -o jsonpath='{.metadata.annotations.deployment\.kubernetes\.io/revision}')
```

This is optional — only call it if the user explicitly asks for rollout history.

## Querying multiple environments

Run one command per env in parallel using a single Bash call with `&` and `wait`, or by dispatching multiple tool calls in one assistant turn. Do not query envs sequentially when latency matters.
