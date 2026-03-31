# refinery

Analyze tickets, designs, documentation, and code — all from Claude Code — to answer one question: **is this ready to implement?**

## What problem does this solve?

A ticket arrives in sprint. To know if it's ready, you need to:

- Read the ticket (Jira/Linear)
- Check the design (Figma/Penpot)
- Search for business rules (Confluence/Notion)
- Look at the codebase (entities, endpoints, migrations)
- Cross-reference everything

That's four tools, twenty minutes, and you probably still missed something.

refinery does this systematically. It reads all sources, cross-references them, and tells you exactly what's missing, contradictory, or undefined.

```
You:    "/refinery:clarify-ticket PROJ-123"
Claude: 3 blockers:
        1. No acceptance criteria defined
        2. "Assignment" entity mentioned but not in data model
        3. Error states not covered in design

        5 nice-to-haves:
        1. No performance requirements specified
        2. Pagination not defined for list view
        ...
```

## Quick start

**1. Add the plugin** to your Claude Code settings:

```json
{
  "plugins": [
    "/path/to/workbench-dev/plugins/refinery"
  ]
}
```

**2. Create your config:**

```bash
cp config.example.yaml config.yaml
```

**3. Fill in your tools:**

```yaml
issue_tracker: jira
jira:
  cloud_id: "myorg.atlassian.net"
  default_project: "PROJ"

design_tool: figma                # figma | penpot | none

docs_sources:
  - type: confluence
    cloud_id: "myorg.atlassian.net"

communication:
  tool: slack                     # slack | teams | discord | none
```

**4. Restart Claude Code.** Skills are available immediately.

## Skills

### Ticket analysis

| Skill | Command | What it does |
|-------|---------|-------------|
| **clarify-ticket** | `/refinery:clarify-ticket PROJ-123` | Quick scan: blockers + nice-to-haves |
| **ticket-analysis** | `/refinery:ticket-analysis PROJ-123` | Deep analysis: ticket + design + docs + code in parallel |
| **create-bug** | `/refinery:create-bug "description"` | Structured bug report with root cause |

**clarify-ticket** is your daily driver. Fast, focused, identifies what's missing.

**ticket-analysis** is the heavy hitter. Launches 4 parallel agents that analyze design, documentation, data model, and feasibility simultaneously. Use it for complex tickets before sprint commitment.

### Sprint management

| Skill | Command | What it does |
|-------|---------|-------------|
| **sprint-review** | `/refinery:sprint-review BOARD-1` | 8 automated checks on sprint readiness |

Checks include: story point distribution, ticket completeness, vague language detection, dependency mapping, design coverage, documentation coverage, and more.

### Design and documentation

| Skill | Command | What it does |
|-------|---------|-------------|
| **analyze-design** | `/refinery:analyze-design <figma-url>` | Extract fields, states, actions from designs |
| **analyze-docs** | `/refinery:analyze-docs "search term"` | Search Confluence/Notion for business rules |
| **analyze-data-model** | `/refinery:analyze-data-model Client` | Trace entity through codebase |
| **analyze-feasibility** | `/refinery:analyze-feasibility "approach"` | Evaluate technical approach vs codebase |

These skills work standalone but are most powerful when combined via `ticket-analysis`, which orchestrates them in parallel.

### Architecture and communication

| Skill | Command | What it does |
|-------|---------|-------------|
| **adr** | `/refinery:adr "topic"` | Create/update Architecture Decision Records |
| **board-to-stories** | `/refinery:board-to-stories <miro-url>` | Extract user stories from visual boards |
| **notify-team** | `/refinery:notify-team #channel "message"` | Draft messages for Slack/Teams/Discord |

## Workflows

See [docs/workflows.md](docs/workflows.md) for step-by-step recipes:

