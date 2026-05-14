# Implementation Plan: ops-suite Full Technology Agnosticism

**Branch**: `002-ops-suite-agnostic` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-ops-suite-agnostic/spec.md`

## Summary

Complete the ops-suite adapter coverage so every technology declared in `config.example.yaml`
has a working adapter in every skill that uses that technology dimension. Fix the hardcoded
`kubectl port-forward` in `db-query/SKILL.md`. Migrate `queue-status` from `references/` to
`adapters/`. Add three-pass environment auto-detection triggered when no `config.yaml` is
present, and upgrade the `configure` wizard to pre-fill answers from detection and validate
connections before saving.

Each skill gets an `INTERFACE.md` that formally contracts the step labels every adapter must
implement. Adapter files adopt YAML frontmatter declaring `implements` and `requires` fields.

## Technical Context

**Language/Version**: Markdown + YAML (skill and adapter files); Bash (probe commands);
Node.js v18+ optional (existing `query.js` helper for PostgreSQL)

**Primary Dependencies**: External CLI tools already installed by users — `kubectl`, `docker`,
`docker-compose`, `aws`, `az`, `psql`, `mysql`, `mongosh`, `kafka-consumer-groups.sh`,
`flyway`, `knex`; no new npm/pip dependencies added by the plugin

**Storage**: `${XDG_CONFIG_HOME:-$HOME/.config}/ops-suite/config.yaml` (primary config);
`/tmp/ops-suite-session/config.json` (session cache, invalidated on technology key change)

**Testing**: Manual acceptance scenarios from spec.md; existing test datasets in
`plugins/ops-suite/tests/datasets/`

**Target Platform**: macOS and Linux developer machines (any where Claude Code runs)

**Project Type**: Claude Code plugin (Markdown skill files + YAML frontmatter + Bash adapter
commands)

**Performance Goals**: Auto-detection probe completes in ≤5 s (3 s reachability timeout per
probe); new-user onboarding from zero config to working session in ≤2 min (SC-005)

**Constraints**: All adapter commands must be read-only probes; no credentials in output
(Principle V); adapter pattern only — zero new standalone scripts outside existing
`scripts/` directories; backward-compatible for kubernetes + postgresql + rabbitmq users

**Scale/Scope**: ~22 new adapter Markdown files, 5 new INTERFACE.md files, 2 SKILL.md edits
(`db-query` Step 3, `configure` wizard), 1 `auto-detect.md` probe guide, 1 `queue-status`
directory restructure

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Plugin-First | All new capabilities deliverable as `/commands` | ✅ All changes are adapter files or SKILL.md edits within the existing plugin — no ad-hoc scripts |
| II. Context-Aware Execution | No hardcoded connection details or stack assumptions | ✅ Core of this feature — auto-detection, adapter routing, INTERFACE.md contract |
| III. Report-Oriented Output | New adapters match existing report format | ✅ All adapters must produce the same structured report format as the rabbitmq/postgresql reference implementations |
| IV. Read Before Act | Auto-detect is non-destructive; configure confirms before saving | ✅ All probes are read-only; configure validation is read-only; db-migrate confirmation flow unchanged |
| V. Credential Safety | Probes use env vars / CLI flags; `# UNVALIDATED` for failed connections | ✅ No credentials in output; failed connections get explicit `# UNVALIDATED` marker before saving |

No violations. No Complexity Tracking required.

## Project Structure

### Documentation (this feature)

```text
specs/002-ops-suite-agnostic/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output — adapter interface contracts per skill
│   ├── db-query.md
│   ├── db-migrate.md
│   ├── queue-status.md
│   ├── queue-triage.md
│   └── queue-reprocess.md
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
plugins/ops-suite/
├── skills/
│   ├── db-query/
│   │   ├── SKILL.md                         # EDIT: replace hardcoded kubectl in Step 3
│   │   ├── INTERFACE.md                     # NEW: step contract (connect, execute, format)
│   │   └── adapters/
│   │       ├── postgresql.md                # EXISTING (no change)
│   │       ├── mysql.md                     # NEW
│   │       └── mongodb.md                   # NEW
│   ├── db-migrate/
│   │   ├── SKILL.md                         # EXISTING (no change needed)
│   │   ├── INTERFACE.md                     # NEW: step contract (list, apply, verify)
│   │   └── adapters/
│   │       ├── mikro-orm.md                 # EXISTING (no change)
│   │       ├── typeorm.md                   # EXISTING (no change)
│   │       ├── knex.md                      # NEW
│   │       └── flyway.md                    # NEW
│   ├── queue-status/
│   │   ├── SKILL.md                         # EDIT: update to load from adapters/ not references/
│   │   ├── INTERFACE.md                     # NEW: step contract (connect, list, format)
│   │   ├── adapters/                        # NEW directory
│   │   │   ├── rabbitmq.md                  # NEW: content from references/rabbitmq.md
│   │   │   ├── sqs.md                       # NEW
│   │   │   ├── kafka.md                     # NEW
│   │   │   └── azure-service-bus.md         # NEW: content from references/azure-service-bus.md
│   │   └── references/                      # EXISTING: kept for backward compat; SKILL.md now loads adapters/
│   ├── queue-triage/
│   │   ├── SKILL.md                         # EXISTING (no change needed)
│   │   ├── INTERFACE.md                     # NEW: step contract (connect, list-dlqs, peek, analyze)
│   │   └── adapters/
│   │       ├── rabbitmq.md                  # EXISTING (no change)
│   │       ├── sqs.md                       # NEW
│   │       ├── kafka.md                     # NEW
│   │       └── azure-service-bus.md         # NEW
│   ├── queue-reprocess/
│   │   ├── SKILL.md                         # EXISTING (no change needed)
│   │   ├── INTERFACE.md                     # NEW: step contract (connect, list-dlqs, reprocess)
│   │   └── adapters/
│   │       ├── rabbitmq.md                  # EXISTING (no change)
│   │       ├── sqs.md                       # NEW
│   │       ├── kafka.md                     # NEW
│   │       └── azure-service-bus.md         # NEW
│   └── configure/
│       ├── SKILL.md                         # EDIT: add auto-detect flow + connection validation
│       └── auto-detect.md                   # NEW: three-pass probe instructions
├── config.example.yaml                      # EXISTING (no change)
└── runtime/
    └── session-state.md                     # EXISTING: document cache-invalidation rule (FR-007)
```

**Structure Decision**: Single plugin directory extending the existing `plugins/ops-suite`
layout. All new files follow the established `skills/{skill}/adapters/{technology}.md`
pattern. No new top-level directories.
