# Slack Adapter — notify-team

## Discover MCP tools

Use ToolSearch to find Slack MCP tools:
```
ToolSearch: +slack send_message
```
Store the discovered prefix as `{slack_prefix}`.

## Channel registry

Channels are configured in `{config.communication.channels}`. Each entry has:
- `id` — the Slack channel ID (e.g., "CXXXXXXXXXX")
- `name` — the display name (e.g., "#my-team")

Use the `id` for all API calls and the `name` for display.

## Search channels

If the destination is not in the configured channels:
```
{slack_prefix}__slack_search_channels(
  query: "{channel_name}"
)
```

## Search users

To find a person:
```
{slack_prefix}__slack_search_users(
  query: "{user_name}"
)
```

## Send message draft

Preferred method — creates a draft that the user can review in Slack before sending:
```
{slack_prefix}__slack_send_message_draft(
  channel: "{destination_id}",
  message: "{formatted_message}"
)
```

## Send message (immediate)

Only use when the user explicitly confirms they want to send immediately:
```
{slack_prefix}__slack_send_message(
  channel: "{destination_id}",
  message: "{formatted_message}"
)
```

## Schedule message

If the user wants to send at a specific time:
```
{slack_prefix}__slack_schedule_message(
  channel: "{destination_id}",
  message: "{formatted_message}",
  post_at: "{unix_timestamp}"
)
```

## Read channel (for context)

To check recent messages in a channel before posting:
```
{slack_prefix}__slack_read_channel(
  channel: "{destination_id}",
  limit: 10
)
```

## Message formatting (Slack mrkdwn)

Use Slack mrkdwn formatting:
- Bold: `*text*`
- Italic: `_text_`
- Code: `` `code` ``
- Code block: ` ```code``` `
- Link: `<url|display text>`
- User mention: `<@user_id>`
- Channel mention: `<#channel_id>`
- Emoji: `:emoji_name:`
- Bullet list: `• item` (use bullet character, not dash)
- Blockquote: `> text`

Keep messages under 4000 characters. If longer, split into multiple messages or use a thread.
