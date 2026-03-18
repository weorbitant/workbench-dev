# Commands Reference — Session 2026-03-18

> **Note:** This is a snapshot from a specific incident session on 2026-03-18, not a general reference. Pod names, credentials, and queue names are specific to that session. Use it as a template — replace values with your own.

All commands executed during the `mp-service-obligations-api` dev incident triage and remediation session.

## Environment

- **Service**: `mp-service-obligations-api`
- **Environment**: dev
- **K8s context**: `dev`
- **Namespace (apps)**: `plataformadato`
- **Namespace (infra)**: `shared-infra`
- **RabbitMQ pod**: `dev-test-afianza-rabbit-ha-56857fbcfc-ckzm7`
- **RabbitMQ vhost**: `data_platform`
- **RabbitMQ user**: `afianza` (from secret `dev-test-afianza-rabbit-ha-secret`)
- **DB**: `mp-service-obligations-api-dev` via PgBouncer in `plataformadato`
- **DB user**: `postgres` (password from secret `mp-service-obligations-api-secrets`)

---

## 1. Service Status

### List pods for a service
```bash
kubectl --context=dev get pods -n plataformadato | grep mp-service-obligations-api
```

### Check restart counts
```bash
kubectl --context=dev get pods -n plataformadato \
  -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,RESTARTS:.status.containerStatuses[0].restartCount,AGE:.metadata.creationTimestamp \
  | grep mp-service-obligations-api
```

### Resource usage (CPU/memory)
```bash
kubectl --context=dev top pods -n plataformadato | grep mp-service-obligations-api
```

### Deployment status
```bash
kubectl --context=dev get deploy -n plataformadato | grep mp-service-obligations-api
```

---

## 2. Service Logs

### Recent errors from all replicas
```bash
kubectl --context=dev logs -l app=mp-service-obligations-api -n plataformadato \
  --tail=200 --timestamps | grep -iE "error|exception|fail|fatal|panic"
```

### Count and classify errors
```bash
kubectl --context=dev logs -l app=mp-service-obligations-api -n plataformadato \
  --tail=1000 | grep -iE "error|exception" | sort | uniq -c | sort -rn | head -20
```

### Logs from a specific pod with timestamps
```bash
kubectl --context=dev logs mp-service-obligations-api-965897fc5-2zzm8 \
  -n plataformadato --tail=50 --timestamps
```

### Logs since a time period
```bash
kubectl --context=dev logs -l app=mp-service-obligations-api -n plataformadato \
  --since=5m --timestamps
```

### Errors since a time period
```bash
kubectl --context=dev logs -l app=mp-service-obligations-api -n plataformadato \
  --since=5m --timestamps | grep -iE "error|exception"
```

---

## 3. Port Forwarding

### PgBouncer (database) — namespace is plataformadato, NOT shared-infra
```bash
kubectl --context=dev port-forward svc/pd-infra-pgbouncer 16432:6432 -n plataformadato &
```

### RabbitMQ Management API
```bash
kubectl --context=dev port-forward -n shared-infra \
  dev-test-afianza-rabbit-ha-56857fbcfc-ckzm7 15672:15672 &
```

### Verify port-forward is active
```bash
lsof -i :16432
```

### Kill port-forward
```bash
kill $(lsof -t -i :16432)
```

---

## 4. Credential Retrieval

### PostgreSQL password
```bash
kubectl --context=dev get secret mp-service-obligations-api-secrets \
  -n plataformadato -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d
```

### RabbitMQ credentials
```bash
kubectl --context=dev get secret dev-test-afianza-rabbit-ha-secret \
  -n shared-infra -o jsonpath='{.data}' | jq -r 'to_entries[] | "\(.key): \(.value | @base64d)"'
```

### Test RabbitMQ auth
```bash
curl -s -u 'afianza:${RABBIT_PASSWORD}' 'http://localhost:15672/api/whoami'
```

---

## 5. Database Migrations (MikroORM)

### List pending migrations
```bash
POSTGRES_HOST=localhost POSTGRES_PORT=16432 \
POSTGRES_DB=mp-service-obligations-api-dev \
POSTGRES_USER=postgres POSTGRES_PASSWORD='${DB_PASSWORD}' \
  npx mikro-orm migration:pending
```

### Run all pending migrations
```bash
POSTGRES_HOST=localhost POSTGRES_PORT=16432 \
POSTGRES_DB=mp-service-obligations-api-dev \
POSTGRES_USER=postgres POSTGRES_PASSWORD='${DB_PASSWORD}' \
  npx mikro-orm migration:up
```

### Verify no pending migrations remain
```bash
POSTGRES_HOST=localhost POSTGRES_PORT=16432 \
POSTGRES_DB=mp-service-obligations-api-dev \
POSTGRES_USER=postgres POSTGRES_PASSWORD='${DB_PASSWORD}' \
  npx mikro-orm migration:pending
```

### Verify migrations in DB (node, since psql not available)
```bash
node -e "
const { Client } = require('pg');
const c = new Client({
  host:'localhost', port:16432,
  database:'mp-service-obligations-api-dev',
  user:'postgres', password:'${DB_PASSWORD}'
});
c.connect()
  .then(() => c.query('SELECT name, executed_at FROM mikro_orm_migrations ORDER BY executed_at DESC LIMIT 5'))
  .then(r => { console.table(r.rows); c.end(); })
  .catch(e => { console.error(e.message); c.end(); });
"
```

---

## 6. Database Queries

