---
name: board-to-stories
description: "Use when extracting user stories from a visual board. Use when user says 'extract stories', 'genera user stories', 'procesa scope', 'board to stories', or shares a board URL."
argument-hint: "[board-url] [section]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Agent
  - AskUserQuestion
  - ToolSearch
  - Edit
  - Write
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `board_tool` — miro, excalidraw, or none
- `board_config.default_parent_page` — target page for publishing user stories
- `board_config.available_roles` — list of roles for user story format
- `issue_tracker` — for optional ticket creation

If `board_tool` is "none", tell the user no board tool is configured and stop.

## Step 1 — Load adapter

Read the adapter file at `${CLAUDE_PLUGIN_ROOT}/skills/board-to-stories/adapters/{board_tool}.md`.
If the adapter does not exist, tell the user that `{board_tool}` is not yet supported and stop.

## Step 2 — Parse arguments

From `$ARGUMENTS`:
1. Extract the board URL
2. Extract the section name (optional — to focus on a specific area of the board)

If no URL provided, ask the user.

## Phase 1 — Explore board

Use the adapter's commands to:

1. **Get board overview** — list all frames, sections, or areas
2. **Get content** — for the target section (or all sections if none specified)

For each item on the board, extract:
- Text content
- Position/grouping (which section it belongs to)
- Color coding (often indicates priority or category)
- Connections/arrows (indicate flows or dependencies)
- Sticky notes, cards, or text blocks

Present the board structure to the user and confirm which sections to process.

## Phase 2 — Cross with codebase

For each concept or feature mentioned on the board:

1. Search the codebase for existing implementations:
   - Grep for entity names, feature names, endpoint names
   - Check if the feature already exists (partially or fully)

2. Classify each item:
   - **New** — does not exist in codebase at all
   - **Enhancement** — exists but needs modifications
   - **Existing** — already implemented, no changes needed
   - **Unknown** — cannot determine from codebase alone

## Phase 3 — Generate user stories

For each board item that maps to a user story, generate using this format:

```
Como [{role}], quiero [{action}], para [{benefit}].
```

Where `{role}` comes from `{config.board_config.available_roles}`.

Classify each generated story:

### Defined stories
Stories with enough information to estimate and implement:
- Clear action
- Clear benefit
- Identifiable acceptance criteria

### Implicit stories
Stories that are implied by the board but not explicitly stated:
- Dependencies between features
- Technical prerequisites
- Data migration needs

### Blocked stories
Stories that cannot be defined without additional information:
- Missing business rules
- Undefined integrations
- Unclear user flows

For each story, generate:
- Title (summary)
- Description (using US template from references)
- Acceptance criteria (testable, specific)
- Estimated complexity (S, M, L, XL)
- Dependencies (other stories or external)

Read the US template at [references/us-template.md](references/us-template.md).

## Phase 4 — Publish

Ask the user where to publish the generated stories:

### Option 1: Notion page
If `{config.board_config.default_parent_page}` is set:
- Use ToolSearch to find Notion MCP tools
- Create a page under the configured parent page
- Format stories using the US template

### Option 2: Issue tracker
If `{config.issue_tracker}` is configured:
- Load the issue tracker adapter
- Create tickets for each defined story
- Link stories to each other based on dependencies

### Option 3: Local file
- Write stories to a markdown file in the project
- Path: `docs/user-stories/{date}-{board_section}.md`

### Option 4: Display only
- Show all stories in terminal format

## Output format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 BOARD TO STORIES: {board_name}
   Section: {section_name} | Stories: {count}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━ DEFINED ({count}) ━━━━━━━━━━━━━━━━━━━━━━━━━

US-001: {title}
  Como {role}, quiero {action}, para {benefit}.
  Complejidad: {S/M/L/XL}
  AC:
  - [ ] {criterion_1}
  - [ ] {criterion_2}

US-002: {title}
  ...

━━ IMPLICIT ({count}) ━━━━━━━━━━━━━━━━━━━━━━━━

US-I01: {title}
  Implícita por: {what implies this story}
  ...

━━ BLOCKED ({count}) ━━━━━━━━━━━━━━━━━━━━━━━━━

US-B01: {title}
  Bloqueada por: {reason}
  Pregunta: {what needs to be answered}

━━ ALREADY EXISTS ({count}) ━━━━━━━━━━━━━━━━━━

- {feature}: ya implementado en {file_path}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
