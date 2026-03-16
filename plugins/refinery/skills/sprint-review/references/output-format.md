# Output Format — sprint-review (Terminal)

All output MUST be in Spanish.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 SPRINT REVIEW: {sprint_name}
   {total_tickets} tickets | {total_points} puntos | Readiness: {score}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RESUMEN
  Historias: {story_count} ({story_points} pts)
  Bugs:      {bug_count} ({bug_points} pts)
  Tareas:    {task_count} ({task_points} pts)
  Spikes:    {spike_count} ({spike_points} pts)

  Por asignado:
    {assignee_1}: {count} tickets ({points} pts)
    {assignee_2}: {count} tickets ({points} pts)
    Sin asignar: {count} tickets

━━ HALLAZGOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 PROBLEMAS SISTÉMICOS (afectan >{threshold}% del sprint)
  1. {check_name}: {fail_rate}% de tickets afectados
     → Recomendación: {recommendation}

🟡 DUPLICADOS ({count})
  - {KEY-1} ↔ {KEY-2}: "{title_similarity}"

🟡 DEFINICIÓN INSUFICIENTE ({count})
  - {KEY}: Sin criterios de aceptación
  - {KEY}: Descripción < 50 caracteres
  - {KEY}: AC no testeables: "{vague_ac}"

🟡 SIN ESTIMACIÓN ({count})
  - {KEY}: "{title}"
  - {KEY}: "{title}"

🟡 LENGUAJE VAGO ({count})
  - {KEY}: encontrado "{term}" en {location}
  - {KEY}: encontrado "{term}" en {location}

🟡 DEPENDENCIAS ({count})
  - {KEY} bloqueado por {OTHER_KEY} (estado: {status})
  - {KEY} menciona {OTHER_KEY} sin link formal

🟡 BALANCE
  {bug_percentage}% del sprint son bugs
  {assessment}

🟡 TICKETS SOBREDIMENSIONADOS ({count})
  - {KEY}: {points} puntos — "{title}"
    → Sugerencia: dividir en {suggested_split}

🟡 SIN ASIGNAR ({count})
  - {KEY}: "{title}"

━━ VEREDICTO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{✅ LISTO PARA INICIAR | ⚠️ NECESITA TRABAJO | 🚫 NO LISTO}

{One paragraph summary with key actions needed}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Omit sections that have zero findings. Only show checks that found issues.
