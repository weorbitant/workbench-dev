# Changelog

All notable changes to ops-suite are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [0.3.0] — 2026-04-24

### Added

- **`configure` skill** — interactive setup wizard that walks through every infrastructure component (orchestrator, environments, broker, database, CI/CD, migrations, primary service, service registry) and writes `config.yaml`.
- **`configure` slash command** (`/ops-suite:configure`) for direct invocation.
- **Orchestrator adapters** for the configure skill:
  - `skills/configure/adapters/kubernetes.md` — kubectl context/namespace/service detection
  - `skills/configure/adapters/docker-compose.md` — compose file path and service detection
  - `skills/configure/adapters/ecs.md` — AWS CLI prerequisites, cluster/region questions, SSM tunnel for local DB access

### Fixed

- `query.js` (db-query) and `analyze_messages.py` (queue-triage) were missing the executable bit — fixed with `chmod +x`.

### Changed

- **Skill descriptions rewritten** to comply with Anthropic CSO guidelines — removed workflow summaries from `db-migrate`, `db-query`, `deploy`, `queue-reprocess`, `queue-triage`. Descriptions now state capability + trigger conditions + SKIP guidance only.
- `configure/SKILL.md` is now fully orchestrator-agnostic; technology-specific detection commands live in the adapter files.

---

## [0.2.0] — 2026-04-23

### Added

- **`workflow-deploy` skill** — guided interactive deployment wizard (verify merge → find artifact → confirm → deploy → verify).
- **Skill chaining** via session state at `/tmp/ops-suite-session/` — skills share environment context without re-asking the user.
- **Safety gates** — production deployments require explicit confirmation; dev verification is enforced before prod.
- **Slash commands** for all skills (CLI autocomplete).
- **SessionStart hook** — loads config into session cache on startup.

### Fixed

- `workflow-deploy`: resolved `ci_rollback_command` reference and improved service extraction.
- `queue-triage`: improved handling of main queues (missing consumer path) and git history inspection for removed handlers.
- `db-migrate`: added production lockout and pending migration detection.

---

## [0.1.0] — 2026-04-22

### Added

Initial release with 9 parametrized infrastructure skills:

- `service-status` — health checks and restart counts
- `service-logs` — log tailing and search
- `queue-status` — broker queue overview and consumer counts
- `queue-triage` — DLQ diagnosis and root cause reports
- `queue-reprocess` — move DLQ messages back to main queue
- `db-query` — read-only SQL against remote databases
- `db-migrate` — apply pending migrations
- `port-forward` — local port-forwarding to cluster services
- `deploy` — deploy a merged PR or commit

Adapters for RabbitMQ and PostgreSQL/pgbouncer.
Kubernetes and ECS orchestrator support.