- [New ticket arrives](#1-new-ticket-arrives) — Quick triage
- [Sprint planning](#2-sprint-planning) — Full sprint review
- [Deep ticket analysis](#3-deep-ticket-analysis) — Cross-source investigation
- [Architecture decisions](#4-architecture-decisions) — ADR workflow
- [Design handoff](#5-design-handoff) — Design-to-code verification
- [Bug reporting](#6-bug-reporting) — Structured bug creation

## How skills connect

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   clarify-ticket ──→ "needs deeper analysis?"            │
│                           │                              │
│                           ▼                              │
│                   ticket-analysis                        │
│                     │  │  │  │                           │
│                     ▼  ▼  ▼  ▼                           │
│          ┌──────────┬──┬──┬──────────┐                   │
│          │ analyze- │  │  │ analyze- │   (4 parallel     │
│          │ design   │  │  │ feasib.  │    agents)        │
│          └──────────┘  │  └──────────┘                   │
│          ┌──────────┐  ┌──────────────┐                  │
│          │ analyze- │  │ analyze-     │                   │
│          │ docs     │  │ data-model   │                   │
│          └──────────┘  └──────────────┘                   │
│                           │                              │
│                           ▼                              │
│               Consolidated report                        │
│               with cross-references                      │
│                           │                              │
│                     ┌─────┼─────┐                        │
│                     ▼     ▼     ▼                        │
│               notify-   adr   create-                    │
│               team            bug                        │
│                                                          │
│   sprint-review ──→ flags tickets ──→ clarify-ticket     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Configuration reference

<details>
<summary><strong>Issue tracker (required)</strong></summary>

```yaml
issue_tracker: jira               # jira | linear | github-issues

jira:
  cloud_id: "myorg.atlassian.net"
  default_project: "PROJ"
  story_points_field: "customfield_10031"
  default_bug_epic: "PROJ-25"

# OR
linear:
  team_id: "TEAM-ID"
```
</details>

<details>
<summary><strong>Design tool (optional)</strong></summary>

```yaml
design_tool: figma                # figma | penpot | none
```

Required for `analyze-design` and the design analysis in `ticket-analysis`.
</details>

<details>
<summary><strong>Documentation sources (optional)</strong></summary>

```yaml
docs_sources:
  - type: confluence
    cloud_id: "myorg.atlassian.net"
  - type: notion
```

Required for `analyze-docs` and the documentation analysis in `ticket-analysis`.
</details>

<details>
<summary><strong>Board tool (optional)</strong></summary>

```yaml
board_tool: miro                  # miro | excalidraw | none
board_config:
  default_parent_page: ""         # Notion page ID for publishing stories
  available_roles: []             # e.g. [advisor, technician, coordinator]
```

Required for `board-to-stories`.
</details>

<details>
<summary><strong>Communication (optional)</strong></summary>

```yaml
communication:
  tool: slack                     # slack | teams | discord | none
  channels: {}
```

Required for `notify-team`.
</details>

<details>
<summary><strong>Sprint review settings (optional)</strong></summary>

```yaml
sprint_review:
  oversized_threshold: 5          # story points above this = oversized
  systemic_threshold: 0.5         # ratio of tickets with same issue = systemic
  bug_alert_threshold: 0.4        # ratio of bugs in sprint = alert
  vague_terms_es: ["debería", "quizás", "TBD", ...]
  vague_terms_en: ["should", "maybe", "TBD", ...]
```
</details>

## Adapters

refinery uses the same config + adapter pattern as ops-suite:

| Category | Adapters |
|----------|----------|
| Issue tracker | jira, linear, github-issues |
| Design tool | figma, penpot |
| Documentation | confluence, notion |
| Board tool | miro |
| Communication | slack |

To add a new adapter (e.g., Asana, Zeplin):

1. Create `skills/<skill>/adapters/<tool>.md`
2. Define the API calls using the tool's MCP server
3. Update `config.example.yaml` with the new option

## Project structure

```
refinery/
├── config.example.yaml        ← copy to config.yaml and fill in
├── commands/                   ← slash command triggers (/refinery:xxx)
├── skills/                     ← skill logic (one folder per skill)
│   └── <skill>/
│       ├── SKILL.md            ← step-by-step workflow
│       ├── adapters/           ← tool-specific API calls
│       └── references/         ← templates, output formats
└── docs/                       ← workflows and guides
```

## License

MIT
