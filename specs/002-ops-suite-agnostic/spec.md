# Feature Specification: ops-suite Full Technology Agnosticism

**Feature Branch**: `002-ops-suite-agnostic`

**Created**: 2026-05-14

**Status**: Draft

**Input**: "quiero que mi plugin ops-suite sea agnostico de tecnologias (orquestador, base de datos, etc)"

## Clarifications

### Session 2026-05-14

- Q: How should db-query delegate the port-forward step — load port-forward's adapter directly, invoke port-forward as a chained skill, or have its own orchestrator adapters? → A: Load `skills/port-forward/adapters/{orchestrator}.md` directly (Option A). No skill chaining, no duplicate adapters under db-query.
- Q: For Azure Service Bus queue-reprocess, should the adapter check for the Python SDK at runtime or let Python fail naturally? → A: Adapter actively checks at runtime (`python3 -c "import azure.servicebus"`); if missing, prints install command and stops cleanly (Option A).

---

## Context

ops-suite already uses an adapter pattern: each skill reads a technology key from
`config.yaml` (e.g. `orchestrator: kubernetes`, `database: postgresql`) and loads
the matching `adapters/{technology}.md` file at runtime.

However, the adapter coverage is incomplete and two structural inconsistencies exist:

**Missing adapters (gaps vs. config.yaml declared options):**

| Skill | Has adapters | Missing |
|-------|-------------|---------|
| `db-query` | postgresql | mysql, mongodb |
| `db-migrate` | mikro-orm, typeorm | knex, flyway |
| `queue-triage` | rabbitmq | azure-service-bus, sqs, kafka |
| `queue-reprocess` | rabbitmq | azure-service-bus, sqs, kafka |
| `queue-status` | *(uses references/, not adapters/)* | rabbitmq, azure-service-bus, sqs, kafka adapter files |

**Hardcoded technology in skill bodies:**

- `db-query/SKILL.md` contains a hardcoded `kubectl port-forward` command in its
  connection step instead of delegating to the `port-forward` skill's adapter.

This feature completes the adapter coverage and eliminates the hardcoded references
so that ops-suite works identically regardless of which technologies are declared
in `config.yaml`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use db-query with MySQL or MongoDB (Priority: P1)

A user whose `config.yaml` sets `database: mysql` (or `mongodb`) runs
`/ops-suite:db-query` and gets a working query session — same flow, same output
format as PostgreSQL, just different underlying commands.

**Why this priority**: `db-query` is the most-used skill after `service-logs`.
MySQL and MongoDB are the two declared-but-unsupported databases. Any user not
on PostgreSQL hits an immediate "not yet supported" wall.

**Independent Test**: Set `database: mysql` in config; run `/ops-suite:db-query`;
verify a connection is established and a simple read query returns results without
error. Repeat for `mongodb`.

**Acceptance Scenarios**:

1. **Given** `config.yaml` has `database: mysql`, **When** `/ops-suite:db-query`
   runs, **Then** it connects via MySQL client commands (not psql), executes the
   query, and returns results in the same tabular report format as PostgreSQL.

2. **Given** `config.yaml` has `database: mongodb`, **When** `/ops-suite:db-query`
   runs, **Then** it connects via MongoDB shell, accepts a query in MongoDB syntax,
   and returns results formatted as a readable report.

3. **Given** `config.yaml` has `database: unsupported-db`, **When** the skill runs,
   **Then** it tells the user the database is not supported and lists supported options.

---

### User Story 2 - Use queue skills with SQS, Kafka, or Azure Service Bus (Priority: P2)

A user whose `config.yaml` sets `message_broker: sqs` (or `kafka` / `azure-service-bus`)
runs `/ops-suite:queue-status`, `/ops-suite:queue-triage`, or `/ops-suite:queue-reprocess`
and gets the same diagnostic + remediation flow as RabbitMQ.

**Why this priority**: Queue skills have the widest technology gap — only RabbitMQ is
supported despite the config declaring three other brokers. Teams on AWS or Azure
are completely blocked.

