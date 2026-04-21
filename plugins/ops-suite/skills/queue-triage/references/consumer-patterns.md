# Consumer Patterns — Framework-Specific Search Guide

Load this reference in queue-triage Step 6 when you know the consumer framework.

---

## NestJS + @golevelup/nestjs-rabbitmq

### Find subscription config

Subscriptions are typically declared in a module config file:

```bash
grep -r "subscriptions" src/config/ --include="*.ts" -A 20
grep -r "RabbitMQModule.forRoot" src/ --include="*.ts" -A 30
```

Look for entries like:
```typescript
subscriptions: {
  mySubscriptionName: { routingKey: 'some.routing.key', queue: 'queue_name' }
}
```

### Verify subscribe() call exists

```bash
grep -r "subscribe('" src/ --include="*.ts"
```

Compare all subscription names in config vs all `subscribe('...')` calls. Any name in config
without a matching `subscribe()` call = orphaned config (messages go to DLQ with no consumer).

### Find the subscriber class

Consumer classes typically live in `src/**/application/amqp/` or `src/**/infrastructure/amqp/`:

```bash
find src/ -path "*/amqp/*.ts" -o -path "*/subscribers/*.ts" | head -20
```

### Check registered subscriptions at bootstrap

Look for `onApplicationBootstrap()` in subscriber classes — this is where `subscribe()` calls are made:

```bash
grep -r "onApplicationBootstrap" src/ --include="*.ts" -l
```

Read the method body to see which subscriptions are actually registered at runtime.

### Common failure modes in NestJS

| Pattern | What to search for | Root cause |
|---------|-------------------|------------|
| `subscribe()` call missing | `grep -r "subscribe("` returns no match for that name | Handler was removed or renamed |
| Subscription in config, no handler | Config has entry, no `onApplicationBootstrap` with it | Orphaned config |
| Handler throws uncaught error | `grep -r "nack\|reject" src/` — handler may not handle errors | Missing try/catch in handler |
| DTO validation fails | Look for `class-validator` decorators in the DTO | Producer changed payload shape |

---

## Spring AMQP (Java/Kotlin)

### Find the listener

```bash
grep -r "@RabbitListener" src/ --include="*.java" --include="*.kt" -l
grep -r "queues = " src/ --include="*.java" --include="*.kt"
```

### Check the binding

```bash
grep -r "@Bean" src/ --include="*.java" --include="*.kt" -A 5 | grep -A 5 "Queue\|Binding"
```

---

## Celery (Python)

### Find the task handler

```bash
grep -r "@app.task\|@celery.task\|@shared_task" . --include="*.py" -l
grep -r "queue=" . --include="*.py" | grep "{queue_name}"
```

### Check task routing

```bash
grep -r "task_routes\|CELERY_ROUTES" . --include="*.py"
```
