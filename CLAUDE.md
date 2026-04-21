# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Pure Markdown + YAML skill collection for Claude Code. No build, no tests, no linting — validation is manual (read and review skill files). The only commands you'll run are `git` operations.

## Architecture: Config + Adapters

Every skill follows the same pattern:

```
config.yaml  →  SKILL.md  →  adapters/<technology>.md
```

1. The user defines their stack once in `config.yaml` (`orchestrator: kubernetes`, `message_broker: rabbitmq`, etc.)
2. Each `SKILL.md` reads config and loads the right adapter at runtime
3. Adapters contain actual CLI commands with `{config.X.Y}` placeholders

**To add support for a new technology**: create `adapters/<tech>.md` inside the skill folder — no changes to `SKILL.md` or config schema needed.

## Plugin layout

```
plugins/
  ops-suite/           # Infrastructure: status, logs, deploy, DB, queues
    skills/<name>/
      SKILL.md         # Frontmatter + step-by-step instructions
      adapters/        # One file per supported technology
      references/      # Deep docs loaded on-demand (keep SKILL.md < 500 lines)
    commands/          # Command shims (.md) that invoke each skill
    hooks/             # hooks.json + session-start.sh
    runtime/           # Shared docs: chaining.md, safety.md, session-state.md
    config.example.yaml
    config.yaml        # User's actual config (gitignored)
  refinery/            # Roadmap refinement: tickets, design, docs, sprints
  creating-skills/     # Meta-skill for authoring new skills
.claude-plugin/
  marketplace.json     # Plugin registry (name, version, source paths)
```

## SKILL.md frontmatter

Key fields when creating or editing skills:

| Field | Notes |
|-------|-------|
| `name` | Kebab-case, becomes the slash-command |
| `description` | **Most critical** — drives auto-invocation. Start with "Use when…" + natural-language triggers. Max 1024 chars. |
| `disable-model-invocation: true` | Required for all destructive ops (deploy, migrate, reprocess). Prevents auto-chaining. |
| `allowed-tools` | Restrict what the skill can call |
| `model` | Override per-skill (e.g. `haiku` for cheap read-only checks) |
| `argument-hint` | Autocomplete hint shown to user |

## Session state (ops-suite)

Skills share state through `/tmp/ops-suite-session/`:

- `config.json` — parsed `config.yaml`, written by the `session-start.sh` hook and cached for the session
- `env.json` — selected environment (planned)
- `credentials.json` — DB/broker credentials (planned)
- `port-forwards.json` — active port-forward PIDs (planned)

Step 0 in every skill checks for `/tmp/ops-suite-session/config.json` before re-parsing config.

## Skill chaining rules

**Read-only skills** (no `disable-model-invocation`) can be auto-invoked mid-step:
```
Use ops-suite:service-status with arguments: {service} {env_name}.
Use session state from /tmp/ops-suite-session/ — do not re-ask for environment.
```

**Destructive skills** (`disable-model-invocation: true`) must be suggested, never auto-invoked:
```
Next steps:
  → Run `/ops-suite:db-migrate {env_name}` to apply pending migrations.
```

Chain depth is capped at 3.

## Safety classification

| Skill | Type |
|-------|------|
| service-status, service-logs, db-query, queue-status, port-forward | read-only — auto-chainable |
| deploy, db-migrate, queue-reprocess | destructive — suggest only, always ask for explicit confirmation |

## Adding a new skill

1. Run `/creating-skills:creating-skills` — it guides the full authoring process
2. Create `plugins/<plugin>/skills/<name>/SKILL.md` with the standard frontmatter
3. Add adapters under `adapters/` for each supported technology
4. Add a command shim at `plugins/<plugin>/commands/<name>.md`
5. Test: trigger test (natural language), functional test (`/skill-name`), performance test (SKILL.md < 500 lines)
