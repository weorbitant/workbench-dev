# Penpot Adapter — analyze-design

> **Stub adapter.** Penpot support is planned but not yet implemented.
> Contributions welcome — follow the Figma adapter as a reference.

## URL parsing

Extract identifiers from Penpot URLs:
- Pattern: `https://{instance}/view/{project_id}/{file_id}?page-id={page_id}`
- Extract `{project_id}`, `{file_id}`, `{page_id}`

## Get design context

```
# TODO: Implement using Penpot API or MCP tools when available
# penpot_get_file(fileId: "{file_id}", pageId: "{page_id}")
```

## Get screenshot

```
# TODO: Implement using Penpot export API when available
# penpot_export_frame(fileId: "{file_id}", frameId: "{frame_id}", format: "png")
```

## Get components

```
# TODO: Implement using Penpot API when available
# penpot_get_components(fileId: "{file_id}")
```
