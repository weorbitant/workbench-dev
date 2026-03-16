# Linear Adapter — clarify-ticket

> **Stub adapter.** Linear support is planned but not yet implemented.
> Contributions welcome — follow the Jira adapter as a reference.

## Required configuration

- `config.linear.team_id` — the Linear team identifier

## URL parsing

Extract issue identifier from Linear URLs:
- Pattern: `https://linear.app/{workspace}/issue/{ID}` → extract `{ID}`

## Fetch ticket

```
# TODO: Implement using Linear MCP tools when available
# linear_get_issue(teamId: "{config.linear.team_id}", issueId: "{key}")
```

## Add comment

```
# TODO: Implement using Linear MCP tools when available
# linear_add_comment(issueId: "{key}", body: "{comment_body}")
```

## Edit ticket

```
# TODO: Implement using Linear MCP tools when available
# linear_update_issue(issueId: "{key}", description: "{new_description}")
```
