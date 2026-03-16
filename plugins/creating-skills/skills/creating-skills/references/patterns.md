# Skill Patterns & Troubleshooting

Source: "The Complete Guide to Building Skills for Claude" (Anthropic, 2025)

## The 5 Reusable Patterns

### 1. Sequential Workflow Orchestration

Multi-step processes with clear phases where each step depends on the previous.

**When to use:** Build/deploy pipelines, document creation with review, data processing workflows.

**Structure:**
```markdown
## Workflow
1. [Phase 1] — Gather inputs, validate prerequisites
2. [Phase 2] — Execute main operation
3. [Phase 3] — Verify results, report status

## Phase transitions
- Only proceed to Phase 2 if Phase 1 validation passes
- If Phase 3 fails, retry Phase 2 with adjusted parameters
```

**Key:** Define clear phase transitions and failure handling between steps.

---

### 2. Multi-MCP Coordination

Combining multiple tools/services in a single skill.

**When to use:** Research + writing + publishing, data from one source transformed and sent to another, cross-platform workflows.

**Structure:**
```markdown
## Tools Required
- [MCP Server A] for [purpose]
- [MCP Server B] for [purpose]

## Coordination
1. Fetch data from Server A
2. Transform/analyze the data
3. Push results to Server B
```

**Key:** Document which MCP servers are needed and how data flows between them.

---

### 3. Iterative Refinement

Feedback loops where output is evaluated and improved across cycles.

**When to use:** Code review cycles, content editing, quality improvement, test-fix-verify loops.

**Structure:**
```markdown
## Refinement Loop
1. Generate initial output
2. Evaluate against [criteria]
3. If criteria not met:
   - Identify specific gaps
   - Apply targeted fixes
   - Return to step 2
4. Maximum [N] iterations before escalating
```

**Key:** Define evaluation criteria, maximum iterations, and escalation conditions.

---

### 4. Context-Aware Tool Selection

Choosing the right tool or approach based on the current situation.

**When to use:** When multiple tools could solve a problem, environment-dependent workflows, adaptive behavior based on project state.

**Structure:**
```markdown
## Decision Matrix
- If [condition A]: use [tool/approach 1]
- If [condition B]: use [tool/approach 2]
- Default: use [fallback approach]

## Detection
Check [specific signals] to determine which condition applies.
```

**Key:** Define clear conditions and signals for each decision path. Avoid ambiguous overlap.

---

### 5. Domain-Specific Intelligence

Specialized knowledge for a specific field that Claude doesn't have by default.

**When to use:** Industry terminology, company-specific conventions, regulatory requirements, proprietary frameworks.

**Structure:**
```markdown
## Domain Knowledge
[Key concepts, terminology, rules specific to this domain]

## Application Rules
- When you see [domain term], it means [specific meaning]
- [Domain process] requires [specific steps]
- Common mistakes: [list domain-specific pitfalls]
```

**Key:** Only include knowledge Claude doesn't already have. Don't re-explain general programming concepts.

---

## Troubleshooting

### Skill Doesn't Trigger Automatically

| Symptom | Cause | Fix |
|---------|-------|-----|
| Claude never activates the skill | Description too vague | Add "Use when..." + specific trigger phrases with natural keywords |
| Claude activates wrong skill | Description overlaps with another | Make descriptions more distinct, add negative conditions |
| Skill excluded from context | Description budget exceeded | Run `/context` to check; shorten descriptions across all skills |

### Skill Triggers Too Often

| Symptom | Cause | Fix |
|---------|-------|-----|
| Activates on unrelated requests | Description too broad | Narrow trigger conditions, add specificity |
| Should be manual-only | Missing invocation control | Add `disable-model-invocation: true` |

### Skill Doesn't Work Correctly

| Symptom | Cause | Fix |
|---------|-------|-----|
| Claude ignores instructions | SKILL.md too long | Cut to <500 lines, move detail to references |
| Claude hallucinates steps | Instructions ambiguous | Increase specificity (lower degrees of freedom) |
| Claude can't find referenced files | Wrong path | Use relative paths from SKILL.md: `references/file.md` |
| Subagent has no context | `context: fork` on guidelines-only skill | Remove `context: fork` or add explicit task instructions |

### Performance Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Slow skill execution | Too much content loaded upfront | Move detail to references (progressive disclosure) |
| Takes too many steps | Instructions unclear | Add explicit step-by-step structure |
| Context window fills up | Skill + references too large | Compress content, remove redundancy |

### Testing Commands

```bash
# Check if skill is discovered
# In Claude Code, ask: "What skills are available?"

# Check context budget
# Run: /context

# Test triggering (don't use /slash-command)
# Ask naturally: "help me build a skill for X"

# Test direct invocation
# Run: /creating-skills
```
