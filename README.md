# workbench-dev

Developer toolkit for Claude Code: infrastructure operations, roadmap refinement, and skill authoring.

**Technology-agnostic** — all skills use a config + adapter pattern. Define your stack once in `config.yaml`, and skills automatically load the right commands for your tools.

## Plugins

### ops-suite — Infrastructure Operations

| Skill | Description |
|-------|-------------|
| `service-status` | Check service/container health, events, resource usage |
| `service-logs` | Search and analyze logs, find errors, debug runtime issues |
| `port-forward` | Establish local connections to cluster services |
| `deploy` | Deploy merged changes to environments |
| `db-migrate` | Run database migrations on remote environments |
| `db-query` | Execute read-only SQL queries against databases |
| `queue-status` | Check message queue status, DLQ counts, consumer health |
| `queue-triage` | Diagnose why messages fail in dead letter queues |
| `queue-reprocess` | Move failed messages from DLQ back to main queue |

**Supported stacks:** Kubernetes, Docker Compose, ECS · RabbitMQ, Azure Service Bus, SQS · PostgreSQL, MySQL · GitHub Actions, GitLab CI · MikroORM, TypeORM

### refinery — Roadmap Refinement

| Skill | Description |
|-------|-------------|
| `clarify-ticket` | Analyze tickets for ambiguities and missing information |
| `create-bug` | Create structured bug reports with root cause analysis |
| `sprint-review` | Evaluate sprint readiness with 8 automated checks |
| `ticket-analysis` | Comprehensive analysis across ticket, design, docs, and code |
| `analyze-design` | Extract data fields, UI states, and actions from designs |
| `analyze-docs` | Search documentation across platforms without interpretation |
| `analyze-data-model` | Trace entity fields through the codebase |
| `analyze-feasibility` | Evaluate technical approaches against the codebase |
| `adr` | Create, update, or compact Architecture Decision Records |
| `board-to-stories` | Extract user stories from visual boards |
| `notify-team` | Draft and send team messages |

**Supported tools:** Jira, Linear, GitHub Issues · Figma, Penpot · Confluence, Notion · Miro · Slack, Teams

### creating-skills — Skill Authoring Guide

Meta-skill that guides you through authoring Claude Code skills following Anthropic best practices.

## Installation

```bash
# Add the marketplace
/plugin marketplace add github:aldorea/workbench-dev

# Install the plugins you need
/plugin install ops-suite
/plugin install refinery
/plugin install creating-skills
```

## Configuration

Each plugin with adapters has a `config.example.yaml`. Copy it and fill in your values:

```bash
# For ops-suite
cd ~/.claude/plugins/cache/.../ops-suite
cp config.example.yaml config.yaml

# For refinery
cd ~/.claude/plugins/cache/.../refinery
cp config.example.yaml config.yaml
```

### How config + adapters work

1. **`config.yaml`** — You define your stack (e.g., `orchestrator: kubernetes`, `message_broker: rabbitmq`)
2. **SKILL.md** — Each skill reads your config and loads the right adapter
3. **`adapters/*.md`** — Technology-specific commands with `{config.X.Y}` placeholders

To add support for a new technology, create an adapter file in the relevant skill's `adapters/` directory.

### Example: ops-suite config

```yaml
orchestrator: kubernetes
message_broker: rabbitmq
database: postgresql

environments:
  dev:
    context: dev-cluster
    namespaces:
      apps: my-apps
      infra: shared-infra
    services:
      broker:
        name: my-rabbitmq
        management_port: 15672
        vhost: "/"
      database:
        name: pgbouncer-dev
        port: 6432
        default_db: myapp_dev
```

## Contributing

### Adding an adapter

1. Find the skill you want to extend (e.g., `plugins/ops-suite/skills/queue-status/`)
2. Create a new file in `adapters/` (e.g., `kafka.md`)
3. Add all the commands needed for that technology, using `{config.X.Y}` placeholders
4. Submit a PR

### Creating a new skill

Use the `creating-skills` plugin for guidance: `/creating-skills:creating-skills`

## License

MIT
