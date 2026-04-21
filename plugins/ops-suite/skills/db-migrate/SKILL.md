---
name: db-migrate
description: Run database migrations on remote environments. Identifies pending migrations, connects to the target database, runs the migration command, and verifies the result. Use when asked about "run migrations", "apply migrations", "pending schema changes", "migration status", "update schema", "db migrate". TRIGGER when: user asks "run migrations", "apply migrations", "pending migrations", "migration status", "update schema", "schema migration", "check migrations", "are there pending migrations?". SKIP: querying data (use db-query); checking service health (use service-status).
argument-hint: "[environment]"
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
model: haiku
---

## Step 0 — Load configuration

Check if `/tmp/ops-suite-session/config.json` exists:
- If yes, read it (pre-parsed by session-start hook).
- If no, read the plugin's `config.yaml`, parse it, and write to `/tmp/ops-suite-session/config.json` for other skills to reuse.
If neither exists, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `deploy.migration_tool` — determines which adapter to load
- `deploy.migration_command` — the command to run migrations
- `deploy.local_ports` — local ports for port-forwarding to databases
- `orchestrator` — for port-forward commands
- `environments` — connection details for each environment

Also read the reference at `references/commands.md` (in this skill's directory).

## Step 1 — Load adapter

Read the adapter file at `adapters/{deploy.migration_tool}.md` (in this skill's directory).
If the adapter does not exist, tell the user that the migration tool `{deploy.migration_tool}` is not yet supported and stop.

## Step 2 — Determine target environment

If `$ARGUMENTS` contains an environment name, use it. Otherwise ask the user.

**IMPORTANT: Always recommend running migrations on dev first before prod.**

## Step 3 — Identify pending migrations

Use the adapter's "list pending" command to check what migrations need to run.
If there are no pending migrations, inform the user and stop.

Show the user:
- Migration file names
- What each migration does (read the migration files if accessible)

## Step 4 — Establish database connection

The migration tool needs a database connection. This typically requires:

1. **Port-forward** to the database using the orchestrator:
   Load `${CLAUDE_PLUGIN_ROOT}/skills/port-forward/adapters/{orchestrator}.md` and use its
   "Port-forward a service (background)" command for `{env.services.database.name}`,
   local port `{deploy.local_ports.{env_name}}`, remote port `{env.services.database.port}`.
   Use `{env.services.database.namespace}` if defined, otherwise `{env.namespaces.infra}`.

2. **Credentials**: First check if `env.services.database.credentials_from` is defined in config:
   - If `pod_env:<VAR_NAME>`: load `${CLAUDE_PLUGIN_ROOT}/skills/port-forward/adapters/{orchestrator}.md`
     and use its "retrieve secret" command to read the variable from a running app pod.
   - Otherwise, use the migration adapter's credential retrieval command or ask the user.
   Never hardcode or display credentials in plain text.

3. **Set environment variables** as required by the migration tool (from adapter).

4. **Determine database name**: If `service_databases` is defined in config, use it to resolve
   the correct database name for the target service and environment. Otherwise fall back to
   `env.services.database.default_db`.

## Step 5 — Confirm migration

**ALWAYS ask for explicit confirmation before running migrations.**

Display:
```
Ready to migrate:
  Environment: {env_name}
  Database:    {env.services.database.default_db}
  Pending:     {count} migration(s)
  Files:       {migration_file_list}

This will modify the database schema. Proceed? (yes/no)
```

## Step 6 — Run migrations

Execute the migration command from `deploy.migration_command` or the adapter's default command.
Capture both stdout and stderr.

## Step 7 — Verify

After migration completes:
1. Use the adapter's "check status" command to verify all migrations are applied
2. Run a quick sanity query to confirm the database is accessible
3. Check for any error output

## Step 8 — Cleanup

1. Kill any port-forward processes
2. Unset any temporary environment variables
3. Report the result

## Output format

```
Migration Summary:
  Environment: {env_name}
  Database:    {database}
  Migrations:  {count} applied
  Status:      {success/failed}

Applied:
  - {migration_name_1}
  - {migration_name_2}

Cleanup:
  - Port-forward killed (PID {pid})
```
