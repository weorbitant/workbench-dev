# Figma Adapter — analyze-design

## Discover MCP tools

Use ToolSearch to find Figma MCP tools:
```
ToolSearch: +pencil get_screenshot
```
The Pencil MCP server provides Figma integration. Store the prefix as `{figma_prefix}`.

## URL parsing

Extract identifiers from Figma URLs:

- File URL: `https://www.figma.com/design/{file_key}/{file_name}?node-id={node_id}`
  - Extract `{file_key}` and `{node_id}` (URL-decode node_id: `1-2` means `1:2`)
- Prototype URL: `https://www.figma.com/proto/{file_key}/...`
  - Extract `{file_key}`

## Open document

First, open the Figma document:
```
{figma_prefix}__open_document(
  fileKey: "{file_key}"
)
```

## Get editor state

Check current state and available frames:
```
{figma_prefix}__get_editor_state()
```

## Get design context

Get the design structure and components:
```
{figma_prefix}__snapshot_layout(
  nodeId: "{node_id}"
)
```

This returns the layout tree with all elements, their types, positions, and properties.

## Get screenshot

Get a visual screenshot of a specific frame or node:
```
{figma_prefix}__get_screenshot(
  nodeId: "{node_id}"
)
```

## Get style guide

Retrieve design tokens and styles:
```
{figma_prefix}__get_style_guide()
```

## Get variables

Retrieve design variables (colors, spacing, etc.):
```
{figma_prefix}__get_variables()
```

## Search for specific properties

Find all elements with a specific property value:
```
{figma_prefix}__search_all_unique_properties(
  nodeId: "{node_id}",
  property: "{property_name}"
)
```

## Guidelines

Retrieve design guidelines if available:
```
{figma_prefix}__get_guidelines()
```

## Multiple screens

If the design has multiple top-level frames, list them from the editor state and either:
1. Analyze each frame sequentially
2. Ask the user which frames to focus on
