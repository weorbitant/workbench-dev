# Notion Adapter — analyze-docs

## Discover MCP tools

Use ToolSearch to find Notion MCP tools:
```
ToolSearch: +notion search
```
Store the discovered prefix as `{notion_prefix}`.

## Search pages

```
{notion_prefix}__notion-search(
  query: "{search_term}",
  filter: {
    "value": "page",
    "property": "object"
  }
)
```

## Fetch specific page

```
{notion_prefix}__notion-fetch(
  url: "{page_url}"
)
```

Or by page ID:
```
{notion_prefix}__notion-fetch(
  url: "https://www.notion.so/{page_id}"
)
```

## URL parsing

Extract page ID from Notion URLs:
- `https://www.notion.so/{workspace}/{title}-{page_id}` → extract last 32 hex chars as `{page_id}`
- `https://www.notion.so/{page_id}` → extract `{page_id}`

## Parse content

Notion returns blocks. Extract:
- Text content from paragraph, heading, bulleted_list_item, numbered_list_item blocks
- Table data from table and table_row blocks
- Code from code blocks
- Toggle content (expand toggles to get nested content)
- Links and mentions

## Search in database

If the documentation is stored in a Notion database:
```
{notion_prefix}__notion-search(
  query: "{search_term}",
  filter: {
    "value": "database",
    "property": "object"
  }
)
```

## Get child pages

Pages in Notion can have sub-pages. The fetch response includes child references. Follow them to get complete documentation trees.
