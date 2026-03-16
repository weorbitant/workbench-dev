# Jira Adapter — sprint-review

All commands use `{config.jira.cloud_id}` as the cloud identifier and `{config.jira.default_project}` as the project key.

## Discover MCP tools

Use ToolSearch to find the correct Jira MCP tool prefix:
```
ToolSearch: select:mcp__jira-*__jira_get_agile_boards
```
Store the discovered prefix as `{jira_prefix}`.

## Get boards

```
{jira_prefix}__jira_get_agile_boards(
  cloudId: "{config.jira.cloud_id}"
)
```

## Get sprints from board

```
{jira_prefix}__jira_get_sprints_from_board(
  cloudId: "{config.jira.cloud_id}",
  boardId: "{boardId}"
)
```

Find the sprint with state "future" or "active" (the next one to start).

## Get sprint issues

```
{jira_prefix}__jira_get_sprint_issues(
  cloudId: "{config.jira.cloud_id}",
  sprintId: "{sprintId}"
)
```

## Fetch individual ticket

```
{jira_prefix}__jira_get_issue(
  cloudId: "{config.jira.cloud_id}",
  issueIdOrKey: "{key}"
)
```

## Story points

Story points are stored in: `fields.{config.jira.story_points_field}`

Example: if `config.jira.story_points_field` is `customfield_XXXXX`, read `fields.customfield_XXXXX`.

## Search tickets by JQL

```
{jira_prefix}__jira_search(
  cloudId: "{config.jira.cloud_id}",
  jql: "project = {config.jira.default_project} AND sprint in openSprints()",
  fields: ["summary", "status", "issuetype", "assignee", "description", "{config.jira.story_points_field}", "issuelinks", "subtasks", "labels", "comment"]
)
```

## Add comment to ticket

```
{jira_prefix}__jira_add_comment(
  cloudId: "{config.jira.cloud_id}",
  issueIdOrKey: "{key}",
  body: "{comment_body}"
)
```

## Ticket status mapping

- Done / Closed / Resolved → exclude from analysis
- Sub-task → exclude (analyzed with parent)
- All other statuses → include

## Linked issues

Parse from `fields.issuelinks` array:
- `inwardIssue` with link type "is blocked by" → dependency
- `outwardIssue` with link type "blocks" → dependent ticket
