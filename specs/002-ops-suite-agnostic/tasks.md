# Tasks: ops-suite Full Technology Agnosticism

**Input**: Design documents from `/specs/002-ops-suite-agnostic/`

**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Tests**: Not requested — manual acceptance scenarios are defined in spec.md and validated in the Polish phase.

**Organization**: Tasks grouped by user story to enable independent implementation and validation of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no unmet dependencies)
- **[Story]**: Which user story this task belongs to (US1–US6)
- Exact file paths included in every task description

---

## Phase 1: Setup

**Purpose**: Audit existing plugin layout to confirm which files are present vs. missing before writing new ones.

- [ ] T001 Audit existing adapter files in plugins/ops-suite/skills/ against the gap table in plan.md — confirm which adapter files already exist and which are missing; note any unexpected files

---

## Phase 2: Foundational — Interface Contracts

**Purpose**: Define the step contracts every adapter must implement. All Phase 3+ adapter tasks reference step IDs from these files.

**⚠️ CRITICAL**: Complete this phase before writing any adapter files.

- [ ] T002 Create plugins/ops-suite/skills/db-query/INTERFACE.md with mandatory steps step-a-connect, step-b-execute, step-c-format per contracts/db-query.md — include step IDs, input/output contract, and supported technologies table
- [ ] T003 [P] Create plugins/ops-suite/skills/db-migrate/INTERFACE.md with mandatory steps step-a-list, step-b-apply, step-c-verify per contracts/db-migrate.md — include step IDs, input/output contract, and supported technologies table
- [ ] T004 [P] Create plugins/ops-suite/skills/queue-status/INTERFACE.md with mandatory steps step-a-connect, step-b-list, step-c-format per contracts/queue-status.md — include step IDs, input/output contract, exact report format, and supported technologies table
- [ ] T005 [P] Create plugins/ops-suite/skills/queue-triage/INTERFACE.md with mandatory steps step-a-connect, step-b-list-dlqs, step-c-peek, step-d-analyze per contracts/queue-triage.md — include step IDs, input/output contract, and supported technologies table
- [ ] T006 [P] Create plugins/ops-suite/skills/queue-reprocess/INTERFACE.md with mandatory steps step-a-connect, step-b-list-dlqs, step-c-reprocess per contracts/queue-reprocess.md — include step IDs, input/output contract, safety requirement note, and supported technologies table

**Checkpoint**: All 5 INTERFACE.md files created — adapter implementation can proceed in parallel across all phases.

---

## Phase 3: User Story 1 — db-query with MySQL or MongoDB (Priority: P1) 🎯 MVP

**Goal**: Users with `database: mysql` or `database: mongodb` in config.yaml get a working query session with the same flow and report format as PostgreSQL.

**Independent Test**: Set `database: mysql` in config.yaml; run `/ops-suite:db-query`; verify connection is established and a read query returns results in the tabular report format. Repeat for `database: mongodb`.

- [ ] T007 [P] [US1] Create plugins/ops-suite/skills/db-query/adapters/mysql.md with YAML frontmatter (adapter-for: db-query, technology: mysql, implements: [step-a-connect, step-b-execute, step-c-format], requires: [local_port, db_user, db_password, database, sql_query]) and three labeled steps using mysql CLI commands from research.md Decision 5; Step A includes mysqladmin ping connectivity test; Step B uses `mysql -h 127.0.0.1 -P {local_port} -u {db_user} -p{db_password} -D {database} --connect-timeout=10 -e "{sql_query}"`; Step C formats tabular output per contracts/db-query.md report format
- [ ] T008 [P] [US1] Create plugins/ops-suite/skills/db-query/adapters/mongodb.md with YAML frontmatter (adapter-for: db-query, technology: mongodb, implements: [step-a-connect, step-b-execute, step-c-format], requires: [local_port, db_user, db_password, database, sql_query]) and three labeled steps using mongosh commands from research.md Decision 5; Step A uses mongosh ping eval for connectivity test; Step B uses `mongosh "mongodb://{db_user}:{db_password}@127.0.0.1:{local_port}/{database}?authSource=admin" --eval "{sql_query}" --quiet --norc`; include MQL query syntax note in Step B; Step C formats document results as key/value list per contracts/db-query.md

