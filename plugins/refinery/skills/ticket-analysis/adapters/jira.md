# Jira Adapter — ticket-analysis

All commands use `{config.jira.cloud_id}` as the cloud identifier.

## Discover MCP tools

Use ToolSearch to find the correct Jira MCP tool prefix:
```
ToolSearch: select:mcp__jira-*__jira_get_issue
```
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

Parse from response:
- `fields.summary` — title
- `fields.description` — description (ADF format, extract text)
- `fields.status.name` — status
- `fields.issuetype.name` — type
- `fields.assignee.displayName` — assignee
- `fields.labels` — labels
- `fields.issuelinks` — linked issues
- `fields.comment.comments` — comments
- `fields.{config.jira.story_points_field}` — story points

## Add comment

```
{jira_prefix}__jira_add_comment(
  cloudId: "{config.jira.cloud_id}",
  issueIdOrKey: "{key}",
  body: "{comment_body}"
)
```

## Update ticket

```
{jira_prefix}__jira_update_issue(
  cloudId: "{config.jira.cloud_id}",
  issueIdOrKey: "{key}",
  fields: {
    "description": "{new_description}"
  }
)
```

## Create subtask

```
{jira_prefix}__jira_create_issue(
  cloudId: "{config.jira.cloud_id}",
  projectKey: "{config.jira.default_project}",
  issueType: "Sub-task",
  summary: "{summary}",
  description: "{description}",
  parent: "{parent_key}"
)
```

## Search related tickets

```
{jira_prefix}__jira_search(
  cloudId: "{config.jira.cloud_id}",
  jql: "project = {config.jira.default_project} AND text ~ '{search_term}'",
  fields: ["summary", "status", "description"]
)
```
