# TypeORM Adapter — db-migrate

TypeORM uses its own CLI for migrations. The migration command is typically run from the project root.

## Environment variables for database connection

```bash
export TYPEORM_HOST=localhost
export TYPEORM_PORT={local_port}
export TYPEORM_DATABASE={env.services.database.default_db}
export TYPEORM_USERNAME={db_user}
export TYPEORM_PASSWORD={db_password}
```

Note: The exact variable names depend on your project's TypeORM config (ormconfig.json, data-source.ts, etc.).

## List pending migrations

```bash
npx typeorm migration:show -d {datasource_path}
```

Pending migrations are marked with `[ ]`, applied with `[X]`.

## Run pending migrations

```bash
npx typeorm migration:run -d {datasource_path}
```

Or if `deploy.migration_command` is set in config, use that instead:
```bash
{deploy.migration_command}
```

## Rollback last migration

```bash
npx typeorm migration:revert -d {datasource_path}
```

## Create a new migration (local development only)

```bash
npx typeorm migration:generate -d {datasource_path} -n {MigrationName}
```

## Verify migration was applied

```bash
npx typeorm migration:show -d {datasource_path}
```

All migrations should show `[X]`.

## Direct database verification

```bash
node -e "
const { Client } = require('pg');
const c = new Client({ host:'localhost', port:{local_port}, database:'{env.services.database.default_db}', user:'{db_user}', password:'{db_password}' });
c.connect().then(() => c.query('SELECT * FROM migrations ORDER BY timestamp DESC LIMIT 5'))
.then(r => { console.table(r.rows); c.end(); })
.catch(e => { console.error(e.message); c.end(); });
"
```