**Checkpoint**: US1 complete — users on MySQL or MongoDB can run `/ops-suite:db-query` successfully.

---

## Phase 4: User Story 2 — Queue Skills with SQS, Kafka, Azure Service Bus (Priority: P2)

**Goal**: Users with `message_broker: sqs`, `kafka`, or `azure-service-bus` get full coverage of queue-status, queue-triage, and queue-reprocess — same diagnostic and remediation flow as RabbitMQ.

**Independent Test**: Set `message_broker: sqs`; run `/ops-suite:queue-status`; verify it lists SQS queues with approximate message counts and DLQ status without error. Repeat for kafka and azure-service-bus. Repeat triage and reprocess for each broker.

### queue-status structural migration (do T009 before T010–T012)

- [ ] T009 [US2] Create plugins/ops-suite/skills/queue-status/adapters/ directory by writing plugins/ops-suite/skills/queue-status/adapters/rabbitmq.md — content based on existing references/rabbitmq.md; add YAML frontmatter (adapter-for: queue-status, technology: rabbitmq, implements: [step-a-connect, step-b-list, step-c-format]); restructure headings to match INTERFACE.md step labels
- [ ] T010 [P] [US2] Create plugins/ops-suite/skills/queue-status/adapters/azure-service-bus.md — content based on existing references/azure-service-bus.md; add YAML frontmatter (adapter-for: queue-status, technology: azure-service-bus, implements: [step-a-connect, step-b-list, step-c-format]); restructure headings to match step labels; Step B uses `az servicebus queue list` and `az servicebus queue show --query countDetails`; DLQ identification via $DeadLetterQueue suffix
- [ ] T011 [P] [US2] Create plugins/ops-suite/skills/queue-status/adapters/sqs.md with YAML frontmatter (adapter-for: queue-status, technology: sqs, implements: [step-a-connect, step-b-list, step-c-format]); Step A uses `aws sts get-caller-identity` for reachability; Step B uses `aws sqs list-queues` + `aws sqs get-queue-attributes --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible` + `aws sqs get-queue-attributes --attribute-names RedrivePolicy` to identify DLQs; Step C formats per contracts/queue-status.md report format
- [ ] T012 [P] [US2] Create plugins/ops-suite/skills/queue-status/adapters/kafka.md with YAML frontmatter (adapter-for: queue-status, technology: kafka, implements: [step-a-connect, step-b-list, step-c-format]); Step A uses `kafka-topics.sh --bootstrap-server {broker}:9092 --list` for reachability; Step B uses `kafka-consumer-groups.sh --bootstrap-server {broker}:9092 --list` + `--describe` for lag; DLQ topic identification via `.DLT`, `-dlt`, `.dead`, `.dlq` suffixes using `kafka-topics.sh --list | grep -E`; Step C formats per contracts/queue-status.md
- [ ] T013 [US2] Edit plugins/ops-suite/skills/queue-status/SKILL.md to load `adapters/{message_broker}.md` instead of `references/rabbitmq.md`; leave references/ directory in place (backward compat — do NOT delete); add FR-006 graceful fallback block: if adapter file not found, display unsupported technology name and list supported values (rabbitmq, sqs, kafka, azure-service-bus) and stop

### queue-triage new adapters (all parallel)

