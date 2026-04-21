---
name: port-forward
description: Establish local connections to cluster services like databases, brokers, and APIs. Use when asked about "port-forward", "connect to database", "local connection", "tunnel", "forward port", "access service locally". TRIGGER when: user asks "port-forward to X", "connect to database locally", "tunnel to service", "forward port", "access service locally", "open local connection to X". SKIP: checking service health (use service-status); running queries (use db-query).
argument-hint: "[service] [environment]"
allowed-tools:
  - Bash
  - AskUserQuestion
model: haiku
---

## Step 0 — Load configuration

Check if `/tmp/ops-suite-session/config.json` exists:
- If yes, read it (pre-parsed by session-start hook).
- If no, read the plugin's `config.yaml`, parse it, and write to `/tmp/ops-suite-session/config.json` for other skills to reuse.
If neither exists, tell the user to copy `config.example.yaml` to `config.yaml` and fill in their values. Stop here.

Extract:
- `orchestrator` — determines which adapter to load
- `environments` — available environments and their connection details
- `service_registry` — known services with their ports and namespaces
- `deploy.local_ports` — preferred local port mappings

## Step 1 — Load adapter

Read the adapter file at `adapters/{orchestrator}.md` (in this skill's directory).
If the adapter does not exist, tell the user that the orchestrator `{orchestrator}` is not yet supported and stop.

## Step 2 — Determine target environment and service

If `$ARGUMENTS` contains an environment name, use it. Otherwise ask the user.
If `$ARGUMENTS` contains a service name, check it against `service_registry`.

If the service is found in `service_registry`, use its predefined configuration:
- `namespace`, `service`, `port`, `verify`

If the service is NOT in the registry:
- Use the adapter's "search services" command to find matching services
- Ask the user to confirm the target and port

## Step 3 — Resolve local port

Determine the local port:
1. If the service is a database and `deploy.local_ports.{env}` is defined, use that
2. If the service_registry entry has a port, use the same port locally
3. Otherwise, pick a sensible default and confirm with the user

Check for port conflicts using the adapter's "check port" command. If the port is in use, suggest an alternative.

## Step 4 — Establish connection

Run the adapter's "port-forward" command in the background.
Wait briefly and verify the connection using:
1. The `verify` command from service_registry (if defined)
2. Or a basic TCP connection check

## Step 5 — Provide connection details

Display to the user:

```
Port-forward active:
  Service:   {service_name}
  Remote:    {remote_host}:{remote_port}
  Local:     localhost:{local_port}
  Namespace: {namespace}

Connection string: {connection_string_if_applicable}

To stop: kill the background process or press Ctrl+C
PID: {pid}
```

## Step 6 — Credentials (if needed)

If the service requires credentials (e.g., database):
- **Never hardcode credentials**
- Use the adapter's "retrieve secret" command if available
- Otherwise, ask the user to provide credentials
- Display the connection string with credential placeholders

## Important notes

- Always check for existing port-forwards to avoid conflicts
- Always provide cleanup instructions
- Never log or display passwords in plain text
