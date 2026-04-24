---
name: configure
description: Walks through full ops-suite setup: asks about all infrastructure components and writes config.yaml. Use when setting up ops-suite for the first time or when config.yaml is missing.
argument-hint: ""
allowed-tools:
  - Bash
  - AskUserQuestion
  - Write
model: sonnet
---

## Overview

Full interactive wizard. Asks the user about **every** infrastructure component one section at a time. Auto-detection is used only to suggest defaults — every question is always asked explicitly, never skipped.

Resolve the plugin directory (where `config.yaml` will be written) as the directory two levels above this SKILL.md file. Store it as `{plugin_dir}`.

---

## Section 1 — Orchestrator

Run silently:
```bash
kubectl config get-contexts 2>/dev/null
```

Ask:
> "What container orchestrator do you use?"
- `kubernetes` — kubectl + cluster contexts *(suggest if contexts were detected)*
- `docker-compose` — local or remote compose files
- `ecs` — Amazon Elastic Container Service
- `none` — no container orchestrator

Store as `{orchestrator}`.

---

## Section 2 — Environments

### 2a — Which environments

Ask:
> "Which environments do you want to configure?" (multi-select)
- `dev`
- `staging`
- `prod`
- `other` — user types the name(s) in notes

Store the list as `{envs}`.

### 2b — Load orchestrator adapter

Read `adapters/{orchestrator}.md` for all orchestrator-specific detection commands and questions. If the adapter does not exist, tell the user the orchestrator is not yet supported and skip environment-specific detection (ask manually).

Follow the adapter instructions for each environment to collect:
- `{env.context}` or equivalent connection identifier
- `{env.ns_apps}` / service scope (where app services run)
- `{env.ns_infra}` / infra scope (where broker and DB run)
- `{env.local_port}` (local port for DB port-forwarding)

---

## Section 3 — Message Broker

Ask:
> "Which message broker do you use?"
- `rabbitmq`
- `azure-service-bus`
- `sqs`
- `kafka`
- `none`

Store as `{broker}`.

### If broker = rabbitmq

For **each** environment, run silently:
```bash
kubectl get svc -n {env.ns_infra} --context={env.context} -o name 2>/dev/null | grep -i rabbit | head -1
```

Ask per environment:
1. > "**{env_name}** — RabbitMQ service name?" (suggest detected or `rabbitmq`)
2. > "**{env_name}** — Pod name pattern (e.g. `rabbitmq-*`)?"
3. > "**{env_name}** — Management port?" (default `15672`)
4. > "**{env_name}** — AMQP port?" (default `5672`)
5. > "**{env_name}** — vhost?" (default `/`)

### If broker = sqs / azure-service-bus / kafka

Ask per environment for the connection string or region/endpoint relevant to that broker.

---

## Section 4 — Database

Ask:
> "Which database do you use?"
- `postgresql`
- `mysql`
- `mongodb`
- `none`

Store as `{database}`.

### If database = postgresql or mysql

For **each** environment, run silently:
```bash
kubectl get svc -n {env.ns_infra} --context={env.context} -o name 2>/dev/null | grep -iE 'pgbouncer|postgres|mysql' | head -1
```

Ask per environment:
1. > "**{env_name}** — DB proxy/service name?" (suggest detected)
2. > "**{env_name}** — Port?" (default: 6432 pgbouncer / 5432 postgres / 3306 mysql)
3. > "**{env_name}** — Default database name?"

### If database = mongodb

Ask per environment for service name and port (default `27017`).

---

## Section 5 — CI/CD Pipeline

Ask:
> "Which CI/CD provider triggers your deployments?"
- `github-actions`
- `gitlab-ci`
- `none`

Store as `{ci_provider}`.

### If ci_provider ≠ none

Ask:
1. > "How is the image tag determined after a CI run?"
   - `run-id` *(most common)*, `commit-sha`, `tag`
   - Store as `{image_tag_source}`