- [ ] T014 [P] [US2] Create plugins/ops-suite/skills/queue-triage/adapters/sqs.md with YAML frontmatter (adapter-for: queue-triage, technology: sqs, implements: [step-a-connect, step-b-list-dlqs, step-c-peek, step-d-analyze]); Step A uses `aws sts get-caller-identity`; Step B uses `aws sqs list-queues` + `aws sqs get-queue-attributes --attribute-names RedrivePolicy` to identify DLQs with non-zero messages; Step C peeks using `aws sqs receive-message --visibility-timeout 0 --max-number-of-messages 5` (non-destructive); Step D extracts error info from message attributes and groups by pattern per contracts/queue-triage.md format
- [ ] T015 [P] [US2] Create plugins/ops-suite/skills/queue-triage/adapters/kafka.md with YAML frontmatter (adapter-for: queue-triage, technology: kafka, implements: [step-a-connect, step-b-list-dlqs, step-c-peek, step-d-analyze]); Step A uses kafka-topics.sh --list; Step B uses `kafka-topics.sh --list | grep -E '\.(DLT|dlq|dead)'` + `kafka-consumer-groups.sh --describe` for lag; Step C peeks via `kafka-console-consumer.sh --bootstrap-server {broker}:9092 --topic {topic} --max-messages 5 --from-beginning`; Step D groups by error header pattern per contracts/queue-triage.md
- [ ] T016 [P] [US2] Create plugins/ops-suite/skills/queue-triage/adapters/azure-service-bus.md with YAML frontmatter (adapter-for: queue-triage, technology: azure-service-bus, implements: [step-a-connect, step-b-list-dlqs, step-c-peek, step-d-analyze]); Step A uses `az account show`; Step B uses `az servicebus queue list` and filters on `countDetails.deadLetterMessageCount > 0`; Step C peeks via `az servicebus message peek` or `az servicebus queue show --query countDetails`; Step D formats per contracts/queue-triage.md

### queue-reprocess new adapters (all parallel)

- [ ] T017 [P] [US2] Create plugins/ops-suite/skills/queue-reprocess/adapters/sqs.md with YAML frontmatter (adapter-for: queue-reprocess, technology: sqs, implements: [step-a-connect, step-b-list-dlqs, step-c-reprocess]); Steps A and B same pattern as queue-triage SQS adapter; Step C uses `aws sqs start-message-move-task --source-arn {dlq-arn}` (2023+ native redrive API) then `aws sqs list-message-move-tasks --source-arn {dlq-arn}` to monitor progress; safety confirmation is collected by SKILL.md before Step C runs
- [ ] T018 [P] [US2] Create plugins/ops-suite/skills/queue-reprocess/adapters/kafka.md with YAML frontmatter (adapter-for: queue-reprocess, technology: kafka, implements: [step-a-connect, step-b-list-dlqs, step-c-reprocess]); Step C reprocess = offset reset via `kafka-consumer-groups.sh --reset-offsets --to-earliest`; MUST run `--dry-run` first and display full output before executing with `--execute`; include prominent note that the consumer MUST be fully stopped before Step C
- [ ] T019 [P] [US2] Create plugins/ops-suite/skills/queue-reprocess/adapters/azure-service-bus.md with YAML frontmatter (adapter-for: queue-reprocess, technology: azure-service-bus, implements: [step-a-connect, step-b-list-dlqs, step-c-reprocess]); Step C must check `python3 -c "import azure.servicebus"` at runtime (FR-003) — if absent, print `pip install azure-servicebus azure-identity` and stop with clear error before any operation; if present, include Python SDK script block to move dead-letter messages back to source queue using azure-identity DefaultAzureCredential

**Checkpoint**: US2 complete — queue-status, queue-triage, and queue-reprocess work with all four declared brokers.

---

## Phase 5: User Story 5 — Auto-detect Technologies on First Run (Priority: P2)

**Goal**: A new user with no `config.yaml` runs any ops-suite skill and gets guided through auto-detection to a working session in under 2 minutes — no manual file editing required.

**Independent Test**: Remove or rename config.yaml; run any ops-suite skill; verify the three-pass probe fires, reports detected technologies with confidence ranking, proposes a config, and continues executing the original skill after one confirmation.

