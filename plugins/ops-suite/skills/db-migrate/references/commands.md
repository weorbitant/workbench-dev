# db-migrate — Step-by-step Reference

## Pre-migration checklist

1. **Identify the target environment** (dev or prod)
2. **Always run dev first** before running on prod
3. **Check pending migrations** to know what will be applied
4. **Read migration files** to understand what schema changes will happen
5. **Ensure you have a backup** or rollback plan

## Connection setup

1. **Port-forward to the database**
   - Use `port-forward` skill or manually:
   ```
   kubectl --context={env.context} port-forward svc/{env.services.database.name} {deploy.local_ports.{env_name}}:{env.services.database.port} -n {env.namespaces.infra} &
   ```

2. **Retrieve credentials**
   - From Kubernetes secrets:
   ```
   kubectl --context={env.context} get secret {db_secret_name} -n {env.namespaces.apps} -o jsonpath='{.data.password}' | base64 -d
   ```
   - Or ask the user

3. **Set environment variables**
   - Export DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
   - Use the values from the port-forward and credentials

## Migration execution

4. **Run the migration command**
   - Use the adapter's command or `deploy.migration_command` from config
   - Capture output for verification

5. **Verify the result**
   - List migrations to confirm all are applied
   - Run a quick query to confirm DB access

## Post-migration

6. **Cleanup**
   - Kill port-forward processes
   - Unset environment variables

7. **If migration failed**
   - Check error output
   - Consider rolling back with the adapter's rollback command
   - Do NOT proceed to prod if dev failed

## Rollback procedure

If a migration needs to be rolled back:
1. Run the adapter's rollback/down command
2. Verify the schema is back to the previous state
3. Investigate the failure before retrying
