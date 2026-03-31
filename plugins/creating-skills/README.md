# creating-skills

A meta-skill that guides you through authoring Claude Code skills following Anthropic best practices.

## When to use

- You want to create a new skill for your team or project
- You want to understand how skills work (progressive disclosure, triggers, adapters)
- You want to improve an existing skill's structure

## Usage

```
/creating-skills:creating-skills
```

Claude walks you through the entire process interactively.

## What it covers

### Skill types

| Type | Purpose | Example |
|------|---------|---------|
| **Reference** | Add knowledge Claude can use | "How to configure our CI pipeline" |
| **Task** | Step-by-step instructions Claude follows | "Deploy to staging" |

### Progressive disclosure

Skills load in three tiers to minimize context usage:

```
Tier 1 — Frontmatter (always loaded)
  name, description, allowed-tools → Claude decides if skill is relevant

Tier 2 — SKILL.md body (loaded on invoke)
  Step-by-step instructions → Claude follows the workflow

Tier 3 — references/*.md + adapters/*.md (loaded on demand)
  Deep docs, templates, technology commands → loaded only when needed
```

### Trigger-based invocation

Skills can auto-invoke when Claude detects matching context:

```yaml
# In SKILL.md frontmatter
description: |
  TRIGGER when: user asks about database migration status
  DO NOT TRIGGER when: user is writing migration code
```

### Config + adapter pattern

For technology-agnostic skills:

```
skills/my-skill/
├── SKILL.md              ← reads config, loads right adapter
├── adapters/
│   ├── kubernetes.md     ← kubectl commands
│   ├── docker-compose.md ← docker compose commands
│   └── ecs.md            ← aws ecs commands
└── references/
    └── patterns.md       ← shared knowledge
```

### Distribution levels

| Level | Location | Scope |
|-------|----------|-------|
| Personal | `~/.claude/skills/` | All your projects |
| Project | `.claude/skills/` | This repo only |
| Plugin | `plugins/<name>/skills/` | Where plugin is installed |

## Learn more

- [Anthropic docs on skills](https://docs.anthropic.com/en/docs/claude-code/skills)
- [ops-suite skills](../ops-suite/skills/) — Real examples of the config + adapter pattern
- [refinery skills](../refinery/skills/) — Real examples of multi-agent orchestration

## License

MIT
