# Safety Gates

## Skill classification

| Skill | Type | `disable-model-invocation` | Can be auto-chained |
|-------|------|---------------------------|---------------------|
| service-status | read-only | No | Yes |
| service-logs | read-only | No | Yes |
| db-query | read-only | No | Yes |
| queue-status | read-only | No | Yes |
| port-forward | read-only | No | Yes |
| deploy | **destructive** | **Yes** | No — suggest via "Next steps" |
| db-migrate | **destructive** | **Yes** | No — suggest via "Next steps" |
| queue-reprocess | **destructive** | **Yes** | No — suggest via "Next steps" |

## How chaining works with safety

- **Read-only → Read-only**: Auto-chain. Example: service-status finds unhealthy pod → automatically runs service-logs.
- **Read-only → Destructive**: Suggest. Example: service-logs finds schema error → shows "→ Run `/ops-suite:db-migrate dev`".
- **Destructive → Read-only**: Auto-chain. Example: deploy finishes → automatically runs service-status and service-logs.
- **Destructive → Destructive**: Suggest. Example: deploy finishes → shows "→ Run `/ops-suite:db-migrate dev`".

## "Next steps" format

When a skill cannot auto-chain to a destructive skill, it outputs:

```
Next steps:
  → Run `/ops-suite:db-migrate {env_name}` to apply pending migrations.
  → Run `/ops-suite:queue-reprocess {dlq_name} {env_name}` to reprocess failed messages.
```

The user then explicitly invokes the destructive skill.