**Independent Test**: Set `message_broker: sqs`; run `/ops-suite:queue-status`;
verify it lists queues with message counts without error. Repeat for kafka and
azure-service-bus. Repeat triage and reprocess for each broker.

**Acceptance Scenarios**:

1. **Given** `message_broker: sqs`, **When** `/ops-suite:queue-status` runs,
   **Then** it lists SQS queues with approximate message counts and DLQ status.

2. **Given** `message_broker: kafka`, **When** `/ops-suite:queue-triage` runs,
   **Then** it identifies consumer groups with lag and recommends remediation steps.

3. **Given** `message_broker: azure-service-bus`, **When** `/ops-suite:queue-reprocess`
   runs, **Then** it moves messages from dead-letter queues back to the main queue.

4. **Given** any broker, all three queue skills (`queue-status`, `queue-triage`,
   `queue-reprocess`) use the adapter pattern consistently — no hardcoded
   broker-specific logic in the skill body.

---

### User Story 3 - Use db-migrate with Knex or Flyway (Priority: P3)

A user with `migration_tool: knex` or `migration_tool: flyway` in their config
runs `/ops-suite:db-migrate` and gets a working migration flow — list pending,
confirm, apply — same as mikro-orm and typeorm.

**Why this priority**: Migration tools are less frequently changed than databases or
brokers, but blocking users on knex/flyway means they cannot use the most safety-critical
skill (running migrations in prod) via ops-suite.

**Independent Test**: Set `migration_tool: knex`; run `/ops-suite:db-migrate`; verify
it lists pending migrations and successfully applies them using knex CLI commands.

**Acceptance Scenarios**:

1. **Given** `migration_tool: knex`, **When** `/ops-suite:db-migrate` runs,
   **Then** it uses `knex migrate:list` and `knex migrate:latest` (or equivalent)
   with the correct connection parameters.

2. **Given** `migration_tool: flyway`, **When** `/ops-suite:db-migrate` runs,
   **Then** it uses `flyway info` and `flyway migrate` with correct config.

---

### User Story 4 - db-query port-forward uses adapter, not hardcoded kubectl (Priority: P4)

A user with `orchestrator: docker-compose` or `orchestrator: ecs` runs
`/ops-suite:db-query` and the port-forward step uses the correct adapter commands —
not the hardcoded `kubectl port-forward` that currently exists in the skill body.

**Why this priority**: This is a correctness bug: a user not on Kubernetes gets a
silently wrong port-forward command even if their `orchestrator` is set correctly.

**Independent Test**: Set `orchestrator: docker-compose`; run `/ops-suite:db-query`;
verify it uses docker-compose port mapping syntax, not kubectl, for the connection step.

**Acceptance Scenarios**:

1. **Given** `orchestrator: docker-compose`, **When** `db-query` establishes a
   connection, **Then** it delegates to the `port-forward` skill's docker-compose
   adapter — no `kubectl` command is executed.

2. **Given** `orchestrator: kubernetes`, **When** `db-query` establishes a connection,
   **Then** it delegates to the `port-forward` skill's kubernetes adapter (behaviour
   unchanged for existing users).

---

### User Story 5 - Auto-detect Technologies on First Run (Priority: P2)

A user who has never configured ops-suite runs any skill for the first time. Instead
of getting an error asking them to run `/ops-suite:configure`, the system scans the
environment, detects what is available (CLIs installed, running containers, cluster
contexts, compose files), and proposes a pre-filled config for the user to confirm
before saving.

**Why this priority**: The biggest friction for new users is the manual config setup.
Auto-detection removes that barrier entirely and makes the onboarding experience
match what the user actually has installed — no guessing required.

**Independent Test**: Remove `config.yaml`; run `/ops-suite:service-logs`; verify
the system detects the environment (e.g. finds kubectl and a running context), proposes
a config, and proceeds after one confirmation — without requiring the user to open
any file manually.

