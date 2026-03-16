# Workbench Dev — Plugin Creation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a Claude Code plugin monorepo with 3 plugins (ops-suite, refinery, creating-skills) that are fully parametrized and technology-agnostic.

**Architecture:** Monorepo with marketplace.json at root. Each plugin is self-contained under `plugins/`. Skills use a config+adapter pattern: SKILL.md defines the generic flow, adapters/ contain technology-specific commands, and config.yaml holds the user's infrastructure details.

**Tech Stack:** Claude Code plugins (SKILL.md format), YAML configs, Markdown adapters, Python/Node scripts.

---

### Task 1: Scaffold repo and initialize git

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `marketplace.json`
- Create: `plugins/ops-suite/.claude-plugin/plugin.json`
- Create: `plugins/ops-suite/config.example.yaml`
- Create: `plugins/refinery/.claude-plugin/plugin.json`
- Create: `plugins/refinery/config.example.yaml`
- Create: `plugins/creating-skills/.claude-plugin/plugin.json`

**Step 1: Initialize git repo**

Run: `cd /Users/alfonso/Documents/workbench-dev && git init`

**Step 2: Create marketplace.json**

```json
{
  "owner": "aldorea",
  "description": "Developer toolkit: infrastructure operations, roadmap refinement, and skill authoring for Claude Code",
  "plugins": [
    {
      "name": "ops-suite",
      "source": "file:./plugins/ops-suite",
      "description": "Technology-agnostic infrastructure operations: service status, logs, deployments, database queries, and message queue management",
      "version": "0.1.0"
    },
    {
      "name": "refinery",
      "source": "file:./plugins/refinery",
      "description": "AI-powered roadmap refinement: ticket analysis, sprint review, design analysis, documentation search, and team communication",
      "version": "0.1.0"
    },
    {
      "name": "creating-skills",
      "source": "file:./plugins/creating-skills",
      "description": "Guide for authoring Claude Code skills following Anthropic best practices",
      "version": "0.1.0"
    }
  ]
}
```

**Step 3: Create plugin.json for each plugin**

ops-suite:
```json
{
  "name": "ops-suite",
  "description": "Technology-agnostic infrastructure operations: service status, logs, deployments, database queries, and message queue management. Supports Kubernetes, Docker Compose, ECS, RabbitMQ, Azure Service Bus, PostgreSQL, MySQL, and more via adapters.",
  "version": "0.1.0",
  "author": {
    "name": "aldorea",
    "url": "https://github.com/aldorea"
  },
  "repository": "https://github.com/aldorea/workbench-dev",
  "license": "MIT"
}
```

refinery:
```json
{
  "name": "refinery",
  "description": "AI-powered roadmap refinement: analyze tickets, review sprints, extract user stories, search documentation, analyze designs, create ADRs, and communicate with your team. Supports Jira, Linear, GitHub Issues, Figma, Confluence, Notion, Miro, Slack, and more via adapters.",
  "version": "0.1.0",
  "author": {
    "name": "aldorea",
    "url": "https://github.com/aldorea"
  },
  "repository": "https://github.com/aldorea/workbench-dev",
  "license": "MIT"
}
```

creating-skills:
```json
{
  "name": "creating-skills",
  "description": "Guide for authoring Claude Code skills following Anthropic best practices. Covers skill structure, SKILL.md templates, testing, and distribution.",
  "version": "0.1.0",
  "author": {
    "name": "aldorea",
    "url": "https://github.com/aldorea"
  },
  "repository": "https://github.com/aldorea/workbench-dev",
  "license": "MIT"
}
```

**Step 4: Create config.example.yaml for ops-suite**

