# scaffold-skill — Design

**Date:** 2026-04-21
**Status:** Implemented
**Location:** `plugins/creating-skills/skills/scaffold-skill/`

## Problem

The `creating-skills` plugin teaches skill authoring but requires the user to create all files manually. Every new skill needs the same directory structure, frontmatter fields, and boilerplate steps — work that is repetitive and error-prone.

## Solution

A new skill, `scaffold-skill`, that:
1. Asks two intake questions (plugin + name, and a natural language description)
2. Infers all SKILL.md decisions from the description
3. Confirms a summary card before writing
4. Generates only the files and folders that make sense for that skill type

## Design decisions

### A: New skill vs enhance existing
New skill in `creating-skills` — keeps single responsibility (guide vs scaffold).

### B: Discovers plugins dynamically
Reads `${CLAUDE_PLUGIN_ROOT}/../` to list available plugins. No hardcoded plugin names.

### C: Hybrid intake
Two questions → infer → confirm. Minimizes friction while allowing correction.

## Inference rules

| Indicator in description | Decision |
|---|---|
| "deploy", "send", "run migration", "reprocess", "delete", "publish" | `disable-model-invocation: true` |
| "kubernetes", "docker", "jira", "figma", "rabbitmq", "postgresql" | `adapters/` folder |
| "complex output", "template", "detailed report", "format" | `references/` folder |
| "analyze", "diagnose", "cross-reference", "evaluate", "triage" | `model: sonnet` |
| "list", "check", "status", "count", "show" | `model: haiku` |
| "bash", "commands", "run", "execute", "kubectl" | `allowed-tools: Bash` |
| "search codebase", "grep", "find files", "read" | `allowed-tools: Read, Grep, Glob` |
| "create files", "write", "scaffold", "generate" | `allowed-tools: Write` |

## Files generated

| File | Condition |
|---|---|
| `skills/{name}/SKILL.md` | Always |
| `commands/{name}.md` | Always |
| `skills/{name}/adapters/example.md` | If needs_adapters |
| `skills/{name}/references/` | If needs_references |

## Confirmation card format

```
Skill a crear: {plugin}/skills/{name}/
  model:                    haiku | sonnet
  disable-model-invocation: true | false
  adapters/:                sí | no
  references/:              sí | no
  allowed-tools:            [Bash, Read, ...]
  argument-hint:            "[hint]"

TRIGGER phrases inferidas:
  - "..."

¿Ajustar algo antes de generar? (sí / no / [campo: nuevo valor])
```
