# Changelog

All notable changes to ops-suite are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [0.4.1] — 2026-05-04

### Fixed

- **Config location** — the SessionStart hook used to look for `config.yaml` inside the plugin directory, which resolves to the cached plugin path (`~/.claude/plugins/cache/...`) when installed via `/plugin install`. That path never contains the user's config, so the cache stayed empty and skills with `metadata.model:` set (which run as subagents) silently failed to find the config and returned empty output.
- The hook now resolves `config.yaml` from, in order:
  1. `$OPS_SUITE_CONFIG` (explicit override)
  2. `${XDG_CONFIG_HOME:-$HOME/.config}/ops-suite/config.yaml` (preferred, stable across reinstalls)
  3. `${PLUGIN_ROOT}/config.yaml` (legacy, kept for backwards compatibility)
- All skill `Step 0 — Load configuration` blocks updated to reflect the new lookup order.
- `configure` skill now writes to `${XDG_CONFIG_HOME:-$HOME/.config}/ops-suite/config.yaml` instead of the plugin directory.

### Changed

- README quick-start now instructs users to place their config at `~/.config/ops-suite/config.yaml`.
- New troubleshooting entry: "Skills hang or return nothing after install".

### Migration

If you had a working `config.yaml` inside the plugin directory, move it:

```bash
mkdir -p ~/.config/ops-suite
mv /path/to/plugins/ops-suite/config.yaml ~/.config/ops-suite/config.yaml
```

Or just re-run `/ops-suite:configure`.

---

## [0.4.0] — 2026-04-30

### Added

- **`deploy-status` skill** — read-only deployment visibility across environments. Shows current deployed commit, author, timestamp, PR, and replicas per environment, plus drift detection between envs (in sync / behind / ahead / diverged).
- **Orchestrator references** for deploy-status:
  - `skills/deploy-status/references/kubernetes.md` — extracts image tag, replicas, and conditions from Deployments.
- **CI references** for deploy-status:
  - `skills/deploy-status/references/github-actions.md` — maps image tag (run-id / commit-sha / tag) to commit metadata, PR, and ahead/behind comparisons.

### Fixed

- **`queue-status` auto-triage loop** — previously only triaged the first DLQ with messages; now triages every DLQ with messages > 0. Bounded throughput: parallel auto-triage for 1–3 DLQs, interactive selection (top 3 / all / skip) when 4 or more are flagged.

### Removed

- **`queue-status/adapters/` folder** — broker-specific commands moved to `queue-status/references/` to align with the official Anthropic skill structure (progressive disclosure via `references/`). `SKILL.md` updated to read `references/{message_broker}.md`.

### Notes

- `deploy-status` is intentionally read-only in this release. Chaining to `deploy` or a future `rollback` skill is deferred to a later version.

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
