# Skill Chaining

Skills can reference other skills using the `ops-suite:<skill-name>` convention.

## How it works

There are two types of chains depending on whether the target skill is read-only or destructive.

### Read-only skills (auto-chain)

These skills have no `disable-model-invocation` and can be invoked automatically:
- `ops-suite:service-status`
- `ops-suite:service-logs`
- `ops-suite:db-query`
- `ops-suite:queue-status`
- `ops-suite:port-forward`

Syntax in SKILL.md:
```
Use ops-suite:service-status with arguments: {service} {env_name}.
Use session state from /tmp/ops-suite-session/ — do not re-ask for environment or re-load config.
```

### Destructive skills (suggest, don't invoke)

These skills keep `disable-model-invocation: true` and cannot be auto-invoked:
- `ops-suite:deploy`
- `ops-suite:db-migrate`
- `ops-suite:queue-reprocess`

When a skill wants to chain to a destructive skill, it shows a message instead:
```
## Next steps

The following action requires explicit invocation:
→ Run `/ops-suite:db-migrate dev` to apply pending migrations.
```

## Chaining rules

1. The chained skill inherits session state (config, env, connections from `/tmp/ops-suite-session/`)
2. The chained skill does NOT re-ask for environment if already selected
3. Read-only skills can be invoked directly mid-step
4. Destructive skills are suggested via a "Next steps" message
5. Chain depth is max 3 (prevent infinite loops)

## Common chains

| From | To | Type | When |
|------|-----|------|------|
| deploy | service-status | auto | After deployment to verify health |
| deploy | service-logs | auto | After deployment to check for errors |
| deploy | db-migrate | **suggest** | After deployment if migrations pending |
| queue-triage | service-logs | auto | To find consumer errors |
| queue-triage | service-status | auto | To check if consumer is running |
| queue-triage | db-query | auto | To verify entity state in database |
| queue-triage | queue-reprocess | **suggest** | After triage, if messages are reprocessable |
| queue-reprocess | queue-triage | **suggest** | Pre-flight if no recent triage |
| service-status | service-logs | auto | When unhealthy pod found |
| service-logs | db-migrate | **suggest** | When DB schema errors found |