2. > "Repository slug? (e.g. `my-org/my-repo`)"
   - Store as `{repo_slug}`

---

## Section 6 — Migrations

Ask:
> "Which database migration tool do you use?"
- `mikro-orm`, `typeorm`, `knex`, `flyway`, `none`

Store as `{migration_tool}`.

### If migration_tool ≠ none

Ask:
> "Migration command? (e.g. `npm run migrations:up`)"
Store as `{migration_command}`.

---

## Section 7 — Primary service

Run silently:
```bash
kubectl get deployments -n {env[0].ns_apps} --context={env[0].context} \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | head -4
```

Ask:
> "Primary application service name? (used for health checks and log tailing after deploys)"
- List up to 4 detected services + "I'll type it manually"

Store as `{primary_service}`.

---

## Section 8 — Service registry (optional)

Ask:
> "Register additional services for port-forwarding? (e.g. internal APIs, admin panels)"
- `yes` / `no`

If yes, repeat until done:
1. Friendly name (e.g. `my-api`)
2. Service identifier (e.g. `svc/my-api` for k8s, service name for compose/ECS)
3. Namespace / cluster (if applicable)
4. Port
5. Health check URL (optional, e.g. `http://localhost:{port}/health`)
6. Add another?

---

## Section 9 — Write config.yaml

Assemble and write to `{plugin_dir}/config.yaml`:

```yaml
# ops-suite configuration — generated by /ops-suite:configure on {YYYY-MM-DD}

orchestrator: {orchestrator}
message_broker: {broker}
database: {database}
service: {primary_service}

environments:
  {env_name}:
    context: "{env.context}"
    namespaces:
      apps: "{env.ns_apps}"
      infra: "{env.ns_infra}"
    services:
      broker:
        name: "{broker_service}"
        namespace: "{env.ns_infra}"
        management_port: {mgmt_port}
        amqp_port: {amqp_port}
        vhost: "{vhost}"
        pod_pattern: "{pod_pattern}"
      database:
        name: "{db_service}"
        namespace: "{env.ns_infra}"
        port: {db_port}
        default_db: "{default_db}"

deploy:
  ci_provider: {ci_provider}
  repo: "{repo_slug}"
  image_tag_source: {image_tag_source}
  migration_tool: {migration_tool}
  migration_command: "{migration_command}"
  local_ports:
    {env_name}: {env.local_port}

service_registry:
  {name}:
    namespace: {ns}
    service: {svc}
    port: {port}
    verify: "{health_check}"
```

Omit blocks for `none` values.

---

## Section 10 — Cache session

```bash
mkdir -p /tmp/ops-suite-session
```

Write `/tmp/ops-suite-session/config.json` with equivalent JSON so all skills can use it immediately.

---

## Section 11 — Final summary

```
✓ ops-suite configured successfully
────────────────────────────────────────────────────
  Orchestrator:    {orchestrator}
  Environments:    {env_name_1}, {env_name_2}, ...
  Broker:          {broker}
  Database:        {database}
  CI provider:     {ci_provider}
  Migrations:      {migration_tool}
  Primary service: {primary_service}

  Config written → {plugin_dir}/config.yaml
  Session cache  → /tmp/ops-suite-session/config.json

Skills now available:
  /ops-suite:service-status     check service health & restarts
  /ops-suite:service-logs       tail and search logs
  /ops-suite:queue-status       inspect queues            [if broker ≠ none]
  /ops-suite:queue-triage       diagnose DLQs             [if broker ≠ none]
  /ops-suite:db-query           run read-only SQL         [if database ≠ none]
  /ops-suite:db-migrate         apply migrations          [if migration_tool ≠ none]
  /ops-suite:port-forward       connect to services       [if orchestrator ≠ none]
  /ops-suite:workflow-deploy    guided interactive deploy [if ci_provider ≠ none]
────────────────────────────────────────────────────
```