```yaml
# ops-suite configuration
# Copy this file to config.yaml and fill in your values.

# Which technologies you use (determines which adapters are loaded)
orchestrator: kubernetes          # kubernetes | docker-compose | ecs | none
message_broker: rabbitmq          # rabbitmq | azure-service-bus | sqs | kafka | none
database: postgresql              # postgresql | mysql | mongodb | none

# Environment definitions
environments:
  dev:
    context: ""                   # e.g. dev-cluster (kubectl context)
    namespaces:
      apps: ""                    # e.g. my-apps
      infra: ""                   # e.g. shared-infra
    services:
      broker:
        name: ""                  # e.g. my-rabbitmq
        management_port: 15672
        amqp_port: 5672
        vhost: "/"
        pod_pattern: ""           # e.g. rabbitmq-* (for kubectl exec)
      database:
        name: ""                  # e.g. pgbouncer-dev
        port: 6432
        default_db: ""            # e.g. myapp_dev
  prod:
    context: ""
    namespaces:
      apps: ""
      infra: ""
    services:
      broker:
        name: ""
        management_port: 15672
        amqp_port: 5672
        vhost: "/"
        pod_pattern: ""
      database:
        name: ""
        port: 6432
        default_db: ""

# Deployment configuration
deploy:
  ci_provider: github-actions     # github-actions | gitlab-ci | none
  image_tag_source: run-id        # run-id | commit-sha | tag
  migration_tool: mikro-orm       # mikro-orm | typeorm | knex | flyway | none
  migration_command: ""           # e.g. npm run migrations:up
  local_ports:
    dev: 16432                    # local port for dev DB port-forward
    prod: 16433                   # local port for prod DB port-forward

# Service registry (for port-forward)
# Add your services here. Each entry maps a friendly name to its k8s details.
service_registry:
  # example:
  # my-api:
  #   namespace: apps
  #   service: svc/my-api
  #   port: 8000
  #   verify: "curl -s -o /dev/null -w '%{http_code}' http://localhost:{port}/health"
```

**Step 5: Create config.example.yaml for refinery**

```yaml
# refinery configuration
# Copy this file to config.yaml and fill in your values.

# Issue tracker
issue_tracker: jira               # jira | linear | github-issues
jira:
  cloud_id: ""                    # e.g. myorg.atlassian.net
  default_project: ""             # e.g. DEVPT
  story_points_field: ""          # e.g. customfield_10031
  default_bug_epic: ""            # e.g. DEVPT-25
  bug_description_template: default  # default | custom

linear:
  team_id: ""
  # Add Linear-specific fields as needed

# Design tool
design_tool: figma                # figma | penpot | none

# Documentation sources
docs_sources:
  - type: confluence              # confluence | notion | none
    cloud_id: ""                  # e.g. myorg.atlassian.net
  - type: notion

# Board tool (for extracting user stories)
board_tool: miro                  # miro | excalidraw | none
board_config:
  default_parent_page: ""         # e.g. Notion page ID for publishing US
  available_roles: []             # e.g. [asesor, técnico, coordinador]

# Sprint review
sprint_review:
  oversized_threshold: 5          # story points above this are flagged
  systemic_threshold: 0.5         # percentage (0-1) above which findings become systemic
  bug_alert_threshold: 0.4        # percentage of bugs that triggers a warning
  vague_terms_es:
    - "debería"
    - "quizás"
    - "posiblemente"
    - "varios"
    - "algunos"
    - "etc."
    - "por definir"
    - "TBD"
    - "en general"
    - "eventualmente"
    - "se podría"
    - "a futuro"
  vague_terms_en:
    - "should"
    - "maybe"
    - "possibly"
    - "various"
    - "some"
    - "etc."
    - "TBD"
    - "in general"
    - "eventually"
    - "could be"
    - "as needed"
    - "appropriate"

# Communication
communication:
  tool: slack                     # slack | teams | discord | none
  channels: {}
  # Example:
  # channels:
  #   general: { id: "C0A2HRXEF63", name: "#my-team" }
  #   alerts-dlq: { id: "C09PU66T8S1", name: "#alerts-dlq" }
  #   alerts-critical: { id: "C09PVJJ471C", name: "#alerts-critical" }
  #   alerts-infra: { id: "C09PG6FQCNB", name: "#alerts-infra" }

# Ticket analysis
ticket_analysis:
  ui_keywords:
    - "pantalla"
    - "diseño"
    - "formulario"
    - "botón"
    - "vista"
    - "UI"
    - "interfaz"
    - "modal"
    - "dropdown"
    - "tabla"
    - "listado"
    - "dashboard"
    - "layout"
    - "screen"
    - "form"
    - "button"
    - "view"
    - "interface"
```

