# Interface Contract: db-migrate

Every adapter file at `plugins/ops-suite/skills/db-migrate/adapters/{technology}.md` MUST
implement all steps below. The adapter YAML frontmatter must declare:

```yaml
implements: [step-a-list, step-b-apply, step-c-verify]
```

---

## Step A — List

**ID**: `step-a-list`

**Input**: `local_port` (if DB access needed), `migration_tool`, connection credentials

**Output**: A table of pending migrations and applied migrations

**Contract**: Adapter lists all pending and recently applied migrations. Output MUST show:
- Migration name / filename
- Applied timestamp (or "pending")
- Total count of pending migrations

---

## Step B — Apply

**ID**: `step-b-apply`

**Input**: Confirmation from user (SKILL.md body collects this before calling the adapter)

**Output**: CLI output from the migration tool showing which migrations ran

**Contract**: Adapter runs the migration tool's apply command (`migrate:latest`, `flyway
migrate`, etc.). Must show the exact command before executing. If `deploy.migration_command`
is set in config, use that instead of the default.

---

## Step C — Verify

**ID**: `step-c-verify`

**Input**: Same connection credentials as Step A

**Output**: Confirmation that all expected migrations are now marked applied

**Contract**: Adapter re-queries the migration table (or runs `migration:list`) and reports
the post-migration state. Zero pending migrations is a success. Any pending migration after
apply is reported as a warning.

---

## Supported Technologies

| Technology | Adapter file | Status |
|------------|-------------|--------|
| `mikro-orm` | `adapters/mikro-orm.md` | Existing |
| `typeorm` | `adapters/typeorm.md` | Existing |
| `knex` | `adapters/knex.md` | New (this feature) |
| `flyway` | `adapters/flyway.md` | New (this feature) |
