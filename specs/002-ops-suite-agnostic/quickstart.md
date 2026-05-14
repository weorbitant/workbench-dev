# Quickstart: ops-suite Full Technology Agnosticism

## For implementers

### 1. Writing a new adapter

Create `plugins/ops-suite/skills/{skill}/adapters/{technology}.md` with this structure:

```markdown
---
adapter-for: {skill}
technology: {technology}
implements: [{step-ids}]
requires: [{config-keys}]
---

# {Technology} Adapter — {skill}

## Step A — VerbNoun

... bash commands using {template_vars} from config ...

## Step B — VerbNoun

...

## Step C — VerbNoun

...
```

Step IDs are kebab-case versions of the heading: `## Step A — Connect` → `step-a-connect`.

Template variables use `{camelCase}` syntax matching the config.yaml schema (e.g.
`{env.context}`, `{local_port}`, `{db_user}`).

### 2. Validating adapter completeness

Before the adapter is accepted, verify:

1. The frontmatter `implements` array lists ALL step IDs from the skill's `INTERFACE.md`
2. All `requires` keys are available in the config schema (check `config.example.yaml`)
3. The output format matches the report format specified in the skill's contract (see
   `specs/002-ops-suite-agnostic/contracts/{skill}.md`)
4. No credentials appear in the command output (use `{password}` template var, not literal)

### 3. Running the acceptance scenarios

For each new adapter, run the corresponding acceptance scenario from `spec.md`:

```
# Example: testing mysql adapter
1. Set database: mysql in config.yaml
2. Start port-forward to a MySQL instance on local_port
3. Run /ops-suite:db-query
4. Verify: connection established, query returns tabular results, format matches postgresql output
```

### 4. Auto-detection flow (configure + SKILL.md edits)

The auto-detect behavior lives in `skills/configure/auto-detect.md`. When implementing:

- Three-pass probe fires in `configure/SKILL.md` when `config.yaml` is absent or technology
  keys are empty
- Pass 1 (binary): `command -v {cli}` — score 1
- Pass 2 (active context): context-specific commands — score 3
- Pass 3 (reachability): network/daemon check with 3s timeout — score 5
- Present ranked candidates; propose highest-score winner if unambiguous (only one ≥ 3)
- User confirms → write `config.yaml` → return to calling skill

### 5. queue-status migration

The `queue-status/references/` directory contains legacy files. During implementation:

1. Create `queue-status/adapters/` directory
2. Copy `references/rabbitmq.md` → `adapters/rabbitmq.md` (add INTERFACE.md frontmatter)
3. Copy `references/azure-service-bus.md` → `adapters/azure-service-bus.md` (add frontmatter)
4. Add `adapters/sqs.md` and `adapters/kafka.md`
5. Edit `queue-status/SKILL.md`: change `references/rabbitmq.md` load to `adapters/{message_broker}.md`
6. Leave `references/` in place (backward compat); do NOT delete

## For users

### Switching technologies

Edit `~/.config/ops-suite/config.yaml` (or the plugin's `config.yaml`):

```yaml
database: mysql          # was: postgresql
message_broker: sqs      # was: rabbitmq
```

On next invocation, the session cache at `/tmp/ops-suite-session/config.json` is invalidated
automatically and the new adapters are loaded.

### First run (no config)

Run any ops-suite skill. The system will:
1. Detect available CLIs and active contexts
2. Propose a pre-filled config
3. Ask for your confirmation or corrections
4. Save and continue immediately — no re-run needed

### Supported technologies at completion of this feature

| Dimension | Supported values |
|-----------|-----------------|
| `orchestrator` | `kubernetes`, `docker-compose`, `ecs` |
| `database` | `postgresql`, `mysql`, `mongodb` |
| `message_broker` | `rabbitmq`, `sqs`, `kafka`, `azure-service-bus` |
| `migration_tool` | `mikro-orm`, `typeorm`, `knex`, `flyway` |