- [ ] T020 Create plugins/ops-suite/skills/configure/auto-detect.md with three-pass probe instructions: Pass 1 binary presence (`command -v {cli}` → score 1) for kubectl, docker, docker-compose, psql, mysql, mongosh, aws, az; Pass 2 active context (kubectl config current-context, ls docker-compose.yml, aws configure get region, docker info → score 3); Pass 3 reachability with 3s timeout (kubectl cluster-info --request-timeout=3s, docker ps, aws sts get-caller-identity, az account show → score 5); disambiguation rule (exactly one candidate ≥ 3 → propose as default, multiple ≥ 3 → list and ask, none → leave blank and ask); proposed config YAML template; confirmation and save flow; false-positive mitigations from research.md Decision 2 (psql + lsof, kubectl + cluster-info, docker + docker info not --version)
- [ ] T021 Edit plugins/ops-suite/skills/configure/SKILL.md to add auto-detect trigger: at startup when config.yaml is absent or any technology key (orchestrator, database, message_broker) is empty, load auto-detect.md and run probe for each dimension; present ranked AutoDetectResult candidates; for winner with score ≥ 3 propose as default; for ambiguous top-score ask user to pick; for blank ask user to fill in; collect confirmations; save config.yaml; continue original skill execution without re-invocation (FR-008 through FR-011)
- [ ] T022 Edit plugins/ops-suite/runtime/session-state.md to document cache-invalidation rule (FR-007): /tmp/ops-suite-session/config.json is invalidated when orchestrator, database, or message_broker values differ from cached values; skills must compare current config keys against cached keys before reusing session file

**Checkpoint**: US5 complete — first-run experience guides users from zero config to working session without manual file editing.

---

## Phase 6: User Story 3 — db-migrate with Knex or Flyway (Priority: P3)

**Goal**: Users with `migration_tool: knex` or `migration_tool: flyway` in config get a working migrate flow — list pending, confirm, apply, verify.

**Independent Test**: Set `migration_tool: knex` in config; run `/ops-suite:db-migrate`; verify it lists pending migrations and applies them using `knex migrate:latest`.

- [ ] T023 [P] [US3] Create plugins/ops-suite/skills/db-migrate/adapters/knex.md with YAML frontmatter (adapter-for: db-migrate, technology: knex, implements: [step-a-list, step-b-apply, step-c-verify], requires: [DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]); Step A uses `knex migrate:list` (connectivity check — exits 0 if connection ok); Step B uses `knex migrate:latest` and shows exact command before running; Step C uses `knex migrate:status` post-apply; include note that knexfile.js must exist in working directory
- [ ] T024 [P] [US3] Create plugins/ops-suite/skills/db-migrate/adapters/flyway.md with YAML frontmatter (adapter-for: db-migrate, technology: flyway, implements: [step-a-list, step-b-apply, step-c-verify], requires: [FLYWAY_URL, FLYWAY_USER, FLYWAY_PASSWORD]); Step A uses `flyway info` (read-only connectivity check); Step B uses `flyway migrate` and shows exact command before running; Step C uses `flyway validate` post-apply; include JDBC URL format note: `jdbc:{database}://{host}:{port}/{dbname}`

**Checkpoint**: US3 complete — users on knex or flyway can run `/ops-suite:db-migrate` successfully.

---

## Phase 7: User Story 6 — Configure Wizard with Validation (Priority: P3)

**Goal**: `/ops-suite:configure` pre-fills questions from auto-detect results and validates each connection before saving — eliminating silent misconfiguration.

**Dependency**: T020 and T021 must be complete (auto-detect.md must exist before SKILL.md references it).

**Independent Test**: Run `/ops-suite:configure`; verify it shows detected kubectl context as default; verify it runs pg_isready before saving database config; verify it warns if a declared broker is unreachable.

