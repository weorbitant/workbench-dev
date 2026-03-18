# ops-suite

Run infrastructure operations from Claude Code — check services, read logs, query databases, manage queues, deploy and migrate — without leaving your terminal.

## What problem does this solve?

When something breaks in production, you usually SSH into clusters, copy-paste kubectl commands, open RabbitMQ dashboards, connect to databases... all manually, across multiple terminals.

ops-suite lets you do all of that by talking to Claude:

```
You:    "check if obligations-api is running in dev"
Claude: runs service-status, shows 2/2 pods healthy, 0 restarts, 3m CPU, 86Mi memory

You:    "any errors in the logs?"
Claude: runs service-logs, finds 12 occurrences of "column updated_at does not exist"

You:    "run migrations"
Claude: runs db-migrate, lists 4 pending migrations, asks for confirmation, applies them

You:    "check logs again"
Claude: runs service-logs, confirms 0 errors after migration

You:    "how are the queues?"
Claude: runs queue-status, finds 3 DLQs with 390K messages

You:    "triage and reprocess them"
Claude: runs queue-triage → queue-reprocess, shovels messages back, verifies 0 errors
```

That's a real session. Six operations, zero context switching.

## Quick start

**1. Add the plugin** to your Claude Code settings (`.claude/settings.json`):

```json
{
  "plugins": [
    "/path/to/workbench-dev/plugins/ops-suite"
  ]
}
```

**2. Create your config:**

```bash
cd /path/to/ops-suite
cp config.example.yaml config.yaml
```

**3. Fill in three things** in `config.yaml`:

```yaml
orchestrator: kubernetes          # what runs your services
message_broker: rabbitmq          # what moves your messages
database: postgresql              # what stores your data
```

And your environments (at minimum, one):

```yaml
environments:
  dev:
    context: "dev"                # kubectl context name
    namespaces:
      apps: "my-namespace"       # where your services run
      infra: "shared-infra"      # where infra services live (rabbitmq, etc.)
```

That's enough to start using `service-status`, `service-logs`, and `queue-status`. The other skills need a few more fields — see [Full configuration](#full-configuration) below.

**4. Restart Claude Code.** You'll see the list of available skills.

## What can you do?

### Check services

```
/ops-suite:service-status my-api dev     → pods, restarts, CPU/memory, deployment state
/ops-suite:service-logs my-api dev       → errors, classification, frequency, patterns
```

These are read-only — Claude can run them automatically when the context suggests it.

### Work with databases

```
/ops-suite:db-query "latest 20 orders" dev   → translates to SQL, shows for confirmation, runs it
/ops-suite:db-migrate dev                     → lists pending migrations, applies them
/ops-suite:port-forward database dev          → opens a local tunnel to the cluster DB
```

You describe what you want in plain language. Claude translates it to SQL and asks before running.

### Manage queues

```
/ops-suite:queue-status dev                              → lists all queues, consumers, DLQ counts
/ops-suite:queue-triage my-api:client:persisted.dead_letter dev   → peeks messages, classifies failures
/ops-suite:queue-reprocess my-api:client:persisted.dead_letter dev → shovels messages back or purges
```

Triage tells you *why* messages failed. Reprocess moves them back after the fix.

### Deploy

```
/ops-suite:deploy 42 dev                 → deploys PR #42, verifies health, checks logs
```

After deploying, it automatically checks service health and logs. If migrations are needed, it tells you what to run next.

## How skills connect

Skills suggest each other based on what they find. Read-only skills chain automatically. Destructive skills (deploy, migrate, reprocess) show you what to run next — you decide when.

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   service-status ──→ service-logs ──→ suggests next step │
│                           │                              │
│                     ┌─────┼─────┐                        │
│                     ▼     ▼     ▼                        │
│               DB errors  Queue  App                      │
│                  │      errors  errors                   │
│                  ▼        ▼                               │
│       "→ Run db-migrate"  queue-status                   │
│                             │                            │
│                             ▼                            │
│                       queue-triage                       │
│                             │                            │
│                             ▼                            │
│                "→ Run queue-reprocess"                   │
│                                                          │
│   deploy ──→ service-status ──→ service-logs             │
│                                      │                   │
│                                      ▼                   │
│                           "→ Run db-migrate"             │
│                                                          │
└──────────────────────────────────────────────────────────┘

  ──→  = automatic (read-only skills)
  "→"  = suggested (you invoke it)
