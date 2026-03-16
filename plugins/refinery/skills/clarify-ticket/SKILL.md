---
name: clarify-ticket
description: "Use when analyzing a ticket for ambiguities, missing information, or unclear acceptance criteria. Use when user says 'clarify ticket', 'review ticket', 'analyze ticket', or passes a ticket key."
argument-hint: "[TICKET-KEY or URL]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - ToolSearch
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `issue_tracker` — determines which adapter to load (jira, linear, github-issues)

## Step 1 — Load adapter

Read the adapter file at `${CLAUDE_PLUGIN_ROOT}/skills/clarify-ticket/adapters/{issue_tracker}.md`.
If the adapter does not exist, tell the user that `{issue_tracker}` is not yet supported and stop.

All tool-specific calls come from the adapter. Do not invent tool calls.

## Step 2 — Parse argument

From `$ARGUMENTS`, extract the ticket key or URL:

1. If the argument is a URL, use the adapter's URL-parsing rule to extract the ticket key.
2. If the argument is a key (e.g. `PROJ-123`), use it directly.
3. If no argument was provided, ask the user for a ticket key.

Store the result as `{key}`.

## Step 3 — Fetch ticket

Use the adapter's **fetch ticket** command to retrieve the full ticket for `{key}`.

Extract and store:
- `title` — the ticket summary
- `description` — the full body/description
- `acceptance_criteria` — if present in the description (look for "Criterios de aceptación", "Acceptance Criteria", "AC", or checklist sections)
- `status` — current status
- `type` — story, bug, task, sub-task, etc.
- `assignee` — who it is assigned to
- `labels` — any labels or tags
- `linked_issues` — any linked tickets (blocks, is blocked by, relates to)
- `comments` — all comments on the ticket

## Step 4 — Detect open questions

Scan the description, acceptance criteria, and comments for:

1. **Explicit questions** — sentences ending in `?` or starting with "Pregunta:", "Question:", "Duda:", "TBD", "Por definir"
2. **Conditional language** — "debería", "quizás", "posiblemente", "should", "maybe", "possibly", "could be", "se podría"
3. **Undefined references** — mentions of external documents, designs, or specs without links
4. **Ambiguous pronouns** — "esto", "eso", "aquello", "this", "that" without clear antecedents
5. **Missing quantities or boundaries** — "varios", "algunos", "many", "some", "etc.", "appropriate"

## Step 5 — Analyze content

For each finding from Step 4, classify it:

- **BLOCKER** — Cannot start implementation without this answer. Examples: undefined business rules, missing API contract, unclear data model, no design link.
- **NICE-TO-HAVE** — Implementation can proceed but the answer would improve quality. Examples: edge case clarification, UX preference, performance target.

## Step 6 — Check comments

Review all comments chronologically. Identify:
- Questions that were asked but never answered
- Answers that contradict the description
- Decisions made in comments that should be in the description
- Newer context that updates or overrides original requirements

## Step 7 — Structural validations

Check the ticket for structural completeness:

1. **Description present and non-empty** — flag if missing or too short (< 50 chars)
2. **Acceptance criteria present** — flag if missing entirely
3. **AC are testable** — each criterion should be verifiable (not vague like "should work well")
4. **Design link present** — if the ticket references UI work, a design link should exist
5. **Dependencies documented** — if the ticket mentions other services or teams, linked issues should exist
6. **Estimation present** — flag if story points or estimate is missing
7. **Assignee present** — flag if unassigned
8. **Type appropriate** — flag if type does not match content (e.g., story without user-facing value, bug without reproduction steps)

## Step 8 — Classify by audience

Group all findings by who can answer them:

- **Product / PO** — business rules, priorities, scope decisions
- **Design / UX** — visual behavior, states, interactions
- **Tech Lead / Architecture** — technical approach, data model, integrations
- **QA** — test scenarios, edge cases, environments
- **DevOps / Infra** — deployment, infrastructure, environments
- **Other team** — cross-team dependencies

## Step 9 — Reformulate business blockers

For each BLOCKER finding, reformulate it as a clear, actionable question:

- Bad: "The description is vague about validation"
- Good: "What specific validation rules apply to the email field? (e.g., format, uniqueness, domain restriction)"

Each question must:
1. State what is unclear
2. Suggest possible answers or options when possible
3. Reference the specific part of the ticket that triggered it

## Step 10 — Display results

Read the format reference at [references/actions-and-format.md](references/actions-and-format.md).

Present the analysis using the format defined in the reference file.

Structure:
1. **Header** — ticket key, title, status, type
2. **Summary** — one-paragraph assessment (healthy, needs minor clarification, has blockers)
3. **Blockers** — numbered list with audience tag
4. **Nice-to-have** — numbered list with audience tag
5. **Structural issues** — checklist of what passed and what failed
6. **Unanswered questions from comments** — if any
7. **Contradictions** — if any found between description and comments

## Step 11 — Offer actions

Ask the user which action to take:

1. **Add as comment** — post the analysis as a comment on the ticket using the adapter's comment command
2. **Edit ticket** — update the ticket description to include the identified gaps using the adapter's edit command
3. **Copy to clipboard** — just display, no action
4. **Refine and re-analyze** — let the user provide additional context, then re-run from Step 4
