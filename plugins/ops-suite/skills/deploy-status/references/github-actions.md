# GitHub Actions CI Reference — deploy-status

All commands use the `gh` CLI. Authentication must already be set up. The repo is `{deploy.repo}` from config.

## Resolve image tag → commit metadata

The strategy depends on `deploy.image_tag_source`.

### When `image_tag_source: run-id`

The image tag is a GitHub Actions workflow run ID (numeric). Resolve it like this:

```bash
gh run view {image_tag} --repo {deploy.repo} \
  --json headSha,headBranch,createdAt,event,displayTitle,conclusion \
  --jq '{
    commit_sha:   .headSha[0:7],
    commit_full:  .headSha,
    branch:       .headBranch,
    deployed_at:  .createdAt,
    title:        .displayTitle,
    event:        .event,
    conclusion:   .conclusion
  }'
```

If `gh run view` returns 404 (run was deleted by retention policy), record fields as `unknown` and move on.

### When `image_tag_source: commit-sha`

The image tag is the commit SHA itself. Skip the run lookup and use it directly:

```bash
gh api repos/{deploy.repo}/commits/{image_tag} \
  --jq '{
    commit_sha:   .sha[0:7],
    commit_full:  .sha,
    deployed_at:  .commit.author.date,
    title:        (.commit.message | split("\n")[0]),
    author:       .commit.author.name
  }'
```

### When `image_tag_source: tag`

The image tag is a git tag. Resolve it:

```bash
gh api repos/{deploy.repo}/git/refs/tags/{image_tag} --jq '.object.sha' \
  | xargs -I {} gh api repos/{deploy.repo}/commits/{} --jq '{
      commit_sha:  .sha[0:7],
      commit_full: .sha,
      deployed_at: .commit.author.date,
      title:       (.commit.message | split("\n")[0]),
      author:      .commit.author.name
    }'
```

## Get author from a commit (when run-view did not include it)

```bash
gh api repos/{deploy.repo}/commits/{commit_full} --jq '.commit.author.name'
```

## Find the merged PR for a commit

```bash
gh api repos/{deploy.repo}/commits/{commit_full}/pulls \
  --jq '[.[] | select(.merged_at != null)] | first | {number, title}'
```

Returns `null` if the commit was pushed directly without a PR.

## Compare two commits (drift detection)

Used in Step 5 of the SKILL to detect ahead/behind/diverged.

```bash
gh api repos/{deploy.repo}/compare/{base_sha}...{head_sha} \
  --jq '{status, ahead_by, behind_by, total_commits}'
```

`status` values:
- `identical` — same commit
- `ahead` — `head` is ahead of `base`
- `behind` — `head` is behind `base`
- `diverged` — both have unique commits

## List commits between two SHAs (for drift detail)

```bash
gh api repos/{deploy.repo}/compare/{base_sha}...{head_sha} \
  --jq '.commits[-5:] | reverse | .[] | "\(.sha[0:7]) \(.commit.message | split("\n")[0])"'
```

Limited to the 5 most recent commits to keep the report compact.

## Deduplicate CI lookups

If the same `image_tag` appears in multiple environments, query the CI **once** and reuse the result. Keep an in-memory map `{image_tag → metadata}` while processing the env list.

## Rate limiting

`gh api` has a default budget of 5000 req/h. The commands above are cheap (≤ 3 calls per unique image tag + 1 compare per drift pair). For a typical 3-env setup with 1–2 unique tags, expect ≤ 10 API calls total.