**Step 6: Create LICENSE (MIT)**

**Step 7: Create README.md**

Minimal README with: what this is, how to install, how to configure, list of plugins and skills.

**Step 8: Commit**

```bash
git add .
git commit -m "chore: scaffold workbench-dev monorepo with marketplace and configs"
```

---

### Task 2: Create ops-suite skills (9 skills)

For each skill, the process is:
1. Write generic SKILL.md (no hardcoded values, reads from config)
2. Extract technology-specific commands into adapters/
3. Copy any existing references/ and scripts/

**Skills to create (in dependency order):**

1. `service-status` (from infra-pods)
2. `service-logs` (from infra-logs)
3. `port-forward` (from infra-portforward)
4. `deploy` (from infra-deploy)
5. `db-migrate` (from infra-migrations)
6. `db-query` (from db-query)
7. `queue-status` (from rabbitmq-list-queues)
8. `queue-triage` (from rabbitmq-triage-dlq)
9. `queue-reprocess` (from rabbitmq-reprocess-dlq)

**Key transformation pattern for each SKILL.md:**

```markdown
## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it doesn't exist, tell the user to copy `config.example.yaml`
to `config.yaml` and fill in their values. Stop here.

Extract:
- `orchestrator` → load adapter from `adapters/{orchestrator}.md`
- `environments.{env}` → connection details for the target environment

Ask the user which environment to target if not specified in $ARGUMENTS.
```

Then replace all hardcoded namespaces, service names, contexts with `{config.X.Y}` placeholders in the adapter files.

**Files per skill:**
- `plugins/ops-suite/skills/{name}/SKILL.md`
- `plugins/ops-suite/skills/{name}/adapters/{technology}.md`
- `plugins/ops-suite/skills/{name}/references/*.md` (if applicable)
- `plugins/ops-suite/skills/{name}/scripts/*` (if applicable)

**Step 1: Create all 9 SKILL.md files**

Each one follows the generic flow pattern. Replace all technology-specific commands with "Load the adapter for {config.orchestrator/message_broker/database}".

**Step 2: Create adapter files**

Extract the current hardcoded commands from the original skills into adapter .md files:
- `kubernetes.md` for service-status, service-logs, port-forward, deploy, db-migrate
- `rabbitmq.md` for queue-status, queue-triage, queue-reprocess
- `postgresql.md` for db-query
- `github-actions.md` for deploy
- `mikro-orm.md` for db-migrate

**Step 3: Copy references and scripts**

- `queue-triage/references/known-patterns.md` (make generic)
- `queue-triage/scripts/analyze_messages.py` (already generic)
- `db-query/scripts/query.js` (already generic for PostgreSQL)
- `db-query/references/query-examples.md` (parametrize)
- `deploy/references/commands.md` (parametrize)
- `db-migrate/references/commands.md` (parametrize)
- `port-forward/references/services.md` → remove, replaced by config.yaml service_registry

**Step 4: Commit**

```bash
git add plugins/ops-suite/
git commit -m "feat(ops-suite): add 9 parametrized infrastructure skills with adapters"
```

---

### Task 3: Create refinery skills (11 skills)

**Skills to create:**

1. `clarify-ticket` (from jira-clarify-ticket)
2. `create-bug` (from jira-create-bug)
3. `sprint-review` (from sprint-review)
4. `ticket-analysis` (from ticket-analysis)
5. `analyze-design` (from analyze-design)
6. `analyze-docs` (from analyze-docs)
7. `analyze-data-model` (from analyze-data-model)
8. `analyze-feasibility` (from analyze-technical-feasibility)
9. `adr` (from adr)
10. `board-to-stories` (from miro-to-us)
11. `notify-team` (from notify-team)

