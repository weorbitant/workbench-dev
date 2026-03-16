# Miro Adapter — board-to-stories

## Discover MCP tools

Use ToolSearch to find Miro MCP tools:
```
ToolSearch: miro board context
```

If no Miro MCP is available, use the WebFetch tool with the Miro REST API.

## URL parsing

Extract board ID from Miro URLs:
- Pattern: `https://miro.com/app/board/{board_id}/` → extract `{board_id}`
- Pattern: `https://miro.com/app/board/{board_id}/?moveToWidget={widget_id}` → extract both

## Explore board context

```
{miro_prefix}__context_explore(
  boardId: "{board_id}"
)
```

This returns the board structure with frames, sections, and high-level content.

## List all items

```
{miro_prefix}__board_list_items(
  boardId: "{board_id}",
  type: "all"
)
```

Filter by type if needed:
- `sticky_note` — individual ideas or requirements
- `card` — structured cards with titles and descriptions
- `text` — free text blocks
- `frame` — grouping containers (sections)
- `shape` — diagrams, flows
- `connector` — arrows/connections between items

## List items in a specific frame

```
{miro_prefix}__board_list_items(
  boardId: "{board_id}",
  parentId: "{frame_id}"
)
```

## Read table data

If the board contains tables:
```
{miro_prefix}__table_list_rows(
  boardId: "{board_id}",
  tableId: "{table_id}"
)
```

## Get specific item

```
{miro_prefix}__board_list_items(
  boardId: "{board_id}",
  itemId: "{item_id}"
)
```

## Interpret board structure

When processing Miro content:
1. **Frames** define sections/themes — use frame titles as section headers
2. **Color coding** on sticky notes usually indicates category:
   - Identify the color scheme by looking at patterns
   - Ask the user to confirm color meanings if unclear
3. **Connectors** (arrows) indicate dependencies or flows
4. **Position** — items grouped spatially often relate to each other
5. **Tags** — Miro items can have tags for additional categorization
