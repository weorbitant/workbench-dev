---
name: notify-team
description: "Use when sending communication to the team. Use when user says 'notify team', 'notifica al equipo', 'send message', 'draft a message', 'enviar mensaje', or needs to communicate with the team."
argument-hint: "[channel|person] [description]"
allowed-tools:
  - Read
  - AskUserQuestion
  - ToolSearch
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `communication.tool` — slack, teams, discord, or none
- `communication.channels` — map of channel aliases to {id, name}

If `communication.tool` is "none", tell the user no communication tool is configured and stop.

## Step 1 — Load adapter

Read the adapter file at `${CLAUDE_PLUGIN_ROOT}/skills/notify-team/adapters/{communication.tool}.md`.
If the adapter does not exist, tell the user that `{communication.tool}` is not yet supported and stop.

## Step 2 — Determine destination

From `$ARGUMENTS`, extract the target channel or person:

1. Check if the argument matches a key in `{config.communication.channels}` (e.g., "general", "alerts-dlq")
2. If matched, use the channel's `{id}` and `{name}` from config
3. If not matched, use the adapter's search command to find the channel/person
4. If no destination provided, list configured channels and ask the user

Store: `{destination_id}`, `{destination_name}`

## Step 3 — Determine message type

Classify the message based on the description and conversation context:

| Type | Indicators | Tone |
|------|-----------|------|
| `incident` | outage, error, down, urgente, incidente | Urgent, factual, action-oriented |
| `announcement` | release, deployment, change, anuncio | Informative, clear, structured |
| `question` | question, pregunta, help, ayuda | Collaborative, specific, context-rich |
| `update` | update, status, actualización, progreso | Concise, progress-focused |
| `review` | review, feedback, revisión | Structured, actionable |

If unclear, ask the user.

## Step 4 — Detect language

Detect the language from:
1. The conversation language
2. The channel name (Spanish team channels → Spanish)
3. If unclear, ask

Load the appropriate template:
- Spanish → [references/templates-es.md](references/templates-es.md)
- English → [references/templates-en.md](references/templates-en.md)

## Step 5 — Draft message

Using the appropriate template for the message type, draft the message.

Include:
- Clear subject/headline
- Context (why this message is being sent)
- Key information (what happened, what changed, what is needed)
- Action items (if any — who needs to do what)
- Timeline (if applicable — when is this relevant)

**IMPORTANT:** The default action is to DRAFT the message, not send it. Always show the draft to the user first.

## Step 6 — Review and send

Present the draft to the user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📨 MESSAGE DRAFT
   To: {destination_name}
   Type: {message_type}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{formatted message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Ask the user:
1. **Send as draft** — use the adapter's draft command (if supported)
2. **Send now** — use the adapter's send command
3. **Edit** — let the user modify the message
4. **Cancel** — discard

## Step 7 — Confirm

After sending:
- Display confirmation with timestamp
- Show link to the message (if available from adapter response)
