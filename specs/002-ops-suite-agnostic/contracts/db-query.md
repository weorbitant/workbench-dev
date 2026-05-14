# Interface Contract: db-query

Every adapter file at `plugins/ops-suite/skills/db-query/adapters/{technology}.md` MUST
implement all steps below. The adapter YAML frontmatter must declare:

```yaml
implements: [step-a-connect, step-b-execute, step-c-format]
```

---

## Step A — Connect

**ID**: `step-a-connect`

**Input**: `local_port`, `db_user`, `db_password`, `database`

**Output**: Confirmation that the connection is alive (e.g. exit code 0 from a ping command)

**Contract**: Adapter shows the connection command (with password redacted), runs it, and
reports success or failure. On failure, surfaces the exact error message.

**Note**: The port-forward step that exposes the database on `local_port` is handled by the
`db-query/SKILL.md` body (Step 3) via the `port-forward` skill's adapter — adapters do NOT
manage the tunnel themselves.

---

## Step B — Execute

**ID**: `step-b-execute`

**Input**: `sql_query` (SQL or equivalent query language for the technology)

**Output**: Raw result data from the database

**Contract**: Adapter executes the query read-only. For SQL databases this is a `SELECT` or
`EXPLAIN`. For MongoDB this is a `.find()` or aggregation. Default result limit: 50 rows.
Must use parameterized/safe invocation — no shell-interpolated query strings.

---

## Step C — Format

**ID**: `step-c-format`

**Input**: Raw result from Step B

**Output**: Structured report in this exact format:

```
Environment: {env_name}
Database:    {database_name}
Query:       {query}
Rows:        {row_count}

Results:
| column_1 | column_2 | … |
|----------|----------|---|
| value    | value    | … |

Query time: {duration}ms
```

**Contract**: Table format for tabular results. For document stores (MongoDB), format as
a JSON-like list with clear key/value rows. If results exceed 20 rows, show first 20 and
append "… {N} more rows".

---

## Supported Technologies

| Technology | Adapter file | Status |
|------------|-------------|--------|
| `postgresql` | `adapters/postgresql.md` | Existing |
| `mysql` | `adapters/mysql.md` | New (this feature) |
| `mongodb` | `adapters/mongodb.md` | New (this feature) |
