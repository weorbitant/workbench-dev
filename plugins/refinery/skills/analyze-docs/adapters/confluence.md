# Confluence Adapter — analyze-docs

Each Confluence source has its own `{source.cloud_id}` from the config.

## Discover MCP tools

Confluence is typically accessed through the Jira MCP server or a dedicated Confluence MCP. Use ToolSearch:
```
ToolSearch: confluence search fetch
```

If no dedicated Confluence MCP is available, use the WebFetch tool to access the Confluence REST API.

## Search pages (CQL)

Using Confluence REST API via WebFetch:
```
WebFetch: https://{source.cloud_id}/wiki/rest/api/content/search?cql=text~"{search_term}" OR title~"{search_term}"&limit=10&expand=body.storage,version
```

Or if a Confluence MCP tool is available:
```
{confluence_prefix}__search(
  cloudId: "{source.cloud_id}",
  cql: "text ~ \"{search_term}\" OR title ~ \"{search_term}\"",
  limit: 10
)
```

## Fetch specific page

By page ID:
```
WebFetch: https://{source.cloud_id}/wiki/rest/api/content/{page_id}?expand=body.storage,version,ancestors
```

By URL: extract page ID from Confluence URL patterns:
- `https://{domain}/wiki/spaces/{space}/pages/{page_id}/{title}` → extract `{page_id}`
- `https://{domain}/wiki/x/{short_id}` → resolve short link

## Parse content

Confluence stores content in XHTML storage format. Extract:
- Plain text content (strip HTML tags)
- Table data (preserve structure)
- Code blocks
- Links to other pages
- Attached files list

## Search by label

```
WebFetch: https://{source.cloud_id}/wiki/rest/api/content/search?cql=label="{label}"&limit=10
```

## Get page children (for exploring structure)

```
WebFetch: https://{source.cloud_id}/wiki/rest/api/content/{page_id}/child/page?limit=25
```
