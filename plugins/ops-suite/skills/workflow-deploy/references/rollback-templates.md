# Rollback Templates

Used by workflow-deploy to generate a rollback plan before deployment.
Select the template that matches the deployment type and fill in the values.

## Template: Code-only (no migrations)

```
Rollback Plan
─────────────────────────────────────────────
  If deploy fails or service is unhealthy:

  1. Trigger rollback via CI:
     Previous image tag: {current_tag}
     Run: {ci_rollback_command from adapter}

  2. Verify health:
     /ops-suite:service-status {service} {env_name}

  3. Check logs are clean:
     /ops-suite:service-logs {service} {env_name}
```

## Template: Includes database migrations

```
Rollback Plan
─────────────────────────────────────────────
  ⚠️  This deployment includes database migrations.
  Rollback requires two steps: code + migrations.

  CASE A — Deploy fails BEFORE migrations run:
    1. Trigger rollback via CI (previous tag: {current_tag}).
    No migration rollback needed.

  CASE B — Deploy fails AFTER migrations run:
    1. Roll back code:
       Trigger rollback via CI (previous tag: {current_tag}).
    2. Roll back migrations (CAUTION — may affect data):
       /ops-suite:db-migrate {env_name}  → select rollback option
    3. Verify: /ops-suite:service-status {service} {env_name}
    4. Logs:   /ops-suite:service-logs {service} {env_name}

  ⚠️  If migrations created new columns with data already written,
      rolling back may cause data loss. Confirm with team first.
```

## Template: Not requested

```
No rollback plan generated (not requested).
To generate one, run /ops-suite:workflow-deploy again and answer "yes" to rollback plan.
```