```

## Safety

| Skill | Type | Auto-invocable? | Why |
|-------|------|-----------------|-----|
| service-status | read-only | Yes | Just reading pod state |
| service-logs | read-only | Yes | Just reading log output |
| db-query | read-only | Yes | SELECT queries only (writes require confirmation) |
| queue-status | read-only | Yes | Just listing queues |
| port-forward | read-only | Yes | Just opening a tunnel |
| **deploy** | destructive | **No** | Changes running code |
| **db-migrate** | destructive | **No** | Changes database schema |
| **queue-reprocess** | destructive | **No** | Moves messages between queues |

Destructive skills always require you to type the `/ops-suite:xxx` command explicitly. They also ask for confirmation before acting.

## Full configuration

`config.yaml` has three sections. You only need to fill in what you use.

<details>
<summary><strong>Infrastructure (required)</strong></summary>

```yaml
orchestrator: kubernetes          # kubernetes | docker-compose | ecs
message_broker: rabbitmq          # rabbitmq | azure-service-bus | sqs | kafka | none
database: postgresql              # postgresql | mysql | mongodb | none
```

Set to `none` if you don't use queues or databases.
</details>

<details>
<summary><strong>Environments (required, at least one)</strong></summary>

```yaml
environments:
  dev:
    context: "dev"                        # kubectl context / docker-compose project
    namespaces:
      apps: "my-namespace"                # where your app pods run
      infra: "shared-infra"               # where infra services run
    services:
      broker:
        name: "rabbitmq"                  # service/pod name
        namespace: "shared-infra"         # override if different from infra
        management_port: 15672
        amqp_port: 5672
        vhost: "my_vhost"
        pod_pattern: "rabbitmq-*"         # for kubectl exec
      database:
        name: "pgbouncer"
        namespace: "my-namespace"         # override if different from infra
        port: 6432
        default_db: "my-service-dev"
  prod:
    # same structure, different values
```
</details>

<details>
<summary><strong>Deploy settings (only if using deploy/migrate skills)</strong></summary>

```yaml
deploy:
  ci_provider: github-actions             # github-actions | gitlab-ci
  image_tag_source: run-id                # run-id | commit-sha | tag
  migration_tool: mikro-orm               # mikro-orm | typeorm | knex | none
  migration_command: "npm run migrations:up"
  local_ports:
    dev: 16432                            # local port for dev DB tunnel
    prod: 16433                           # local port for prod DB tunnel
```
</details>

## Adapters

ops-suite is technology-agnostic. Each skill loads an **adapter** based on your config. The adapter contains the actual commands (kubectl, docker, rabbitmqctl, etc.).

To add support for a new technology:

1. Create `skills/<skill>/adapters/<technology>.md` (use an existing adapter as template)
2. Set the corresponding config value (e.g., `orchestrator: ecs`)
3. The skill will load your adapter automatically

Currently supported:

| Category | Adapters |
|----------|----------|
| Orchestrator | kubernetes, docker-compose, ecs |
| Database | postgresql (mysql and mongodb planned) |
| Message broker | rabbitmq (azure-service-bus planned) |
| CI/CD | github-actions, gitlab-ci |
| Migration tool | mikro-orm, typeorm |

## Workflows

See [docs/workflows.md](docs/workflows.md) for step-by-step recipes for common scenarios:

- Incident triage (something is broken)
- Deploy and verify
- DLQ cleanup
- Database investigation
- Pre-deploy check
- Cross-environment comparison
- Post-incident recovery

## Project structure

```
ops-suite/
├── config.example.yaml        ← copy to config.yaml and fill in
├── commands/                   ← slash command triggers (/ops-suite:xxx)
├── skills/                     ← skill logic (one folder per skill)
│   └── <skill>/
│       ├── SKILL.md            ← step-by-step workflow
│       ├── adapters/           ← technology-specific commands
│       ├── references/         ← decision trees, patterns
│       └── scripts/            ← helper scripts
├── runtime/                    ← shared conventions (chaining, safety)
├── hooks/                      ← session-start hook
└── docs/                       ← workflows, plans, references
```

## Troubleshooting

**"config.json not cached" warning on session start**
→ You need `js-yaml` installed: `npm i -g js-yaml`. Without it, skills still work (they read `config.yaml` directly) but lose the caching benefit.

**Port-forward connects but queries fail with "connection refused"**
→ Check the namespace. Some services (like PgBouncer) may run in the apps namespace, not infra. Set `namespace:` in your service config to override.

**Destructive skills don't auto-invoke**
→ By design. `deploy`, `db-migrate`, and `queue-reprocess` require explicit `/ops-suite:xxx` invocation. Read-only skills (status, logs, query) can auto-invoke.

**"relation does not exist" or "column does not exist" errors**
→ Migrations are pending. Run `/ops-suite:db-migrate {env}`.

## Roadmap

See [docs/plans/2026-03-18-ops-suite-v2-skill-chaining.md](docs/plans/2026-03-18-ops-suite-v2-skill-chaining.md) for planned improvements:

- Pipeline skills (`deploy-full`, `incident-triage`) as composite workflows
- Auto-invocation — model detects intent without needing `/` commands
- Session state improvements — credential caching, port-forward pooling
