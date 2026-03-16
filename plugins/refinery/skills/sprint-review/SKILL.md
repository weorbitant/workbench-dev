---
name: sprint-review
description: "Use when evaluating a sprint before starting it. Use when user says 'sprint review', 'review sprint', 'evaluar sprint', 'sprint planning review', or mentions checking sprint readiness."
argument-hint: "[BOARD-ID or TICKET-KEYS or empty]"
allowed-tools:
  - Agent
  - AskUserQuestion
  - ToolSearch
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `issue_tracker` — determines which adapter to load
- `sprint_review.oversized_threshold` — story points above this are flagged
- `sprint_review.systemic_threshold` — percentage (0-1) above which findings become systemic
- `sprint_review.bug_alert_threshold` — percentage of bugs that triggers a warning
- `sprint_review.vague_terms_es` — list of vague terms in Spanish
- `sprint_review.vague_terms_en` — list of vague terms in English
- `communication` — tool and channels for sending reports

Issue tracker-specific config (e.g., `jira.story_points_field`, `jira.default_project`).

## Step 1 — Load adapter

Read the adapter file at `${CLAUDE_PLUGIN_ROOT}/skills/sprint-review/adapters/{issue_tracker}.md`.
If the adapter does not exist, tell the user that `{issue_tracker}` is not yet supported and stop.

All tool-specific calls come from the adapter. Do not invent tool calls.

**IMPORTANT:** Instructions are in English, but all output MUST be in Spanish.

## Phase 1 — Get sprint tickets

Determine the source of tickets:

1. **Board ID provided** — Use the adapter's "get sprint from board" command to find the next/active sprint, then fetch all sprint tickets.
2. **Ticket keys provided** — Use the adapter's "fetch ticket" command for each key.
3. **Nothing provided** — Ask the user for a board ID or list of ticket keys.

Store all tickets as `{tickets}`.

## Phase 1.5 — Filter tickets

Remove from the analysis:
- Tickets with status "Done", "Closed", or equivalent
- Sub-tasks (they are analyzed as part of their parent)

Store the filtered list as `{active_tickets}`. Report how many were filtered and why.

## Phase 2 — Run checks

For each ticket in `{active_tickets}`, run these 8 checks. Use Agent to parallelize when possible.

### Check 1: Duplicates
Compare all ticket summaries and descriptions. Flag pairs with >70% similarity in title or identical acceptance criteria.

### Check 2: Definition quality
For each ticket, evaluate:
- Has a description (non-empty, >50 chars)
- Has acceptance criteria (explicit section or checklist)
- AC are testable (not vague)
- Has a clear scope boundary (what is NOT included)

Score: 0 (no definition) to 3 (fully defined).

### Check 3: Estimation
For each ticket, check if story points are set (using the adapter's story points field).
- Missing estimation → flag
- Estimation of 0 → flag as suspicious

### Check 4: Vague language
Scan title, description, and AC for terms from `{config.sprint_review.vague_terms_es}` and `{config.sprint_review.vague_terms_en}`.
Report each match with the exact term and location.

### Check 5: Dependencies
Check for:
- Linked issues (blocks/is-blocked-by)
- Mentions of other tickets in description (pattern: `[A-Z]+-\d+`)
- Mentions of external teams or services without linked tickets
- Blocked tickets that are included in the sprint

### Check 6: Balance
Calculate:
- Total tickets by type (Story, Bug, Task, Spike)
- Percentage of bugs = bug_count / total_count
- If bug percentage > `{config.sprint_review.bug_alert_threshold}` → flag

### Check 7: Oversized tickets
Flag tickets with story points > `{config.sprint_review.oversized_threshold}`.
Suggest splitting oversized tickets.

### Check 8: Unassigned
Flag tickets without an assignee.

## Phase 2.5 — Classify systemic issues

For each check, calculate the percentage of tickets that failed:
- `fail_rate = failed_tickets / total_active_tickets`

If `fail_rate > {config.sprint_review.systemic_threshold}` for any check, classify it as a **systemic issue** that needs process-level attention, not just ticket-level fixes.

## Phase 3 — Build report

Read the output format at [references/output-format.md](references/output-format.md).

Build the report using that format. All text in the report MUST be in Spanish.

Include:
1. Sprint summary (total tickets, total points, by type, by assignee)
2. Per-check results with affected tickets
3. Systemic issues section (if any)
4. Overall readiness score: ✅ Ready | ⚠️ Needs work | 🚫 Not ready

## Phase 4 — Offer actions

Ask the user which action to take:

1. **Send to team channel** — If `{config.communication.tool}` is configured, offer to send a summary to the configured channel. Format the message using [references/output-format-slack.md](references/output-format-slack.md) if sending to Slack.
2. **Comment on tickets** — For each ticket with findings, post a comment with the specific issues found using the adapter's comment command.
3. **Export as text** — Display the full report for copying.
4. **Re-analyze** — Re-run with updated context.
