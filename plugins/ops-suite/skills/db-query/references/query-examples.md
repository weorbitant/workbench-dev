# db-query — Common Query Examples

These examples use placeholders. Replace `{table}`, `{column}`, `{value}` with actual values.

## Data exploration

### List all tables
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' ORDER BY table_name;
```

### Table structure
```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = '{table}' ORDER BY ordinal_position;
```

### Table row counts (approximate)
```sql
SELECT relname AS table_name, n_live_tup AS row_count
FROM pg_stat_user_tables ORDER BY n_live_tup DESC;
```

### Table sizes
```sql
SELECT relname AS table, pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC LIMIT 20;
```

## Record lookup

### Find by ID
```sql
SELECT * FROM {table} WHERE id = '{id}';
```

### Find by column value
```sql
SELECT * FROM {table} WHERE {column} = '{value}' LIMIT 50;
```

### Search text columns
```sql
SELECT * FROM {table} WHERE {column} ILIKE '%{pattern}%' LIMIT 50;
```

### Recent records
```sql
SELECT * FROM {table} ORDER BY created_at DESC LIMIT 20;
```

## Aggregations

### Count by status
```sql
SELECT {status_column}, COUNT(*) FROM {table}
GROUP BY {status_column} ORDER BY COUNT(*) DESC;
```

### Daily counts
```sql
SELECT DATE(created_at) AS day, COUNT(*)
FROM {table}
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY day ORDER BY day;
```

## Performance and diagnostics

### Active queries
```sql
SELECT pid, usename, state, query_start, LEFT(query, 100) AS query
FROM pg_stat_activity WHERE state != 'idle' ORDER BY query_start;
```

### Long-running queries
```sql
SELECT pid, usename, state, NOW() - query_start AS duration, LEFT(query, 100) AS query
FROM pg_stat_activity WHERE state = 'active' AND NOW() - query_start > INTERVAL '10 seconds';
```

### Index usage
```sql
SELECT relname AS table, indexrelname AS index, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes ORDER BY idx_scan DESC LIMIT 20;
```

### Unused indexes
```sql
SELECT relname AS table, indexrelname AS index, pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes WHERE idx_scan = 0 ORDER BY pg_relation_size(indexrelid) DESC;
```

### Query plan
```sql
EXPLAIN ANALYZE {sql_query};
```

## Safety patterns

### Read-only transaction wrapper
```sql
BEGIN READ ONLY;
{sql_query};
ROLLBACK;
```

### Preview before write
```sql
BEGIN;
{write_query};
-- Review the result
SELECT * FROM {table} WHERE {condition} LIMIT 10;
ROLLBACK; -- Change to COMMIT only after verification
```