- [ ] T025 [US6] Edit plugins/ops-suite/skills/configure/SKILL.md to add wizard enhancements: pre-fill each wizard question with the auto-detected value from the probe (FR-012) — present as "Found {value} — use this? [Y/n]" rather than empty prompt; after user provides database credentials run technology-specific connectivity probe before proceeding to next section (pg_isready for postgresql, mysqladmin ping for mysql, mongosh ping eval for mongodb — FR-013); for broker validate reachability (aws sts get-caller-identity / az account show / rabbitmq management API) and warn if unreachable but allow user to save anyway with explicit acknowledgement; on validation failure ask "retry or save anyway?"; if "save anyway" prepend `# UNVALIDATED` comment to that config block; at wizard completion print summary showing all detected+confirmed technologies and config file path (SC-006)

**Checkpoint**: US6 complete — configure wizard validates connections before saving; users discover misconfiguration during setup, not during skill execution.

---

## Phase 8: User Story 4 — db-query Port-Forward Uses Adapter (Priority: P4)

**Goal**: The `db-query` connection step delegates to the `port-forward` skill's adapter instead of the hardcoded `kubectl port-forward` command in the skill body.

**Independent Test**: Set `orchestrator: docker-compose`; run `/ops-suite:db-query`; verify it uses docker-compose port mapping syntax for the connection step, not kubectl.

- [ ] T026 [US4] Edit plugins/ops-suite/skills/db-query/SKILL.md Step 3 to remove the hardcoded `kubectl port-forward` command and replace with instruction to load `skills/port-forward/adapters/{orchestrator}.md` and follow its steps for the port-forward/connection tunnel (FR-002); verify kubernetes behavior is preserved for existing users

**Checkpoint**: US4 complete — any orchestrator declared in config.yaml produces the correct port-forward commands in db-query.

---

## Polish & Cross-Cutting Concerns

**Purpose**: Final validation sweep across all new files before acceptance.

- [ ] T027 [P] Validate frontmatter completeness across all new adapter files: for each adapter confirm the `implements` array lists all step IDs from the corresponding INTERFACE.md, no credentials appear in command output (use `{password}` template variable, not literal values), and the `requires` keys match keys available in config.example.yaml schema
- [ ] T028 [P] Validate FR-006 graceful fallback in each SKILL.md that now routes to adapters: db-query, db-migrate, queue-status, queue-triage, queue-reprocess — each must display the unsupported technology name, list the supported values, and stop without crashing when an unknown technology key is set
- [ ] T029 Run quickstart.md acceptance scenarios for all user stories: (1) mysql adapter with db-query, (2) mongodb adapter with db-query, (3) sqs queue-status, (4) kafka queue-triage, (5) azure-service-bus queue-reprocess SDK check, (6) knex db-migrate, (7) flyway db-migrate, (8) docker-compose orchestrator with db-query, (9) no config.yaml auto-detect flow end-to-end, (10) configure wizard with connection validation

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends on | Notes |
|-------|-----------|-------|
| Phase 1 (Setup) | — | Start immediately |
| Phase 2 (Foundational) | Phase 1 | Blocks all adapter tasks |
| Phase 3 (US1) | T002 | Can start as soon as db-query INTERFACE.md is done |
| Phase 4 (US2) | T004, T005, T006 | Can run in parallel with Phase 3 once queue INTERFACE.md files are done |
| Phase 5 (US5) | Phase 2 | Can start in parallel with Phases 3 and 4 |
| Phase 6 (US3) | T003 | Can start in parallel after db-migrate INTERFACE.md is done |
| Phase 7 (US6) | T020, T021 | auto-detect.md must exist before wizard references it |
| Phase 8 (US4) | Phase 2 | Independent of all other stories |
| Polish | Phases 3–8 | After all story phases complete |

### User Story Dependencies

