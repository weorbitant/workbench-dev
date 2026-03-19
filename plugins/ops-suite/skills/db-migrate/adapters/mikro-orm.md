# MikroORM Adapter — db-migrate

MikroORM uses its own CLI for migrations. The migration command is typically run from the project root.

**IMPORTANT**: The mikro-orm CLI is typically a `devDependency` and is NOT available inside production container images.
Running `npm run migrations:up` inside a prod pod will fail with "mikro-orm: not found".
Migrations must be run **locally** via port-forward to the remote database.

**IMPORTANT**: `npx mikro-orm migration:pending` run locally can give false results if the local config
resolves to a different database. Always verify pending migrations by querying the `mikro_orm_migrations`
table directly in the target database.

## Environment variables for database connection

```bash
export DB_HOST=localhost
export DB_PORT={local_port}
export DB_NAME={database_name}
export DB_USER={db_user}
export DB_PASSWORD={db_password}
```

Note: The exact variable names depend on your project's mikro-orm config. Check `mikro-orm.config.ts` or equivalent.
Resolve `{database_name}` from `service_databases.{service}.{env}` in config if available.

## Verify pending migrations (reliable method)

Query the target database directly — do NOT rely solely on `migration:pending`:
```bash
node -e "
const { Client } = require('pg');
const c = new Client({ host:'localhost', port:{local_port}, database:'{database_name}', user:'{db_user}', password:'{db_password}' });
c.connect()
  .then(() => c.query('SELECT name, executed_at FROM mikro_orm_migrations ORDER BY executed_at DESC'))
  .then(r => { console.table(r.rows); return c.end(); })
  .catch(e => { console.error(e.message); c.end(); });
"
```
Cross-reference with migration files in `src/migrations/` to identify truly pending ones.

## List pending migrations (local CLI — may be unreliable for remote DBs)

```bash
npx mikro-orm migration:pending
```

## Check migration status (all migrations)

```bash
npx mikro-orm migration:list
```

## Run pending migrations

```bash
npx mikro-orm migration:up
```

Or if `deploy.migration_command` is set in config, use that instead:
```bash
{deploy.migration_command}
```

## Run migrations manually (when CLI is unavailable)

If the mikro-orm CLI is not available (e.g., prod image), run the migration SQL manually:
1. Read the migration `.ts` file to extract the SQL statements
2. Execute each SQL statement via node + pg client:
```bash
node -e "
const { Client } = require('pg');
const c = new Client({ host:'localhost', port:{local_port}, database:'{database_name}', user:'{db_user}', password:'{db_password}' });
c.connect()
  .then(() => c.query('ALTER TABLE ...'))
  .then(() => c.query(\"INSERT INTO mikro_orm_migrations (name, executed_at) VALUES ('{migration_name}', NOW())\"))
  .then(() => { console.log('Done'); return c.end(); })
  .catch(e => { console.error(e.message); c.end(); });
"
```
**Always register the migration** in `mikro_orm_migrations` after applying the SQL.

## Run a specific migration

```bash
npx mikro-orm migration:up --to {migration_name}
```

## Rollback last migration

```bash
npx mikro-orm migration:down
```

## Create a new migration (local development only)

```bash
npx mikro-orm migration:create
```

## Verify migration was applied

```bash
npx mikro-orm migration:list
```

Check that all migrations show as "applied" or "executed".

## Direct database verification

After running migrations, verify the schema:
```bash
node -e "
const { Client } = require('pg');
const c = new Client({ host:'localhost', port:{local_port}, database:'{env.services.database.default_db}', user:'{db_user}', password:'{db_password}' });
c.connect().then(() => c.query('SELECT * FROM mikro_orm_migrations ORDER BY executed_at DESC LIMIT 5'))
.then(r => { console.table(r.rows); c.end(); })
.catch(e => { console.error(e.message); c.end(); });
"
```
