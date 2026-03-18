# Session State Management

Skills share state through files in `/tmp/ops-suite-session/`.

## State files

| File | Content | Written by | Read by |
|------|---------|-----------|---------|
| `config.json` | Parsed config.yaml as JSON | session-start hook | All skills |
| `env.json` | Selected environment + resolved config | Any skill that selects env | All skills |
| `credentials.json` | Retrieved credentials (DB, broker) | Any skill that fetches creds | All DB/broker skills |
| `port-forwards.json` | Active port-forwards `{service: {pid, localPort}}` | Any skill that creates one | All skills |
| `last-triage.json` | Last queue-triage results | queue-triage | queue-reprocess |

## Lifecycle

- Created by `session-start.sh` hook (mkdir + parse config)
- Cleaned up when session ends or user runs `/ops-suite:cleanup`
- Skills check for existing state before creating new connections

## Port-forward reuse

Before creating a port-forward, check `port-forwards.json`:
1. If entry exists for the service, check if PID is still alive (`kill -0 $PID 2>/dev/null`)
2. If alive, reuse the existing port
3. If dead, remove entry and create new

## Credential caching

Credentials are cached in `credentials.json` for the session:
- Key: `{env_name}:{service}` (e.g., `dev:database`, `dev:broker`)
- Value: `{user, password}` (never logged or displayed)
- Skills check cache before running `kubectl get secret`

## How to use in SKILL.md Step 0

```markdown
## Step 0 — Load configuration

Check if `/tmp/ops-suite-session/config.json` exists:
- If yes, read it (pre-parsed by session hook).
- If no, read the plugin's `config.yaml`, parse it, and cache to `/tmp/ops-suite-session/config.json`.

Check if `/tmp/ops-suite-session/env.json` exists:
- If yes and the environment matches, use it.
- If no, determine the environment from arguments and cache it.
```
