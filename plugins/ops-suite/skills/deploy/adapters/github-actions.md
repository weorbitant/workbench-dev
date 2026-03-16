# GitHub Actions Adapter — deploy

All commands use `gh` CLI. Ensure you are authenticated and in the correct repository.

## Check PR state

```bash
gh pr view {pr_number} --json state,mergeCommit,title,headRefName --jq '{state,mergeCommit: .mergeCommit.oid,title,branch: .headRefName}'
```

## Find CI run for a commit

```bash
gh run list --commit {commit_sha} --json databaseId,status,conclusion,name --jq '.[] | {id: .databaseId, status, conclusion, name}'
```

## Get specific workflow run details

```bash
gh run view {run_id} --json databaseId,status,conclusion,headSha
```

## Find the build run ID (image tag source: run-id)

```bash
gh run list --commit {commit_sha} --workflow "{build_workflow}" --json databaseId,status,conclusion --jq '.[0]'
```

## Check if build succeeded

```bash
gh run view {run_id} --json conclusion --jq '.conclusion'
```

## List recent deployments

```bash
gh run list --workflow "{deploy_workflow}" --json databaseId,status,conclusion,createdAt,displayTitle --limit 5
```

## Trigger deploy workflow

```bash
gh workflow run "{deploy_workflow}" -f image_tag={image_tag} -f environment={environment}
```

## Trigger deploy workflow with ref

```bash
gh workflow run "{deploy_workflow}" --ref {ref} -f image_tag={image_tag} -f environment={environment}
```

## Monitor deploy workflow

```bash
gh run watch {run_id}
```

## Get deploy run status

```bash
gh run view {run_id} --json status,conclusion,jobs --jq '{status,conclusion,jobs: [.jobs[] | {name,status,conclusion}]}'
```

## View deploy workflow logs (on failure)

```bash
gh run view {run_id} --log-failed
```

## Check currently deployed version (via recent successful deploy)

```bash
gh run list --workflow "{deploy_workflow}" --status success --json databaseId,displayTitle,createdAt --limit 1 --jq '.[0]'
```

## Get PR details for context

```bash
gh pr view {pr_number} --json title,body,files --jq '{title,body,files: [.files[].path]}'
```
