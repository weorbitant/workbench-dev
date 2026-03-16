# Output Format — sprint-review (Slack)

All output MUST be in Spanish. Use Slack mrkdwn formatting.

```
*📋 SPRINT REVIEW: {sprint_name}*
{total_tickets} tickets | {total_points} puntos | Readiness: {score}

*📊 Resumen*
• Historias: {story_count} ({story_points} pts)
• Bugs: {bug_count} ({bug_points} pts)
• Tareas: {task_count} ({task_points} pts)

*🔴 Problemas sistémicos*
{Only include if systemic issues exist}
1. *{check_name}*: {fail_rate}% de tickets afectados → {recommendation}

*🟡 Hallazgos por ticket*
• `{KEY}` — {finding_summary}
• `{KEY}` — {finding_summary}
• `{KEY}` — {finding_summary}

*Veredicto: {✅ LISTO | ⚠️ NECESITA TRABAJO | 🚫 NO LISTO}*
{One line summary}
```

Keep Slack messages under 4000 characters. If the full report exceeds this:
1. Send a summary message with systemic issues and verdict
2. Offer to send detailed findings as a thread reply
