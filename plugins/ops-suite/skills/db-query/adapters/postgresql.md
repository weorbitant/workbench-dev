# PostgreSQL Adapter — db-query

## Execute a query using node and pg module

```bash
node -e "
const { Client } = require('pg');
const c = new Client({
  host: 'localhost',
  port: {local_port},
  database: '{database}',
  user: '{db_user}',
  password: '{db_password}'
});
c.connect()
  .then(() => c.query(\`{sql_query}\`))
  .then(r => {
    if (r.rows && r.rows.length > 0) {
      console.table(r.rows);
      console.log('Rows:', r.rowCount);
    } else {
      console.log('No rows returned. Affected:', r.rowCount);
    }
    c.end();
  })
  .catch(e => { console.error('ERROR:', e.message); c.end(); process.exit(1); });
"
```

## Execute using the query.js helper script

```bash
DB_HOST=localhost DB_PORT={local_port} DB_NAME={database} DB_USER={db_user} DB_PASSWORD={db_password} \
  node ${CLAUDE_PLUGIN_ROOT}/skills/db-query/scripts/query.js "{sql_query}"
```

## Execute using psql (if available)

```bash
PGPASSWORD='{db_password}' psql -h localhost -p {local_port} -U {db_user} -d {database} -c "{sql_query}"
```

## PgBouncer constraints

When connecting through PgBouncer (common in production):
- Do NOT use prepared statements
- Do NOT use `SET` commands (they may apply to a different connection)
- Do NOT use multi-statement queries separated by `;`
- Use simple query protocol: each query in a separate execution
- Avoid `LISTEN/NOTIFY`

## Common query patterns

### Count records in a table
```sql
SELECT COUNT(*) FROM {table};
```

### Find records by column value
```sql
SELECT * FROM {table} WHERE {column} = '{value}' LIMIT 50;
```

### Recent records
```sql
SELECT * FROM {table} ORDER BY created_at DESC LIMIT 20;
```

### Table structure
```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = '{table}'
ORDER BY ordinal_position;
```

### Table sizes
```sql
SELECT relname AS table, pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;
```

### Active connections
```sql
SELECT datname, usename, state, query_start, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;
```

### Explain a query
```sql
EXPLAIN ANALYZE {sql_query};
```
