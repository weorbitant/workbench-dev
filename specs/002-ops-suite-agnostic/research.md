# Research: ops-suite Full Technology Agnosticism

## Decision 1: Adapter Interface Contract

**Decision**: Each skill gets an `INTERFACE.md` file that defines mandatory `## Step X — VerbNoun`
headings every adapter must implement. The skill body references steps by label only.
Adapter files include a YAML frontmatter block declaring which steps they implement.

**Rationale**: The current adapters have no formal contract — headings are free-form.
When a skill body says "use adapter command for recent error logs", it only works because
there is one adapter. A second adapter with different headings would silently produce
wrong behaviour. Labeled steps give the skill body a reliable anchor.

**Alternatives considered**:
- Shared template adapter: too brittle, relies on copy-paste discipline
- Runtime schema validation: overkill for markdown-instruction-based skills

**Adapter frontmatter contract**:

```yaml
---
adapter-for: db-query
technology: mysql
implements: [step-a-connect, step-b-execute, step-c-format]
requires: [local_port, db_user, db_password, database, sql_query]
---
```

If a required step is missing the skill body reports "adapter incomplete" and stops.

---

## Decision 2: Environment Auto-Detection Strategy

**Decision**: Three-pass probe with confidence scoring. Skills dispatch the auto-detect
flow only when `config.yaml` is absent or `technology` fields are empty.

**Rationale**: Binary presence alone produces false positives (psql installed but no
cluster access). Active-context checks (kubectl current-context, docker-compose.yml in
cwd) add medium confidence. Reachability checks (kubectl cluster-info, docker info)
confirm high confidence. The three-pass approach balances speed vs accuracy.

**Probe passes**:

```
Pass 1 — Binary presence (score 1):
  command -v kubectl | docker | docker-compose | psql | mysql | mongosh | aws | az

Pass 2 — Active context (score 3):
  kubectl config current-context 2>/dev/null         → kubernetes
  ls docker-compose.yml compose.yml 2>/dev/null       → docker-compose
  aws configure get region 2>/dev/null                → ecs/sqs
  docker info --format '{{.ServerVersion}}' 2>/dev/null → docker

Pass 3 — Reachability (score 5, timeout 3s):
  kubectl cluster-info --request-timeout=3s           → kubernetes
  docker ps 2>/dev/null                               → docker-compose
  aws sts get-caller-identity 2>/dev/null             → ecs/sqs
  az account show 2>/dev/null                         → azure
```

**Disambiguation rule**: if exactly one candidate reaches score ≥ 3 for a dimension,
propose it as default. If multiple candidates ≥ 3, always ask. If none reach 1, leave
blank and ask.

**False-positive mitigations**:
- `psql` present: also check `lsof -i :5432` or `PGHOST`/`DATABASE_URL` env vars
- `kubectl` present: always verify with `cluster-info --request-timeout=3s`
- `docker` present: use `docker info` not `docker --version` (daemon may be stopped)

---

## Decision 3: Connection Validation Before Saving Config

**Decision**: Each database technology uses its native minimal connectivity probe:

| Technology | Command | Exits 0 on success |
|------------|---------|-------------------|
| PostgreSQL | `pg_isready -h localhost -p {port} -U {user} -d {db} -t 5` | Yes |
| MySQL | `mysqladmin ping -h 127.0.0.1 -P {port} -u {user} -p{pass} --connect-timeout=5` | Yes |
| MongoDB | `mongosh "mongodb://{user}:{pass}@localhost:{port}/{db}" --eval "db.adminCommand({ping:1})" --quiet --norc` | Yes |

**Rationale**: These commands open a connection and immediately close it — no SQL,
no locks, no data access. They fail fast (5s timeout) and return clear exit codes.

**On validation failure**: report exact error, ask "retry or save anyway?".
If "save anyway": add `# UNVALIDATED` comment to that config block. Never silently
save a failed connection.

---

## Decision 4: Broker CLI Commands

### SQS

```bash
# List queues with counts
aws sqs list-queues --queue-name-prefix {prefix}
aws sqs get-queue-attributes --queue-url {url} \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible

# DLQ detection
aws sqs get-queue-attributes --queue-url {url} --attribute-names RedrivePolicy

# Reprocess (native redrive, 2023+ API)
aws sqs start-message-move-task --source-arn {dlq-arn}
aws sqs list-message-move-tasks --source-arn {dlq-arn}   # monitor progress
```

Auth: `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` + `AWS_DEFAULT_REGION`, or `aws configure`.

### Kafka

