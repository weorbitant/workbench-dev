---
name: adr
description: "Use when creating, updating, or compacting Architecture Decision Records. Use when user says 'adr', 'create ADR', 'record decision', 'registrar decisión', 'decision record', or needs to document a technical decision."
argument-hint: "[topic or existing ADR path]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Agent
  - AskUserQuestion
  - ToolSearch
  - Edit
  - Write
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, this skill can still operate. Log a warning but continue.

Check `docs_sources` — if configured, search existing documentation for related decisions before creating a new ADR.

## Step 1 — Determine action

From `$ARGUMENTS` and conversation context, determine the action:

1. **Create** — `$ARGUMENTS` is a topic/title for a new ADR
2. **Update** — `$ARGUMENTS` is a path to an existing ADR file
3. **Compact** — user explicitly asks to compact/consolidate multiple ADRs
4. **List** — user asks to see existing ADRs

If unclear, ask the user.

## Step 2 — Detect language

Detect the language of the conversation:
- If the user writes in Spanish → use [references/template-es.md](references/template-es.md)
- If the user writes in English → use [references/template-en.md](references/template-en.md)
- If unclear, ask the user

## Step 3 — Scan existing ADRs

Search for existing ADRs in the project:
```
Glob: docs/adr/*.md, doc/adr/*.md, adr/*.md, docs/decisions/*.md
```

If ADRs exist:
- List them with titles and dates
- Check if any are related to the current topic (Grep for keywords)
- If a related ADR exists, ask if the user wants to update it or create a new one that supersedes it

## Step 4 — Gather context (for Create)

If creating a new ADR, gather:

1. **Context** — What is the situation that requires a decision?
2. **Problem** — What specific problem are we solving?
3. **Options considered** — What alternatives were evaluated?
4. **Decision** — What was decided and why?
5. **Consequences** — What are the positive and negative impacts?

For each option, assess:
- Pros and cons
- Impact on existing architecture
- Implementation effort
- Risk level

If the user has already done a feasibility analysis (using `analyze-feasibility`), incorporate those findings.

## Step 5 — Search documentation (optional)

If `{config.docs_sources}` is configured:
- Search for related documentation that supports or informs the decision
- Include references to relevant docs in the ADR

## Step 6 — Generate ADR

Load the appropriate language template from references/.

Fill in all sections of the template. Ensure:
- The title is descriptive and unique
- The date is today's date
- The status is "Accepted" (or "Proposed" if the user wants review first)
- All options are fairly represented
- Consequences are honest (include negatives)

## Step 7 — Determine file path

ADR files go in: `docs/adr/YYYY-MM-DD-<slug>.md`

Where:
- `YYYY-MM-DD` is today's date
- `<slug>` is the kebab-case version of the title

If the `docs/adr/` directory does not exist, create it.

Check for existing ADRs with sequential numbering:
```
Glob: docs/adr/*.md
```
If existing ADRs use a numbered prefix (e.g., `001-`, `002-`), follow that convention.

## Step 8 — Write or update

- **Create** — Write the new ADR file
- **Update** — Edit the existing ADR, adding a new section "## Update — {date}" with the changes and rationale
- **Compact** — Read all related ADRs, create a new consolidated ADR that supersedes them, mark old ones as "Superseded by {new ADR}"

## Step 9 — Post-creation

After writing the file:
1. Display the full ADR content
2. Show the file path
3. Ask if the user wants to:
   - **Adjust** — modify any section
   - **Mark as Proposed** — if it needs team review
   - **Link to ticket** — if there is a related ticket, add a comment linking to the ADR
   - **Commit** — stage and commit the ADR file
