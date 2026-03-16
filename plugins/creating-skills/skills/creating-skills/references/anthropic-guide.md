# Anthropic Official Guide — Condensed Reference

Source: "The Complete Guide to Building Skills for Claude" (32-page PDF, Anthropic 2025)

## Fundamentals

### What is a Skill?
A set of instructions — packaged as a folder — that teaches Claude how to handle specific tasks or workflows. Skills are the knowledge layer ("how Claude should do it"), while MCP is the connectivity layer ("what Claude can access").

### Three Core Principles

**Progressive Disclosure** — Token efficiency through 3 levels:
1. Frontmatter (always loaded): just enough for Claude to know when to use the skill
2. SKILL.md body (loaded when relevant): full instructions
3. Referenced files (loaded on-demand): deep documentation

**Composability** — Claude loads multiple skills simultaneously. Your skill must work alongside others. Don't assume it's the only capability available.

**Portability** — Skills work across Claude.ai, Claude Code, and API. Create once, works everywhere.

### The Context Window is a Public Good
Your skill shares context with: system prompt, conversation history, other skills' metadata, and the user's request. Every token competes for space. Default assumption: Claude is already smart — only add what's specific to your domain.

## Planning & Design

### Before Writing a Skill, Define:
1. **Use cases** — What specific problems does this skill solve?
2. **Success criteria** — How will you know it works?
3. **Technical requirements** — What tools/MCP servers does it need?
4. **Trigger conditions** — When should Claude activate it?
5. **Degrees of freedom** — How much flexibility should Claude have?

### Degrees of Freedom Spectrum

**High freedom** (guidelines, heuristics):
- Creative tasks, multiple valid approaches
- Context-dependent decisions
- Example: "When writing tests, prefer integration tests for API endpoints"

**Medium freedom** (pseudocode with parameters):
- A preferred pattern exists but variation is acceptable
- Configuration affects behavior
- Example: "Use this template but adapt the error handling to the framework"

**Low freedom** (exact code/commands):
- One correct approach, variations cause failure
- Deterministic decisions
- Example: "Run exactly: `npm run build && npm run deploy`"

## Writing Effective Skills

### The Description Field
The most important part of any skill. It's:
- Always loaded in Claude's system prompt
- The only thing always visible
- What determines whether Claude uses your skill

**Best practices:**
- Start with "Use when..." + trigger conditions
- Include natural keywords users would say
- Keep under 1024 characters
- Be specific about what AND when
- Write in third person

### SKILL.md Body Best Practices
- Under 500 lines
- Use headers for scannable structure
- Put the most important info first
- Link to references for depth — don't inline everything
- Use consistent terminology throughout
- Don't explain things Claude already knows (markdown, YAML, common tools)

### Reference Files
- Use `references/` subdirectory
- Claude loads them on-demand only
- Keep naming clear and descriptive
- Link from SKILL.md with relative paths: `[detail](references/detail.md)`
- One level deep — don't nest references within references

## Testing & Iteration

### Red-Green-Refactor for Skills
1. **Build evaluations first** — Define what success looks like before writing
2. **Run tests → watch them fail (RED)** — Verify your tests catch missing behavior
3. **Write/update skill content (GREEN)** — Make tests pass
4. **Iterate and refactor (REFACTOR)** — Tighten, compress, improve

### Three Test Types

**Triggering tests:**
- Does Claude recognize when to use the skill?
- Test with phrases that should trigger it
- Test with phrases that should NOT trigger it
- Verify description keywords match natural language

**Functional tests:**
- Does Claude follow instructions correctly?
- Test primary workflows end-to-end
- Test with and without arguments
- Verify edge cases are handled
- Check output format and quality

**Performance tests:**
- Does the skill execute efficiently?
- Is SKILL.md appropriately sized?
- Does Claude complete tasks in reasonable steps?
- Are references loaded only when needed?

### The Skill Creator
Anthropic provides an official skill-creator tool. Use it as a starting point but always customize the output.

## Distribution & Sharing

### Skill Locations (Priority Order)
1. **Enterprise** (managed settings) — All users in org (highest priority)
2. **Personal** (`~/.claude/skills/`) — All your projects
3. **Project** (`.claude/skills/`) — This project only
4. **Plugin** (`<plugin>/skills/`) — Where plugin is enabled (namespaced)

When skills share names, higher-priority locations win. Plugin skills use `plugin-name:skill-name` namespace.

### Automatic Discovery
When editing files in subdirectories, Claude Code discovers skills from nested `.claude/skills/` directories. Supports monorepo setups.

### Discoverability Budget
- Skill descriptions: always loaded (2% of context window, fallback: 16,000 chars)
- Full skill content: only when invoked
- Check with `/context` if skills are being excluded

## Advanced Features

### Dynamic Context Injection
The `!`command`` syntax runs shell commands before skill content is sent to Claude:
```markdown
Current branch: !`git branch --show-current`
Recent changes: !`git log --oneline -5`
```
This is preprocessing — Claude only sees the output.

### Subagent Isolation
`context: fork` runs the skill in an isolated subagent with no conversation history. Use for complex tasks with explicit instructions. Warning: doesn't work for guidelines-only skills (no actionable prompt).

### Tool Restrictions
`allowed-tools` limits what Claude can do:
```yaml
allowed-tools: Read, Grep, Glob          # Read-only
allowed-tools: Bash(python *)            # Only python commands
```

### Invocation Control

| Config | User invokes | Claude invokes |
|--------|---|---|
| Default | Yes | Yes |
| `disable-model-invocation: true` | Yes | No |
| `user-invocable: false` | No | Yes |

Use `disable-model-invocation: true` for side-effect workflows (deploy, commit, send).
Use `user-invocable: false` for background knowledge.

## Complete YAML Frontmatter Reference

```yaml
---
name: string              # Kebab-case, max 64 chars. Default: directory name
description: string       # <1024 chars. Default: first paragraph of body
argument-hint: string     # Autocomplete hint: "[issue-number]"
disable-model-invocation: boolean  # Default: false
user-invocable: boolean   # Default: true
allowed-tools: string     # Comma-separated: "Read, Grep, Bash(gh *)"
model: string             # Override model
context: string           # "fork" for isolated subagent
agent: string             # Subagent type. Default: "general-purpose"
hooks: object             # Hooks scoped to skill lifecycle
---
```

## Quick Checklist

- [ ] Clear use case defined
- [ ] Trigger phrases identified
- [ ] Description: concise, <1024 chars, starts with "Use when..."
- [ ] SKILL.md body: <500 lines, progressive disclosure
- [ ] Consistent terminology throughout
- [ ] Degrees of freedom match task fragility
- [ ] References linked (not inlined) for deep content
- [ ] Triggering tests pass
- [ ] Functional tests pass
- [ ] Performance tests pass
- [ ] Distribution location chosen (personal/project/plugin)
