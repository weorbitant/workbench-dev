# GitHub Issues Adapter — clarify-ticket

> **Stub adapter.** GitHub Issues support is planned but not yet implemented.
> Contributions welcome — follow the Jira adapter as a reference.

## URL parsing

Extract issue number from GitHub URLs:
- Pattern: `https://github.com/{owner}/{repo}/issues/{number}` → extract `{owner}`, `{repo}`, `{number}`

## Fetch ticket

```bash
gh issue view {number} --repo {owner}/{repo} --json title,body,state,labels,assignees,comments
```

## Add comment

```bash
gh issue comment {number} --repo {owner}/{repo} --body "{comment_body}"
```

## Edit ticket

```bash
gh issue edit {number} --repo {owner}/{repo} --body "{new_description}"
```
