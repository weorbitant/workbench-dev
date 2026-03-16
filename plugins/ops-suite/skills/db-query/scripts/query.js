#!/usr/bin/env node

/**
 * Generic PostgreSQL query helper for the db-query skill.
 *
 * Usage:
 *   DB_HOST=localhost DB_PORT=16432 DB_NAME=mydb DB_USER=user DB_PASSWORD=pass \
 *     node query.js "SELECT * FROM users LIMIT 10"
 *
 * Environment variables:
 *   DB_HOST     - Database host (default: localhost)
 *   DB_PORT     - Database port (default: 5432)
 *   DB_NAME     - Database name (required)
 *   DB_USER     - Database user (required)
 *   DB_PASSWORD - Database password (required)
 */

const { Client } = require('pg');

const query = process.argv[2];

if (!query) {
  console.error('Usage: node query.js "SQL QUERY"');
  console.error('Required env vars: DB_NAME, DB_USER, DB_PASSWORD');
  process.exit(1);
}

const requiredVars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD'];
const missing = requiredVars.filter(v => !process.env[v]);
if (missing.length > 0) {
  console.error(`Missing required environment variables: ${missing.join(', ')}`);
  process.exit(1);
}

const client = new Client({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432', 10),
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  // Simple query mode for PgBouncer compatibility
  statement_timeout: 30000,
});

async function run() {
  try {
    await client.connect();
    const start = Date.now();
    const result = await client.query(query);
    const duration = Date.now() - start;

    if (result.rows && result.rows.length > 0) {
      console.table(result.rows);
      console.log(`\nRows: ${result.rowCount} | Duration: ${duration}ms`);
    } else {
      console.log(`No rows returned. Affected: ${result.rowCount} | Duration: ${duration}ms`);
    }
  } catch (err) {
    console.error(`ERROR: ${err.message}`);
    if (err.detail) console.error(`Detail: ${err.detail}`);
    if (err.hint) console.error(`Hint: ${err.hint}`);
    process.exit(1);
  } finally {
    await client.end();
  }
}

run();
