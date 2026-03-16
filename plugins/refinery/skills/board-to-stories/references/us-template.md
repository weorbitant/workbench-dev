# User Story Template

## Format

```markdown
# {US_ID}: {Title}

## User Story
Como **{role}**, quiero **{action}**, para **{benefit}**.

## Contexto
{Why this story exists. What problem it solves. Background information.}

## Criterios de Aceptación
- [ ] **Dado** {precondition}, **cuando** {action}, **entonces** {expected result}
- [ ] **Dado** {precondition}, **cuando** {action}, **entonces** {expected result}
- [ ] {Simple criterion if Gherkin is overkill}

## Notas técnicas
- {Implementation hints, relevant patterns, affected modules}
- {Data model considerations}
- {Integration points}

## Diseño
- Link: {design URL if available}
- Pantallas: {list of screens/frames}

## Dependencias
- Depende de: {US_ID or ticket key}
- Bloquea a: {US_ID or ticket key}

## Complejidad
{S | M | L | XL}

## Estado
{Definida | Implícita | Bloqueada}
Razón bloqueo: {if blocked, why}
```

## Complexity guide

| Size | Description | Story points (approx) |
|------|-------------|----------------------|
| S | Simple change, single file, clear pattern exists | 1-2 |
| M | Multi-file change, follows existing pattern | 3-5 |
| L | New feature, multiple modules, some unknowns | 5-8 |
| XL | Large feature, architectural changes, many unknowns — should be split | 8-13+ |

## Role format

Always use roles from `{config.board_config.available_roles}`. If a board item does not map to a configured role, use the closest match and flag it for review.

Common role patterns:
- End user roles: usuario, cliente, administrador
- Internal roles: asesor, técnico, coordinador, supervisor
- System roles: sistema, servicio, cron job
