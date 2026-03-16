# MikroORM Adapter — db-migrate

MikroORM uses its own CLI for migrations. The migration command is typically run from the project root.

## Environment variables for database connection

```bash
export DB_HOST=localhost
export DB_PORT={local_port}
export DB_NAME={env.services.database.default_db}
export DB_USER={db_user}
export DB_PASSWORD={db_password}
```

Note: The exact variable names depend on your project's mikro-orm config. Check `mikro-orm.config.ts` or equivalent.

## List pending migrations

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