- **US1 (P1)**: After Phase 2 — no dependencies on other stories
- **US2 (P2)**: After Phase 2 — no dependencies on US1
- **US5 (P2)**: After Phase 2 — no dependencies on US1, US2
- **US3 (P3)**: After Phase 2 — no dependencies on other stories
- **US6 (P3)**: After US5 (configure/SKILL.md auto-detect block must exist first)
- **US4 (P4)**: After Phase 2 — no dependencies on other stories

### Parallel Opportunities Within Phases

- T003–T006: all parallel (four different INTERFACE.md files in different skill directories)
- T007–T008: parallel (mysql.md and mongodb.md, different files)
- T009 must precede T010–T012; then T010, T011, T012 are parallel; T013 after all four
- T014, T015, T016: parallel (queue-triage adapters, different files)
- T017, T018, T019: parallel (queue-reprocess adapters, different files)
- T014–T019: all six can run in parallel with each other (different skill directories)
- T023–T024: parallel (knex.md and flyway.md, different files)
- T027, T028: parallel (different validation concerns)

---

## Parallel Execution Examples

### Phase 2 — INTERFACE.md files

```
# Run concurrently after T002 starts:
Task: T003 Create db-migrate/INTERFACE.md
Task: T004 Create queue-status/INTERFACE.md
Task: T005 Create queue-triage/INTERFACE.md
Task: T006 Create queue-reprocess/INTERFACE.md
```

### Phase 4 — queue-triage + queue-reprocess adapters

```
# Run all six concurrently after Phase 2 complete:
Task: T014 queue-triage/adapters/sqs.md
Task: T015 queue-triage/adapters/kafka.md
Task: T016 queue-triage/adapters/azure-service-bus.md
Task: T017 queue-reprocess/adapters/sqs.md
Task: T018 queue-reprocess/adapters/kafka.md
Task: T019 queue-reprocess/adapters/azure-service-bus.md
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational)
2. Complete Phase 3 (US1) — MySQL + MongoDB adapters for db-query
3. **STOP and VALIDATE**: Test MySQL and MongoDB query sessions
4. Delivers immediate value to all users not on PostgreSQL

### Incremental Delivery

1. Phase 1–2 (Setup + Contracts) → foundation and contracts ready
2. Phase 3 (US1) → MySQL/MongoDB users unblocked → **MVP**
3. Phase 4 (US2) → all broker users unblocked across three queue skills
4. Phase 5 (US5) → first-run experience eliminates manual config setup
5. Phase 6 (US3) → knex/flyway users unblocked for db-migrate
6. Phase 7 (US6) → configure wizard validates before saving
7. Phase 8 (US4) → port-forward correctness bug fixed
8. Polish → all acceptance scenarios pass (SC-001 through SC-006)

### Parallel Team Strategy

After Phase 2 completes:

- Dev A: US1 (Phase 3) — T007, T008 (MySQL + MongoDB adapters)
- Dev B: US2 (Phase 4) — T009–T019 (queue-status migration + 9 broker adapters)
- Dev C: US5 (Phase 5) + US6 (Phase 7) — T020–T022, T025 (auto-detect + wizard)
- Dev D: US3 (Phase 6) + US4 (Phase 8) — T023, T024, T026 (knex, flyway, port-forward fix)

---

## Notes

- **[P]** tasks = different files, no shared-file dependencies — safe to run concurrently
- All adapter commands must be read-only probes (Constitution Principle IV)
- No credentials in adapter output — use `{password}` template variable, never literals
- `queue-status/references/` stays in place after migration — do NOT delete (backward compat)
- Azure Service Bus queue-reprocess requires Python SDK runtime check (FR-003)
- Session cache at `/tmp/ops-suite-session/config.json` invalidated on technology key change (FR-007)
- Before marking any adapter task complete: verify `implements` array lists all step IDs from the skill's INTERFACE.md
- SC-001 target: every option in config.example.yaml has a working adapter in every skill that uses that dimension