**Key transformation:**
- Replace `afianza-ac.atlassian.net` with `{config.jira.cloud_id}`
- Replace `DEVPT` with `{config.jira.default_project}`
- Replace `customfield_10031` with `{config.jira.story_points_field}`
- Replace `DEVPT-25` with `{config.jira.default_bug_epic}`
- Replace Slack channel IDs with `{config.communication.channels.*}`
- Replace Notion workspace ID with `{config.board_config.default_parent_page}`
- Replace hardcoded roles with `{config.board_config.available_roles}`
- Replace vague terms lists with `{config.sprint_review.vague_terms_*}`
- Move Jira-specific MCP tool calls into `adapters/jira.md`
- Move Figma-specific calls into `adapters/figma.md`
- Move Confluence calls into `adapters/confluence.md`
- Move Notion calls into `adapters/notion.md`
- Move Miro calls into `adapters/miro.md`
- Move Slack calls into `adapters/slack.md`

**Files per skill:**
- `plugins/refinery/skills/{name}/SKILL.md`
- `plugins/refinery/skills/{name}/adapters/{tool}.md`
- `plugins/refinery/skills/{name}/references/*.md` (migrated)

**Step 1: Create all 11 SKILL.md files (generic)**

**Step 2: Create adapter files**

- `jira.md` — for clarify-ticket, create-bug, sprint-review, ticket-analysis
- `linear.md` — stub adapters for future
- `figma.md` — for analyze-design
- `confluence.md`, `notion.md` — for analyze-docs
- `miro.md` — for board-to-stories
- `slack.md` — for notify-team, sprint-review

**Step 3: Copy and parametrize references**

- `clarify-ticket/references/actions-and-format.md`
- `sprint-review/references/output-format.md`
- `sprint-review/references/output-format-slack.md`
- `ticket-analysis/references/output-format.md`
- `adr/references/template-en.md`, `template-es.md`
- `board-to-stories/references/us-template.md`
- `notify-team/references/templates-es.md`, `templates-en.md`

**Step 4: Commit**

```bash
git add plugins/refinery/
git commit -m "feat(refinery): add 11 parametrized roadmap refinement skills with adapters"
```

---

### Task 4: Create creating-skills plugin

**Step 1: Create SKILL.md**

Migrate from original — this one doesn't need adapters or config. It's a meta-skill.

**Files:**
- `plugins/creating-skills/skills/creating-skills/SKILL.md`
- `plugins/creating-skills/skills/creating-skills/references/anthropic-guide.md`
- `plugins/creating-skills/skills/creating-skills/references/patterns.md`

**Step 2: Commit**

```bash
git add plugins/creating-skills/
git commit -m "feat(creating-skills): add skill authoring guide"
```

---

### Task 5: Create life-os repo

Separate repo at `/Users/alfonso/Documents/life-os/`.

**Step 1: Initialize git and scaffold**

- `README.md`
- `LICENSE` (MIT)
- `.claude-plugin/plugin.json`
- `config.example.yaml`

**Step 2: Create all 10 skills**

1. `today` — parametrize vault_path and structure paths from config
2. `week` — same parametrization
3. `status` — same
4. `prep` — same
5. `shop` — same
6. `train` — same
7. `sync-training` — same
8. `sync-calendar` — same
9. `sync-slack` — same
10. `process-inbox` — same

**Key transformation:**
- Replace `/Users/alfonso/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault` with `{config.vault_path}`
- Replace `03 Daily` with `{config.structure.daily_notes}`
- Replace `01 Backlog.md` with `{config.structure.backlog}`
- Replace all hardcoded folder paths with config references
- Replace hardcoded tags with configurable tag lists
- Replace hardcoded backlog sections with config

**Step 3: Commit**

```bash
git add .
git commit -m "feat: scaffold life-os plugin with 10 parametrized skills"
```

---

### Task 6: Documentation and final polish

**Step 1: Write comprehensive README for workbench-dev**

Include: overview, installation, configuration guide, list of all skills with descriptions, how to create adapters, contributing guide.

**Step 2: Write README for life-os**

Same structure but for personal productivity skills.

**Step 3: Final commits**

```bash
# workbench-dev
git commit -m "docs: add comprehensive README and contributing guide"

# life-os
git commit -m "docs: add README with configuration guide"
```
