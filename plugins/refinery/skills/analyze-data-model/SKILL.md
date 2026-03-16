---
name: analyze-data-model
description: "Use when interrogating the codebase to understand an entity, its fields, relationships, and data flows. Use when user says 'analyze data model', 'analizar modelo', 'understand entity', 'check schema', or asks about a specific entity or database field."
argument-hint: "[entity or field name]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
---

## Step 0 — Load configuration

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`.
If it does not exist, this skill can still operate on the codebase directly. Log a warning but continue.

Check if config defines any custom code paths or conventions that should guide the search (e.g., specific directories for models, migrations, etc.).

## Step 1 — Parse argument

From `$ARGUMENTS`, extract the entity or field name to investigate.
If no argument provided, ask the user what entity or field they want to understand.

Store as `{entity}`.

## Step 2 — Locate entity definition

Search the codebase for the entity definition:

1. **ORM models** — Search for class/interface definitions matching `{entity}`:
   - Glob: `**/*{entity}*.*` (case-insensitive approach — try variations)
   - Grep: `class {Entity}`, `interface {Entity}`, `@Entity.*{entity}`, `model {Entity}`
   - Check common model directories: `src/models/`, `src/entities/`, `app/models/`, `prisma/schema.prisma`

2. **Database schemas** — Search migrations and schema files:
   - Grep: `CREATE TABLE.*{entity}`, `createTable.*{entity}`, `tableName.*{entity}`
   - Glob: `**/migrations/**`

3. **DTOs and types** — Search for data transfer objects:
   - Grep: `{Entity}Dto`, `{Entity}Input`, `{Entity}Response`, `{Entity}Type`

If multiple matches found, present them and ask the user which one to focus on.

## Step 3 — Interrogate each field

For each field found in the entity definition, answer these questions:

| Pregunta | Cómo encontrarlo |
|----------|------------------|
| What does this field mean? | Check comments, JSDoc, variable name semantics |
| Where does the data originate? | Grep for assignments to this field |
| Who/what generates it? | Check constructors, factory methods, seed data |
| Under what condition is it created? | Check create methods, POST endpoints |
| When/how does it mutate? | Grep for update/set operations on this field |
| What validations exist? | Check decorators, validators, constraints |
| What are the possible values? | Check enums, unions, DB constraints |
| Is it nullable? | Check schema definition, TypeScript types |
| Is it indexed? | Check migration files, schema decorators |

Build a comprehensive field table:

| Campo | Tipo | Nullable | Default | Validaciones | Origen | Mutaciones |
|-------|------|----------|---------|-------------|--------|-----------|
| {field} | {type} | {yes/no} | {value} | {rules} | {source} | {when/how} |

## Step 4 — Config parameter interrogation

If the entity involves configuration or environment variables, also investigate:

| Config | Dónde se define | Valor por defecto | Dónde se usa | Qué pasa si falta |
|--------|----------------|-------------------|-------------|-------------------|

Search for:
- `process.env.{RELATED_VARS}`
- Config files referencing the entity
- Feature flags that control behavior for this entity

## Step 5 — Map relationships

Search for references to the entity from other files:

1. **Foreign keys** — Grep for `{entity}Id`, `{entity}_id`, references in migrations
2. **ORM relations** — `@ManyToOne`, `@OneToMany`, `@ManyToMany`, `belongsTo`, `hasMany`, `references`
3. **Imports** — Which files import this entity
4. **Type references** — Where this entity is used as a type

Build a relationship map:
```
{Entity} ──1:N──▶ {RelatedEntity}
{Entity} ◀──N:1── {ParentEntity}
{Entity} ──N:M──▶ {OtherEntity} (via {JoinTable})
```

## Step 6 — Check migrations

Search migration files for this entity:
- Glob: `**/migrations/**`
- Grep: `{entity}`, `{table_name}`

List all migrations that touch this entity, in chronological order:
1. {date} — Created table with columns: ...
2. {date} — Added column {field}: ...
3. {date} — Added index on {field}: ...

## Step 7 — Check consumers and endpoints

Find all API endpoints and consumers that read or write this entity:

1. **REST endpoints** — Grep for route definitions mentioning the entity
2. **GraphQL resolvers** — Grep for resolver/query/mutation definitions
3. **Event handlers** — Grep for event listeners that process this entity
4. **Scheduled jobs** — Grep for cron/scheduled tasks involving this entity
5. **Message consumers** — Grep for queue/topic consumers

For each consumer:
| Endpoint/Consumer | Método | Lee campos | Escribe campos | Validaciones |
|-------------------|--------|-----------|---------------|-------------|
| {path} | {GET/POST/...} | {fields} | {fields} | {rules} |

## Step 8 — Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗃️ DATA MODEL ANALYSIS: {Entity}
   Source: {file_path}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━ CAMPOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{field table from Step 3}

━━ ORIGEN DE DATOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━
{For each field: where data comes from and how it is generated}

━━ RELACIONES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{relationship map from Step 5}

━━ VALIDACIONES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{All validation rules found, grouped by field}

━━ MIGRACIONES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chronological migration history from Step 6}

━━ ENDPOINTS / CONSUMERS ━━━━━━━━━━━━━━━━━━━━━
{consumer table from Step 7}

━━ PREGUNTAS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{Questions that could not be answered from code alone}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