**Acceptance Scenarios**:

1. **Given** no `config.yaml` exists, **When** any ops-suite skill is invoked,
   **Then** the system runs environment detection, reports what it found
   (e.g. "Found: kubectl with context dev-cluster, psql available, no message broker
   detected"), proposes a config, and asks for confirmation before saving.

2. **Given** environment detection finds multiple options for a technology
   (e.g. both kubectl and docker-compose are installed), **When** proposing the config,
   **Then** the system lists the options ranked by confidence and asks the user to
   pick one — it never silently choose one over the other.

3. **Given** detection cannot determine a technology (e.g. no database CLI found),
   **When** proposing the config, **Then** that field is left blank with a prompt
   asking the user to fill it in, rather than blocking the whole process.

4. **Given** the user confirms the proposed config, **When** it is saved,
   **Then** the original skill continues executing immediately without requiring
   the user to re-run it.

---

### User Story 6 - Guided Config Wizard with Validation (Priority: P3)

When a user explicitly runs `/ops-suite:configure`, the wizard asks smart questions,
pre-fills answers from auto-detected environment state where possible, validates each
connection before moving to the next section, and saves only a fully working config.

**Why this priority**: The existing configure wizard asks questions but does not
validate connections or pre-fill from detection — users fill in values incorrectly
and only discover the mistake when running a skill later.

**Independent Test**: Run `/ops-suite:configure`; verify it detects the current
kubectl context and offers it as the default; verify it tests the database connection
before saving; verify it warns if a declared message broker is unreachable.

**Acceptance Scenarios**:

1. **Given** the user runs `/ops-suite:configure`, **When** the orchestrator question
   is asked, **Then** detected options are presented as defaults (e.g. "Found kubectl
   context dev-cluster — use this? [Y/n]") rather than an empty prompt.

2. **Given** the user provides database connection details, **When** moving to the
   next section, **Then** the wizard tests the connection and reports success or
   failure before proceeding — it MUST NOT save an untested connection.

3. **Given** the user declares a message broker, **When** the wizard validates it,
   **Then** it attempts to reach the broker management endpoint and warns if
   unreachable, but allows the user to save anyway with an explicit acknowledgement.

4. **Given** the wizard completes, **When** config is saved, **Then** a summary is
   printed showing all detected+confirmed technologies and the config file path.

---

### Edge Cases

- A user sets a technology that is in `config.yaml`'s declared options but has no
  adapter yet (e.g. a future addition): skill MUST surface "not yet supported" with
  a list of supported values — never crash silently.
- An adapter file exists but is empty or malformed: skill MUST detect this and report
  a clear error, not produce nonsensical output.
- A user switches `database:` in config mid-session (while `/tmp/ops-suite-session/config.json`
  is cached): session cache must be invalidated so the new adapter is loaded.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `db-query` MUST have adapter files for `mysql` and `mongodb` that
  implement the same interface contract as `adapters/postgresql.md`: connection setup,
  read-only query execution, and result formatting.

- **FR-002**: `db-query/SKILL.md` MUST NOT contain any hardcoded orchestrator-specific
  commands for the connection/port-forward step. It MUST delegate by loading
  `skills/port-forward/adapters/{orchestrator}.md` directly and following its steps —
  no skill chaining, no duplicate adapter files under db-query.

- **FR-003**: `queue-status`, `queue-triage`, and `queue-reprocess` MUST each have
  adapter files for `sqs`, `kafka`, and `azure-service-bus` implementing the same
  interface contract as their respective `rabbitmq.md` adapters. The
  `queue-reprocess/adapters/azure-service-bus.md` adapter MUST check for the
  `azure-servicebus` Python package at runtime (`python3 -c "import azure.servicebus"`);
  if absent, it MUST print the install command (`pip install azure-servicebus
  azure-identity`) and stop with a clear error before attempting any operation.

- **FR-004**: `queue-status` MUST migrate from `references/` to `adapters/` to be
  consistent with the rest of the plugin. Existing `references/*.md` content MUST be
  preserved as the basis for the new adapters.

- **FR-005**: `db-migrate` MUST have adapter files for `knex` and `flyway` implementing
  the same interface contract as `mikro-orm.md` and `typeorm.md`: list pending, apply,
  and verify migrations.

- **FR-006**: Every skill MUST handle the "adapter not found" case gracefully: display
  the unsupported technology name, list the supported values, and stop without error.

- **FR-007**: The session cache (`/tmp/ops-suite-session/config.json`) MUST be
  invalidated when the technology keys (`orchestrator`, `database`, `message_broker`)
  change between invocations.

- **FR-008**: When any skill is invoked without a valid `config.yaml`, the system
  MUST run environment auto-detection before prompting the user to configure manually.
  Detection MUST check: available CLIs (`kubectl`, `docker`, `docker-compose`,
  `psql`, `mysql`, `mongosh`, `aws`, `az`), active kubectl contexts, running
  docker-compose projects, and `docker-compose.yml` files in the current directory.

- **FR-009**: Auto-detection MUST produce a confidence-ranked list of detected
  options per technology dimension (orchestrator, database, message broker) and
  propose the highest-confidence option as the default.

- **FR-010**: When multiple options are detected for the same technology dimension,
  the system MUST present all options and ask the user to choose — never silently
  pick one.

- **FR-011**: After the user confirms the auto-detected config, the original skill
  MUST continue executing immediately without requiring a separate re-invocation.

- **FR-012**: `/ops-suite:configure` MUST pre-fill each question with the
  auto-detected value (if available) and allow the user to accept with a single
  confirmation or override with a custom value.

- **FR-013**: `/ops-suite:configure` MUST validate each connection before saving:
  database connection MUST be tested; broker reachability MUST be tested with a
  warning-but-not-block if unreachable; orchestrator context MUST be verified
  (e.g. `kubectl cluster-info` or `docker info`).

### Key Entities

- **Adapter**: a Markdown file at `skills/{skill}/adapters/{technology}.md` that
  provides technology-specific commands for a defined interface (connect, query/list,
  format output). All adapters for the same skill MUST implement the same interface.

- **Interface contract**: the set of named steps (e.g. "Step A — Connect", "Step B —
  Execute", "Step C — Format") that every adapter for a given skill MUST implement,
  enabling the skill body to call them without knowing the underlying technology.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every technology option declared in `config.example.yaml` has a
  corresponding adapter in every skill that uses that technology dimension.
  Zero "not yet supported" errors for declared options.

- **SC-002**: Zero hardcoded technology-specific commands (kubectl, psql, rabbitmqctl,
  etc.) appear in any skill body (`SKILL.md`). All such commands live exclusively
  in adapter files.

- **SC-003**: A user can switch `orchestrator`, `database`, or `message_broker` in
  their `config.yaml` and all affected skills work correctly on the next invocation
  without any skill body changes.

- **SC-004**: All new adapters follow the same interface contract as existing adapters
  for the same skill — validated by a consistent step naming convention.

- **SC-005**: A new user with no `config.yaml` can go from zero to a working
  ops-suite session in under 2 minutes, using only auto-detection and confirmations —
  without opening any file manually.

- **SC-006**: `/ops-suite:configure` validates and confirms at least the database
  and orchestrator connections before saving, eliminating "silent misconfiguration"
  errors that only surface later during skill execution.

## Assumptions

- The adapter interface contracts (step naming, input/output shape) for each skill are
  already implicitly defined by the existing `rabbitmq.md` / `postgresql.md` / etc.
  adapters and will be made explicit during planning.
- `queue-status` currently uses `references/` instead of `adapters/` — this is treated
  as a structural inconsistency to fix, not intended design.
- No changes to `config.yaml` schema or the configure wizard are required for this
  feature (all technologies are already declared as valid options).
- Existing users on supported technologies (kubernetes + postgresql + rabbitmq)
  MUST experience zero behaviour change.
