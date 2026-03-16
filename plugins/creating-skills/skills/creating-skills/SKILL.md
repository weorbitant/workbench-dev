---
name: creating-skills
description: Use when creating new skills, editing existing skills, or reviewing skill quality. Use when user mentions building, writing, or improving a SKILL.md file or skill folder. Guides skill authoring following Anthropic's official best practices.
model: sonnet
---

# Creating Skills

Skills are instruction folders that teach Claude specialized workflows. The core principle is **progressive disclosure**: minimize tokens while maintaining expertise.

## Skill Structure

```
skill-name/
├── SKILL.md           # Required. Frontmatter + instructions
├── references/        # Optional. Deep documentation (loaded on-demand)
├── scripts/           # Optional. Executable code
└── assets/            # Optional. Templates, icons
```

## SKILL.md Template

```yaml
---
name: kebab-case-name
description: Use when [trigger conditions]. [What it does]. [When to apply it].
---

# Skill Title

## Overview
One paragraph: what this skill does and the core principle.

## Instructions
Step-by-step guidance or reference content.

## References
- Link to [references/detail.md](references/detail.md) for deep content
```

## Writing the Description

The `description` field is the most critical part. It's always loaded in Claude's system prompt and determines auto-invocation.

**Rules:**
- Start with "Use when..." followed by trigger conditions
- Include natural keywords users would say
- Keep under 1024 characters
- Be specific about what AND when

**Good:**
```yaml
description: Use when creating new skills, editing existing skills, or reviewing skill quality. Use when user mentions building, writing, or improving a SKILL.md file.
```

**Bad:**
```yaml
description: Helps with skills
```

## Content Guidelines

### Be Concise
The context window is shared. Claude is already smart — only add domain-specific knowledge it doesn't have. Keep SKILL.md body under 500 lines.

### Match Degrees of Freedom to Task

| Freedom | When | Format |
|---------|------|--------|
| **High** | Multiple valid approaches, creative work | Text guidelines |
| **Medium** | Preferred pattern exists, some variation OK | Pseudocode with params |
| **Low** | One correct approach, variations cause failure | Exact code/commands |

### Use Consistent Terminology
Pick one term per concept. Don't alternate between "skill", "command", and "instruction" — use "skill" throughout.

### Progressive Disclosure (3 Levels)
1. **Frontmatter** — Always loaded. Just enough for Claude to know when to use it
2. **SKILL.md body** — Loaded when skill is invoked. Full instructions
3. **Referenced files** — Loaded on-demand. Deep documentation, examples, APIs

## Frontmatter Reference

| Field | Default | Purpose |
|-------|---------|---------|
| `name` | Directory name | Display name, becomes `/slash-command`. Kebab-case, max 64 chars |
| `description` | First paragraph | When to use. Claude uses this for auto-invocation |
| `argument-hint` | — | Autocomplete hint: `[issue-number]`, `[filename]` |
| `disable-model-invocation` | `false` | `true` = manual-only (deploy, commit, dangerous ops) |
| `user-invocable` | `true` | `false` = hidden from `/` menu (background knowledge) |
| `allowed-tools` | — | Tool restrictions: `Read, Grep, Bash(gh *)` |
| `model` | — | Override model for this skill |
| `context` | — | `fork` = run in isolated subagent |
| `agent` | `general-purpose` | Subagent type when `context: fork` |

## Skill Types

**Reference skills** — Add knowledge Claude applies to current work (conventions, patterns, domain knowledge). Run inline with conversation context.

**Task skills** — Step-by-step instructions for specific actions. Often use `disable-model-invocation: true` and `context: fork`.

## String Substitutions

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed to the skill |
| `$ARGUMENTS[N]` or `$N` | Specific argument by index (0-based) |
| `${CLAUDE_SESSION_ID}` | Current session ID |

## Distribution

| Level | Path | Scope |
|-------|------|-------|
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where plugin enabled |

Priority: Enterprise > Personal > Project > Plugin.

## Testing Checklist

Run these three test types before considering a skill complete:

### 1. Triggering Test
- Ask Claude something that should activate the skill (without `/invoking` it)
- Verify the description keywords match natural language triggers
- Test phrases that should NOT trigger it

### 2. Functional Test
- Invoke with `/skill-name` directly
- Verify Claude follows instructions correctly
- Test with and without arguments
- Check edge cases

### 3. Performance Test
- Is SKILL.md under 500 lines?
- Does Claude complete tasks in reasonable steps?
- Are referenced files loaded only when needed?

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Description too vague | Add "Use when..." + specific trigger phrases |
| SKILL.md too long (>500 lines) | Move detail to `references/` |
| Over-explaining basics Claude knows | Remove — Claude knows markdown, YAML, git, etc. |
| Inconsistent terminology | Pick one term per concept |
| No testing before deployment | Run all 3 test types |
| Missing `disable-model-invocation` on dangerous ops | Add it for deploy, commit, send-message skills |

## References

- [Anthropic Official Guide](references/anthropic-guide.md) — Condensed content from the 32-page PDF
- [Patterns & Troubleshooting](references/patterns.md) — 5 reusable patterns + debugging