```bash
# List consumer group lag
kafka-consumer-groups.sh --bootstrap-server {broker}:9092 \
  --group {group} --describe

# List DLQ topics (naming convention: .DLT or -dlt suffix)
kafka-topics.sh --bootstrap-server {broker}:9092 --list | grep -E '\.(DLT|dlq|dead)'

# Reprocess (STOP CONSUMER FIRST)
kafka-consumer-groups.sh --bootstrap-server {broker}:9092 \
  --group {group} --topic {topic} --reset-offsets --to-earliest --dry-run
kafka-consumer-groups.sh ... --execute   # after dry-run review
```

Note: `queue-reprocess` for Kafka = offset reset on the DLQ topic. Consumer must be
fully stopped. Always run `--dry-run` first and show output before `--execute`.

### Azure Service Bus

```bash
# List queues with counts
az servicebus queue list --resource-group {rg} --namespace-name {ns}
az servicebus queue show --rg {rg} --namespace-name {ns} --name {q} --query countDetails

# DLQ count
az servicebus queue show ... --query countDetails.deadLetterMessageCount
```

**Reprocess**: Azure CLI has no data-plane redrive command. Reprocess requires the
Python SDK (`azure-servicebus` + `azure-identity`). The `configure` wizard MUST warn
users that `queue-reprocess` for Azure Service Bus requires `pip install azure-servicebus
azure-identity` and Python available on PATH.

---

## Decision 5: Database CLI Adapter Commands

### MySQL (db-query adapter)

```bash
# Connect + execute (read-only)
mysql -h 127.0.0.1 -P {port} -u {user} -p{password} -D {database} \
  --connect-timeout=10 -e "{sql}"

# Avoid password in process list: use ~/.my.cnf or --login-path
# Connectivity test:
mysqladmin ping -h 127.0.0.1 -P {port} -u {user} -p{password} --connect-timeout=5
```

### MongoDB (db-query adapter)

```bash
# Connect + execute
mongosh "mongodb://{user}:{password}@127.0.0.1:{port}/{database}?authSource=admin" \
  --eval "{query}" --quiet --norc

# Connectivity test (ping command):
mongosh "mongodb://{user}:{password}@127.0.0.1:{port}/?authSource=admin" \
  --eval "db.adminCommand({ping:1})" --quiet --norc
```

Note: MongoDB queries in the skill are MQL (Mongo Query Language), not SQL.
The skill body must clarify to the user that MongoDB queries use `.find()` syntax.

---

## Decision 6: Migration Tool Adapters

### Knex (db-migrate)

```bash
# List: knex migrate:list
# Apply: knex migrate:latest
# Rollback: knex migrate:rollback
# Connection: env vars (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME) or knexfile.js
# Connectivity test: knex migrate:status (exits 0 if connection ok)
```

Requires `knexfile.js` in the working directory. The `configure` wizard should ask
for the knexfile path if `migration_tool: knex`.

### Flyway (db-migrate)

```bash
# List: flyway info
# Apply: flyway migrate
# Validate: flyway validate
# Connection: FLYWAY_URL, FLYWAY_USER, FLYWAY_PASSWORD env vars
#   or flyway.conf file
# Connectivity test: flyway info (read-only, non-destructive)
```

JDBC URL format: `jdbc:{database}://{host}:{port}/{dbname}`.
The configure wizard must ask for the JDBC URL format when `migration_tool: flyway`.

---

## Decision 7: queue-status Structural Fix

**Decision**: Migrate `queue-status/references/` to `queue-status/adapters/` and
restructure the content to match the standard adapter format (labeled steps + frontmatter).

**Rationale**: `queue-status` is the only skill using `references/` instead of `adapters/`.
This was likely an oversight in the original implementation. All other skills use
`adapters/`. Making it consistent removes a special case and allows `queue-status` to
follow the same loading pattern as other skills.

**Existing content preserved**: `references/rabbitmq.md` and `references/azure-service-bus.md`
become the basis for `adapters/rabbitmq.md` and `adapters/azure-service-bus.md`.

---

## Constitution Compliance

| Principle | Status |
|-----------|--------|
| I. Plugin-First | ✅ All changes are adapter files within existing skills — no new scripts |
| II. Context-Aware Execution | ✅ Core of this feature — auto-detection + adapter routing |
| III. Report-Oriented Output | ✅ New adapters must match existing report format from SKILL.md |
| IV. Read Before Act | ✅ Auto-detect is read-only; configure validation is read-only; db-migrate remains unchanged |
| V. Credential Safety | ✅ Validation commands use env vars / flags; `# UNVALIDATED` marker for failed connections |
