# GitLab CI Adapter — deploy

All commands use `glab` CLI or `curl` with the GitLab API. Ensure you are authenticated.

## Check MR state

```bash
glab mr view {mr_number} --output json | jq '{state,merge_commit_sha,title,source_branch}'
```

## Find pipeline for a commit

```bash
glab ci list --commit {commit_sha} --output json | jq '.[0] | {id,status,ref}'
```

## Check if pipeline succeeded

```bash
glab ci view {pipeline_id} --output json | jq '.status'
```

## List recent deployments

```bash
glab ci list --status success --output json | jq '.[:5] | .[] | {id,status,created_at,ref}'
```

## Trigger deploy pipeline

```bash
glab ci run --ref {ref} --variables "IMAGE_TAG={image_tag},ENVIRONMENT={environment}"
```

## Monitor pipeline

```bash
glab ci view {pipeline_id}
```

## View pipeline logs (on failure)

```bash
glab ci trace {pipeline_id}
```

## Get MR details

```bash
glab mr view {mr_number}
```
