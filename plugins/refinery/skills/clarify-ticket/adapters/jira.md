# Jira Adapter — clarify-ticket

All commands use `{config.jira.cloud_id}` as the cloud identifier.

## Discover MCP tools

Use ToolSearch to find the correct Jira MCP tool prefix:
```
ToolSearch: select:mcp__jira-*__jira_get_issue
```
The tool name varies by installation (e.g. `mcp__jira-myorg__jira_get_issue`). Use ToolSearch to resolve the exact name, then use that prefix for all subsequent calls.

Store the discovered prefix as `{jira_prefix}`.

## URL parsing

Extract ticket key from Jira URLs:
- Pattern: `https://{domain}/browse/{KEY}` → extract `{KEY}`
- Pattern: `https://{domain}/jira/software/projects/{PROJECT}/boards/{N}/backlog?selectedIssue={KEY}` → extract `{KEY}`

## Fetch ticket

```
{jira_prefix}__jira_get_issue(
  cloudId: "{config.jira.cloud_id}",
  issueIdOrKey: "{key}"
)
```

## Add comment

```
{jira_prefix}__jira_add_comment(
  cloudId: "{config.jira.cloud_id}",
  issueIdOrKey: "{key}",
  body: "{comment_body}"
)
```

## Edit ticket (update description)

```
{jira_prefix}__jira_update_issue(
  cloudId: "{config.jira.cloud_id}",
  issueIdOrKey: "{key}",
  fields: {
    "description": "{new_description}"
  }
)
```

## Get comments

Comments are included in the `jira_get_issue` response. Parse them from the `fields.comment.comments` array.