### Generic query via node pg client
```bash
node -e "
const { Client } = require('pg');
const c = new Client({
  host: 'localhost', port: 16432,
  database: 'mp-service-obligations-api-dev',
  user: 'postgres', password: '${DB_PASSWORD}'
});
c.connect()
  .then(() => c.query(\`SELECT * FROM assignment ORDER BY created_at DESC LIMIT 20\`))
  .then(r => {
    if (r.rows && r.rows.length > 0) { console.table(r.rows); console.log('Rows:', r.rowCount); }
    else { console.log('No rows returned.'); }
    c.end();
  })
  .catch(e => { console.error('ERROR:', e.message); c.end(); process.exit(1); });
"
```

### Count records
```bash
# Same pattern, change the SQL:
# SELECT COUNT(*) as total FROM employee
# SELECT COUNT(*) as total FROM assignment
```

---

## 7. Queue Management (RabbitMQ)

### List all DLQs with messages (via rabbitmqctl)
```bash
kubectl --context=dev exec -n shared-infra dev-test-afianza-rabbit-ha-56857fbcfc-ckzm7 -- \
  rabbitmqctl list_queues -p data_platform name messages consumers state \
  --formatter table | grep -iE "dlq|dead.letter" | awk '$2 > 0'
```

### Check live queue status (consumers, messages)
```bash
kubectl --context=dev exec -n shared-infra dev-test-afianza-rabbit-ha-56857fbcfc-ckzm7 -- \
  rabbitmqctl list_queues -p data_platform name messages consumers \
  --formatter table | grep -E "^obligations-api" | grep -v dead_letter
```

### Peek DLQ messages (non-destructive)
```bash
curl -s -u 'afianza:${RABBIT_PASSWORD}' \
  -X POST 'http://localhost:15672/api/queues/data_platform/${QUEUE_NAME_URL_ENCODED}/get' \
  -H 'content-type: application/json' \
  -d '{"count":3,"ackmode":"ack_requeue_true","encoding":"auto"}' | jq '.[] | {
    routing_key: .routing_key,
    death_reason: .properties.headers["x-first-death-reason"],
    death_queue: .properties.headers["x-first-death-queue"],
    payload_preview: (.payload | if length > 200 then .[:200] + "..." else . end)
  }'
```

### URL encoding for queue names
```
obligations-api:client:persisted.dead_letter
→ obligations-api%3Aclient%3Apersisted.dead_letter

obligations-api:provided-service:persisted.dead_letter
→ obligations-api%3Aprovided-service%3Apersisted.dead_letter

obligations-api:client-assignment:deleted.dead_letter
→ obligations-api%3Aclient-assignment%3Adeleted.dead_letter
```

### Purge a DLQ
```bash
kubectl --context=dev exec -n shared-infra dev-test-afianza-rabbit-ha-56857fbcfc-ckzm7 -- \
  rabbitmqctl purge_queue -p data_platform 'obligations-api:client-assignment:deleted.dead_letter'
```

### Create a temporary shovel (move DLQ → live queue)
```bash
curl -s -u 'afianza:${RABBIT_PASSWORD}' \
  -X PUT 'http://localhost:15672/api/parameters/shovel/data_platform/reprocess-${SHOVEL_NAME}' \
  -H 'content-type: application/json' \
  -d '{
    "value": {
      "src-protocol": "amqp091",
      "src-uri": "amqp:///data_platform",
      "src-queue": "${DLQ_NAME}",
      "dest-protocol": "amqp091",
      "dest-uri": "amqp:///data_platform",
      "dest-queue": "${TARGET_QUEUE}",
      "src-prefetch-count": 100,
      "ack-mode": "on-confirm",
      "src-delete-after": "queue-length"
    }
  }'
```

### Monitor shovel progress
```bash
curl -s -u 'afianza:${RABBIT_PASSWORD}' \
  'http://localhost:15672/api/shovels/data_platform' | \
  jq '.[] | select(.name | startswith("reprocess-")) | {name, state}'
```

### Check shovel plugin is enabled
```bash
kubectl --context=dev exec -n shared-infra dev-test-afianza-rabbit-ha-56857fbcfc-ckzm7 -- \
  rabbitmq-plugins list | grep rabbitmq_shovel
```

---

## 8. Discovery Commands

### List all secrets in a namespace
```bash
kubectl --context=dev get secret -n plataformadato -o name
kubectl --context=dev get secret -n shared-infra -o name
```

### List all services in a namespace
```bash
kubectl --context=dev get svc -n plataformadato
kubectl --context=dev get svc -n shared-infra
```

### Find a service by keyword
```bash
kubectl --context=dev get svc -n plataformadato | grep -i pg
kubectl --context=dev get svc -n shared-infra | grep -i rabbit
```

---

## Session Timeline

| Time | Skill | Action | Result |
|------|-------|--------|--------|
| 11:00 | service-logs | Check errors | Found 2 error types: missing column + missing table |
| 11:02 | service-status | Check pods | 2/2 healthy, 0 restarts |
| 11:05 | db-migrate | List pending | 4 migrations pending |
| 11:18 | db-migrate | Apply migrations | 4 applied successfully |
| 11:20 | service-logs | Verify post-migration | 0 errors (confirmed fix) |
| 11:22 | db-query | Check assignments | Empty table (expected) |
| 11:25 | queue-triage | Survey DLQs | 3 DLQs: 1 + 106K + 283K messages |
| 11:28 | queue-reprocess | Purge + shovel | 1 purged, 390K shoveled back |
| 11:35 | — | Shovels completed | 0 DLQ messages, 0 errors |
