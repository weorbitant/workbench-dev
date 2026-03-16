---
name: analyze-docs
description: "Use when searching documentation about a concept across platforms. Use when user says 'search docs', 'buscar documentación', 'analyze docs', 'find documentation', or needs to understand existing documentation about a topic."
argument-hint: "[search term or URL]"
allowed-tools:
  - Read
  - AskUserQuestion
  - ToolSearch
model: sonnet
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `docs_sources` — array of documentation sources (each with `type` and optional `cloud_id`)

If `docs_sources` is empty or not defined, tell the user no documentation sources are configured and stop.

## Step 1 — Load adapters

For each source in `{config.docs_sources}`:
- Read the adapter at `${CLAUDE_PLUGIN_ROOT}/skills/analyze-docs/adapters/{source.type}.md`
- If the adapter does not exist, warn the user and skip that source

Store all loaded adapters and their associated source configs.

## Step 2 — Parse argument

From `$ARGUMENTS`:
1. If the argument is a URL, identify which source it belongs to and fetch that specific page.
2. If the argument is a search term, search across all configured sources.
3. If no argument provided, ask the user what to search for.

## Step 3 — Search across sources

For each configured documentation source, use the adapter's **search** command to find relevant pages.

Search strategy:
1. Exact term match first
2. Related terms (synonyms, translations if applicable)
3. Broader category if no results

Collect the top 5 results per source.

## Step 4 — Fetch and extract content

For each relevant page found:
1. Fetch the full page content using the adapter's **fetch** command
2. Extract information WITHOUT interpreting it — use direct quotes
3. Note the page title, URL, and last modified date

**Critical rule:** Extract only what the documentation explicitly states. Do not infer, summarize, or add context that is not in the source.

## Step 5 — Identify business rules

From the extracted content, identify explicit business rules:
- Validation rules ("X must be...", "X cannot exceed...")
- Process rules ("When X happens, Y must...")
- Constraint rules ("Only users with role X can...")
- Data rules ("Field X is calculated as...")

For each rule, record:
- The exact quote
- The source page
- Confidence level (explicitly stated vs. implied)

## Step 6 — Detect contradictions

Compare information across sources. Flag:
- Different definitions of the same term
- Conflicting rules or processes
- Outdated information (older source contradicts newer)
- Missing information in one source that another covers

## Step 7 — Assess coverage

For each aspect of the search topic, assess documentation coverage:

| Aspecto | Fuente 1 | Fuente 2 | ... | Cobertura |
|---------|----------|----------|-----|-----------|
| {aspect} | ✅ Documented | ❌ Not found | ... | {partial/full/none} |

## Step 8 — Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 DOCUMENTATION ANALYSIS: "{search_term}"
   Sources: {count} | Pages found: {total}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━ SOURCE: {source_name} ({source_type}) ━━━━━━

📄 {page_title}
   URL: {url}
   Updated: {date}

   Relevant content:
   > "{direct quote 1}"
   > "{direct quote 2}"

📄 {page_title_2}
   ...

━━ BUSINESS RULES FOUND ━━━━━━━━━━━━━━━━━━━━━━

1. "{exact rule}" — Source: {page_title} ({source})
2. "{exact rule}" — Source: {page_title} ({source})

━━ CONTRADICTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ {source_a}/{page_a} says: "{X}"
   {source_b}/{page_b} says: "{Y}"
   → Needs clarification from: {audience}

━━ COVERAGE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{coverage table from Step 7}

━━ NOT DOCUMENTED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The following aspects were NOT found in any source:
- {missing_aspect_1}
- {missing_aspect_2}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
