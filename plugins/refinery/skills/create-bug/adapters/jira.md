# Jira Adapter — create-bug

All commands use `{config.jira.cloud_id}` as the cloud identifier and `{config.jira.default_project}` as the project key.

## Discover MCP tools

Use ToolSearch to find the correct Jira MCP tool prefix:
```
ToolSearch: select:mcp__jira-*__jira_create_issue
```
Store the discovered prefix as `{jira_prefix}`.

## Search for epic (or any issue)

```
{jira_prefix}__jira_search(
  cloudId: "{config.jira.cloud_id}",
  jql: "project = {config.jira.default_project} AND key = {config.jira.default_bug_epic}",
  fields: ["summary", "status"]
)
```

## Search for user (to assign)

```
{jira_prefix}__jira_search(
  cloudId: "{config.jira.cloud_id}",
  jql: "project = {config.jira.default_project} AND assignee = '{name}'",
  fields: ["assignee"]
)
```

Alternatively, look up the account ID from a known ticket's assignee field.

## Create bug issue

```
{jira_prefix}__jira_create_issue(
  cloudId: "{config.jira.cloud_id}",
  projectKey: "{config.jira.default_project}",
  issueType: "Bug",
  summary: "{summary}",
  description: "{description}",
  parent: "{config.jira.default_bug_epic}"
)
```

Note: If `parent` is empty or not configured, omit the parent field.

## Edit issue (assign, set priority, add labels)

```
{jira_prefix}__jira_update_issue(
  cloudId: "{config.jira.cloud_id}",
  issueIdOrKey: "{key}",
  fields: {
    "assignee": { "accountId": "{accountId}" },
    "priority": { "name": "{priority}" },
    "labels": ["{label1}", "{label2}"]
  }
)
```

## Get issue (to verify creation)

```
{jira_prefix}__jira_get_issue(
  cloudId: "{config.jira.cloud_id}",
  issueIdOrKey: "{key}"
)
```
