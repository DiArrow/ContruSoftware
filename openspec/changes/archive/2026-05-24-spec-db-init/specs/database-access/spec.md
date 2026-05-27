# Database Access Specification

## Purpose

Define the application user creation, permission model, and credential management for the ContruSoftware PostgreSQL database.

## Requirements

### Requirement: Application User Creation

The system SHALL create a dedicated `app_user` role with LOGIN capability for the application to connect to the database.

#### Scenario: User created successfully

- GIVEN a PostgreSQL database with the schema initialized
- WHEN the users.sql script is executed
- THEN a role `app_user` exists with LOGIN enabled
- AND the role can authenticate with the configured password

#### Scenario: User already exists

- GIVEN `app_user` role already exists
- WHEN the users.sql script is executed again
- THEN the script handles the duplicate gracefully (uses `CREATE ROLE IF NOT EXISTS` or equivalent)
- AND no error is raised

### Requirement: Permission Model

The system SHALL grant `app_user` only the minimum permissions required: `SELECT`, `INSERT`, `UPDATE`, `DELETE` on all tables in the `public` schema. The user SHALL NOT have `DROP`, `ALTER`, `CREATE`, or `TRUNCATE` privileges.

| Privilege | Granted | Rationale |
|-----------|---------|-----------|
| CONNECT | Yes | Access database |
| USAGE on public schema | Yes | Access schema objects |
| SELECT | Yes | Read data |
| INSERT | Yes | Create records |
| UPDATE | Yes | Modify records |
| DELETE | Yes | Remove records |
| DROP | No | Prevent schema destruction |
| ALTER | No | Prevent schema changes |
| CREATE | No | Prevent new objects |
| TRUNCATE | No | Prevent bulk deletion |

#### Scenario: CRUD operations succeed

- GIVEN `app_user` is connected to the database
- WHEN the user executes `SELECT`, `INSERT`, `UPDATE`, or `DELETE` on any application table
- THEN the operation succeeds

#### Scenario: DDL operations denied

- GIVEN `app_user` is connected to the database
- WHEN the user executes `DROP TABLE usuario` or `ALTER TABLE usuario ADD COLUMN foo TEXT`
- THEN the operation fails with a permission denied error
- AND the table schema remains unchanged

### Requirement: Credential Management via Environment Variables

The system SHALL obtain the `app_user` password from the `POSTGRES_APP_PASSWORD` environment variable. Credentials SHALL NOT be hardcoded in SQL scripts or configuration files.

#### Scenario: Password from environment variable

- GIVEN `POSTGRES_APP_PASSWORD` is set in the docker-compose environment
- WHEN the users.sql script is executed via psql with variable substitution
- THEN `app_user` is created with the password value from the environment variable
- AND the literal string `${POSTGRES_APP_PASSWORD}` does NOT appear in the created role's password

#### Scenario: Missing environment variable

- GIVEN `POSTGRES_APP_PASSWORD` is not set in the environment
- WHEN docker-compose attempts to start the database
- THEN the container fails to start or the user creation fails
- AND a clear error message indicates the missing variable

#### Scenario: No hardcoded credentials

- GIVEN all SQL files in `db/init/`
- WHEN the files are scanned for password literals
- THEN no hardcoded passwords are found
- AND all password references use variable substitution (`:var` or `psql` variable syntax)

### Requirement: Default Privileges for Future Tables

The system SHALL configure default privileges so that `app_user` automatically receives `SELECT`, `INSERT`, `UPDATE`, `DELETE` on any new tables created in the `public` schema after the initial setup.

#### Scenario: New table inherits permissions

- GIVEN default privileges are configured for `app_user`
- WHEN a new table is created in the `public` schema by the superuser
- THEN `app_user` can immediately `SELECT`, `INSERT`, `UPDATE`, `DELETE` on the new table
- AND no additional GRANT statement is needed
