# workbench-dev

A developer toolkit for Claude Code that eliminates context switching in two areas where it hurts most: **infrastructure operations** and **roadmap refinement**.

## The problem

### During incidents

You get an alert. You open a terminal for `kubectl get pods`, another for `kubectl logs`, another for the RabbitMQ dashboard, another for `psql`... Five terminals, fifteen minutes, and you still don't know what's wrong.

### During planning

A ticket lands in sprint. You open Jira, then Figma, then Confluence, then the codebase... Four tools, twenty minutes, and you still can't tell if it's ready to implement.

## The solution

Define your stack once. Talk to Claude. Get answers.

```
You:    "check if my-api is running in dev"
Claude: 2/2 pods healthy, 0 restarts, 3m CPU, 86Mi memory

You:    "any errors in the logs?"
Claude: 12 occurrences of "column updated_at does not exist"

You:    "run migrations"
Claude: 4 pending migrations. Apply them? [confirm] → Done. 0 errors.

You:    "is PROJ-123 ready to implement?"
Claude: 3 blockers found — missing acceptance criteria, design doesn't match
        data model, no error states defined in Figma
```

## Plugins

### ops-suite — Infrastructure Operations

Manage services, logs, databases, queues, and deployments without leaving your terminal.

| Skill | What it does | Auto-invocable? |
|-------|-------------|-----------------|
| `service-status` | Pod/container health, restarts, CPU, memory | Yes |
| `service-logs` | Error search, classification, pattern detection | Yes |
| `port-forward` | Local tunnels to cluster services | Yes |
| `db-query` | Natural language → SQL, read-only by default | Yes |
| `queue-status` | Queue listing, DLQ counts, consumer health | Yes |
| `queue-triage` | DLQ failure diagnosis, root cause analysis | Yes |
| `deploy` | Deploy merged PRs, verify health post-deploy | **No** — destructive |
| `db-migrate` | Run pending migrations with confirmation | **No** — destructive |
| `queue-reprocess` | Move DLQ messages back after fix | **No** — destructive |

**Supported stacks:** Kubernetes, Docker Compose, ECS · RabbitMQ, Azure Service Bus, SQS, Kafka · PostgreSQL, MySQL · GitHub Actions, GitLab CI · MikroORM, TypeORM

[Full documentation →](plugins/ops-suite/README.md)

### refinery — Roadmap Refinement

Analyze tickets, designs, documentation, and code to answer: *"Is this ready to implement?"*

| Skill | What it does |
|-------|-------------|
| `clarify-ticket` | Find ambiguities and missing info in tickets |
| `ticket-analysis` | Comprehensive cross-source analysis (ticket + design + docs + code) |
| `sprint-review` | Sprint readiness evaluation with 8 automated checks |
| `analyze-design` | Extract data fields, UI states, and actions from designs |
| `analyze-docs` | Search documentation across Confluence/Notion |
| `analyze-data-model` | Trace entity fields through the codebase |
| `analyze-feasibility` | Evaluate technical approaches against the codebase |
| `create-bug` | Structured bug reports with root cause analysis |
| `adr` | Architecture Decision Records |
| `board-to-stories` | Extract user stories from Miro/Excalidraw boards |
| `notify-team` | Draft and send team messages via Slack/Teams |

**Supported tools:** Jira, Linear, GitHub Issues · Figma, Penpot · Confluence, Notion · Miro, Excalidraw · Slack, Teams, Discord

[Full documentation →](plugins/refinery/README.md)

### creating-skills — Skill Authoring Guide

Meta-skill that teaches you how to create your own Claude Code skills following Anthropic best practices. Progressive disclosure, proper triggering, adapter patterns — all covered.

```
/creating-skills:creating-skills
```

## How it works

All plugins share one design principle: **config + adapters**.

```
┌─────────────┐     ┌──────────────┐     ┌────────────────────┐
│ config.yaml │────▶│   SKILL.md   │────▶│ adapters/<tech>.md  │
│             │     │              │     │                    │
│ orchestrator│     │ reads config │     │ kubernetes.md      │
│ = kubernetes│     │ loads right  │     │ docker-compose.md  │
│             │     │ adapter      │     │ ecs.md             │
└─────────────┘     └──────────────┘     └────────────────────┘
```

1. **You define your stack once** in `config.yaml` (Kubernetes? RabbitMQ? PostgreSQL?)
2. **Each skill reads your config** and loads the right adapter
3. **Adapters contain the real commands** (`kubectl`, `rabbitmqctl`, `psql`) with `{config.X.Y}` placeholders

To add support for a new technology, create a markdown file. No code changes needed.

## Installation

```bash
# From the Claude Code marketplace
/plugin marketplace add github:weorbitant/workbench-dev

# Install what you need
/plugin install ops-suite
/plugin install refinery
/plugin install creating-skills
```

## Configuration

Each plugin has a `config.example.yaml`. Copy and fill in your values:

```bash
# For ops-suite
cd ~/.claude/plugins/cache/.../ops-suite
cp config.example.yaml config.yaml

# For refinery
cd ~/.claude/plugins/cache/.../refinery
cp config.example.yaml config.yaml
```

### Minimal ops-suite config

```yaml
orchestrator: kubernetes
message_broker: rabbitmq
database: postgresql

environments:
  dev:
    context: "dev-cluster"
    namespaces:
      apps: "my-namespace"
      infra: "shared-infra"
    services:
      broker:
        name: "rabbitmq"
        management_port: 15672
        vhost: "/"
      database:
        name: "pgbouncer"
        port: 6432
        default_db: "myapp_dev"
```

### Minimal refinery config

```yaml
issue_tracker: jira
jira:
  cloud_id: "myorg.atlassian.net"
  default_project: "PROJ"

design_tool: figma
docs_sources:
  - type: confluence
    cloud_id: "myorg.atlassian.net"
```

## When to use what

| Situation | Plugin | Start with |
|-----------|--------|-----------|
| Production alert / 500 errors | ops-suite | `service-status` → `service-logs` |
| DLQ growing | ops-suite | `queue-status` → `queue-triage` |
| Need to deploy a PR | ops-suite | `deploy` → `service-status` |
| Ticket seems vague | refinery | `clarify-ticket` |
| Sprint planning | refinery | `sprint-review` |
| New ticket to implement | refinery | `ticket-analysis` |
| Design doesn't match specs | refinery | `analyze-design` |
| Need to document a decision | refinery | `adr` |
| Want to create your own skill | creating-skills | `creating-skills` |

## Contributing

### Adding an adapter

1. Find the skill: `plugins/<plugin>/skills/<skill>/adapters/`
2. Create `<technology>.md` using an existing adapter as template
3. Use `{config.X.Y}` placeholders for all environment-specific values
4. Submit a PR

### Creating a new skill

Run `/creating-skills:creating-skills` — it guides you through the entire process.

## License

MIT
