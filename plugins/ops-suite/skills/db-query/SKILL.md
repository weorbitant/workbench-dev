---
name: db-query
description: Execute read-only queries against databases. Connects to the target environment's database, runs SQL queries, and formats results. Use when asked about "query database", "db query", "SQL", "check data", "database lookup", "count records", "find rows". TRIGGER when: user asks "query X table", "count records", "find rows where", "SQL query", "check the data", "how many X?", "look up Y in the database", "run a query". SKIP: running migrations (use db-migrate); service health checks (use service-status).
argument-hint: "[query description] [environment]"
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
model: sonnet
---

## Step 0 — Load configuration

Check if `/tmp/ops-suite-session/config.json` exists:
- If yes, read it (pre-parsed by session-start hook).
- If no, read the plugin's `config.yaml`, parse it, and write to `/tmp/ops-suite-session/config.json` for other skills to reuse.
If neither exists, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `database` — determines which adapter to load (postgresql, mysql, mongodb)
- `orchestrator` — for port-forward commands
- `environments` — connection details
- `deploy.local_ports` — local ports for database connections

Also read the reference at `references/query-examples.md` (in this skill's directory) for common query patterns.

## Step 1 — Load adapter

Read the adapter file at `adapters/{database}.md` (in this skill's directory).
If the adapter does not exist, tell the user that the database `{database}` is not yet supported and stop.

## Step 2 — Determine target environment

If `$ARGUMENTS` contains an environment name, use it. Otherwise ask the user.

## Step 3 — Establish database connection

Check if a port-forward is already active on the expected local port (`deploy.local_ports.{env_name}`).

If not active:
1. Start a port-forward using the orchestrator:
   ```
   kubectl --context={env.context} port-forward svc/{env.services.database.name} {deploy.local_ports.{env_name}}:{env.services.database.port} -n {env.services.database.namespace || env.namespaces.infra} &
   ```
2. Verify the connection is working

Retrieve or ask for credentials. Never hardcode credentials.

## Step 4 — Formulate query

If `$ARGUMENTS` contains a natural language description:
- Translate it into a SQL query (or equivalent for the database type)
- Show the query to the user and ask for confirmation before running

If `$ARGUMENTS` contains raw SQL:
- Use it directly, but validate it first

**Constraints:**
- Default to read-only queries (SELECT, EXPLAIN)
- If the user requests a write operation (INSERT, UPDATE, DELETE), warn them and ask for explicit confirmation
- Always use LIMIT to prevent unbounded result sets (default LIMIT 50)
- Wrap queries in a transaction with ROLLBACK for safety when testing writes

## Step 5 — Execute query

Use the adapter's query execution command.
The script at `scripts/query.js` (in this skill's directory) can be used as a helper for PostgreSQL.

## Step 6 — Format and present results

Present results in a clear, readable format:

```
Environment: {env_name}
Database:    {database_name}
Query:       {sql_query}
Rows:        {row_count}

Results:
| column_1 | column_2 | column_3 |
|----------|----------|----------|
| value    | value    | value    |

Query time: {duration}ms
```

If results are too many to display, show the first 20 rows and provide the total count.

## Step 7 — Cleanup

If a port-forward was started in this session, provide the cleanup command but do not kill it automatically (the user may want to run more queries).

## Important notes

- Always use parameterized queries when possible to prevent SQL injection
- Be aware of PgBouncer limitations: avoid multi-statement queries, SET commands, or prepared statements when connecting through PgBouncer
- For large datasets, suggest using EXPLAIN ANALYZE first to estimate query cost
