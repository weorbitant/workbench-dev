# Data Model: ops-suite Full Technology Agnosticism

## Entities

### Adapter

A Markdown file that provides technology-specific commands for one skill.

| Field | Type | Constraints |
|-------|------|-------------|
| `adapter-for` | string | Required; must match a skill directory name (`db-query`, `db-migrate`, `queue-status`, `queue-triage`, `queue-reprocess`) |
| `technology` | string | Required; must match a declared option in `config.example.yaml` for that skill's technology dimension |
| `implements` | string[] | Required; each entry is a kebab-case step ID matching a `## Step X — VerbNoun` heading in the skill's `INTERFACE.md` |
| `requires` | string[] | Required; config/env keys the adapter needs to execute (e.g. `local_port`, `db_user`) |

File path convention: `plugins/ops-suite/skills/{adapter-for}/adapters/{technology}.md`

YAML frontmatter example:
```yaml
---
adapter-for: db-query
technology: mysql
implements: [step-a-connect, step-b-execute, step-c-format]
requires: [local_port, db_user, db_password, database, sql_query]
---
```

**Validation rule**: If any step listed in the skill's `INTERFACE.md` is absent from
`implements`, the skill body reports "adapter incomplete" and stops before execution.

---

### InterfaceContract

Defined in `plugins/ops-suite/skills/{skill}/INTERFACE.md`. Documents the mandatory labeled
steps every adapter for that skill must implement.

| Field | Type | Constraints |
|-------|------|-------------|
| `skill` | string | Derived from parent directory name |
| `steps` | Step[] | Ordered list; each step is mandatory unless marked optional |

**Step sub-entity**:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Kebab-case (`step-a-connect`); derived from heading `## Step A — VerbNoun` |
| `label` | string | Human-readable (`Step A — Connect`) |
| `required` | bool | Default true; false only if marked `(optional)` in INTERFACE.md |
| `description` | string | What input/output this step produces |

---

### ConfigState

Loaded at skill startup from session cache or config file.

| Field | Type | Constraints |
|-------|------|-------------|
| `orchestrator` | string | `kubernetes` \| `docker-compose` \| `ecs` \| `none` |
| `database` | string | `postgresql` \| `mysql` \| `mongodb` \| `none` |
| `message_broker` | string | `rabbitmq` \| `azure-service-bus` \| `sqs` \| `kafka` \| `none` |
| `environments` | map | Per-environment connection details (existing schema) |
| `deploy` | object | CI provider, migration tool, local ports (existing schema) |

**Cache invalidation rule** (FR-007): `/tmp/ops-suite-session/config.json` is invalidated
whenever `orchestrator`, `database`, or `message_broker` differs from the cached value.
Skills check this by comparing the current config keys against the cached keys before
reusing the session file.

---

### AutoDetectResult

Produced by the three-pass probe when no valid `config.yaml` is present.

| Field | Type | Description |
|-------|------|-------------|
| `dimension` | string | `orchestrator` \| `database` \| `message_broker` |
| `candidates` | Candidate[] | All detected options for this dimension, ordered by score descending |
| `winner` | Candidate \| null | Highest-scoring candidate; null if no candidate reaches score ≥ 1 |
| `ambiguous` | bool | True if multiple candidates share the top score (≥ 3); requires user selection |

**Candidate sub-entity**:

| Field | Type | Description |
|-------|------|-------------|
| `technology` | string | Technology name (`kubernetes`, `mysql`, etc.) |
| `score` | int | 1 (binary presence) + 3 (active context) + 5 (reachability); max 9 |
| `evidence` | string[] | Human-readable evidence strings shown to user (e.g. `kubectl context: dev-cluster`) |

**Disambiguation rule**: If exactly one candidate scores ≥ 3, propose it as default.
If multiple candidates score ≥ 3, always ask. If none score ≥ 1, leave blank and ask.

---

## State Transitions

### Adapter Loading

```
SKILL invoked
  → read ConfigState.{dimension}
  → check adapters/{technology}.md exists
    ↳ NOT FOUND → report unsupported technology, list supported options, STOP
    ↳ FOUND     → validate implements covers all INTERFACE.md steps
      ↳ INCOMPLETE → report "adapter incomplete", STOP
      ↳ COMPLETE   → execute steps A → B → C (→ D …)
```

### Auto-Detection Flow

```
SKILL invoked, no config.yaml
  → run three-pass probe for each dimension
  → produce AutoDetectResult[]
  → for each dimension:
    ↳ winner && !ambiguous → propose winner as default
    ↳ ambiguous            → list candidates ranked by score, ask user to choose
    ↳ no candidates        → leave blank, ask user to fill in
  → present proposed config YAML
  → user confirms → save config.yaml → continue SKILL execution
  → user edits    → update proposal  → save config.yaml → continue SKILL execution
```

### Connection Validation (configure wizard)

```
user provides database credentials
  → run connectivity probe (pg_isready / mysqladmin ping / mongosh ping)
    ↳ exit 0 → mark VALIDATED → proceed to next question
    ↳ non-0  → display error, ask "retry or save anyway?"
      ↳ retry      → re-run probe
      ↳ save anyway → add "# UNVALIDATED" comment to config block → save
```
