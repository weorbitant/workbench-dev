# Output Format — ticket-analysis

Fixed 8-section structure. Never skip sections. If a section has no findings, write "No se encontraron hallazgos en esta sección."

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔬 TICKET ANALYSIS: {key} — {title}
   Type: {ticket_type} | Status: {status} | Points: {points}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

═══ SECCIÓN 1: RESUMEN DEL TICKET ═══

{Brief summary of what the ticket asks for, in your own words}

Tipo clasificado: {business-feature | technical-infra | bug-fix | data-integration}
Fuentes analizadas: {list of sources checked — ticket, design, docs, codebase}

═══ SECCIÓN 2: DATOS Y CAMPOS ═══

| Dato / Campo | Ticket | Diseño | Docs | Código | Estado |
|-------------|--------|--------|------|--------|--------|
| {field_1}   | ✅     | ✅     | ❓    | ✅     | Claro  |
| {field_2}   | ✅     | ❌     | ❌    | ❌     | Dudoso |

═══ SECCIÓN 3: REGLAS DE NEGOCIO ═══

1. {rule_1} — Fuente: {source}
2. {rule_2} — Fuente: {source}

Contradicciones encontradas:
- {source_a} dice "{X}" pero {source_b} dice "{Y}"

═══ SECCIÓN 4: DISEÑO Y UI ═══

Estados detectados:
- ✅ {state}: {description}
- ❌ {missing_state}: no encontrado en diseño

Campos del diseño:
- {field}: {type}, {validation_info}

Flujos implícitos:
- {flow_description}

═══ SECCIÓN 5: MODELO DE DATOS ═══

Entidades involucradas: {entity_list}

| Campo | Tipo | Origen | Validaciones | En código |
|-------|------|--------|-------------|-----------|
| {field} | {type} | {source} | {validations} | {yes/no} |

Relaciones: {entity_a} → {entity_b} ({relationship_type})
Migraciones necesarias: {yes/no — detail}

═══ SECCIÓN 6: FACTIBILIDAD TÉCNICA ═══

Complejidad estimada: {low | medium | high}

Patrones existentes: {list of relevant patterns found in codebase}
Gaps de implementación: {what does not exist yet}
Riesgos técnicos: {list}
Dependencias: {external services, libraries, teams}

═══ SECCIÓN 7: ALCANCE Y PREGUNTAS ═══

SE ENTREGA:
- {item_1}
- {item_2}

NO SE ENTREGA:
- {item_1}
- {item_2}

BLOQUEADO:
- {item_1} — Razón: {reason}

Preguntas por audiencia:

[Product/PO]
1. {question}
2. {question}

[Design/UX]
1. {question}

[Tech Lead]
1. {question}

[QA]
1. {question}

═══ SECCIÓN 8: PRÓXIMOS PASOS ═══

1. {action_1}
2. {action_2}
3. {action_3}

Subtareas sugeridas:
- [ ] {subtask_1}
- [ ] {subtask_2}
- [ ] {subtask_3}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
