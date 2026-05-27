# Health Check Specification

## Purpose

Define a `GET /health` endpoint that verifies PostgreSQL database connectivity and returns a structured JSON response.

## Requirements

### Requirement: Health Endpoint

The system SHALL expose `GET /health` on the FastAPI application. The endpoint SHALL execute a database connectivity check and return JSON with status.

| Response Field | Type | Values |
|----------------|------|--------|
| status | string | `"ok"` or `"error"` |

#### Scenario: healthy database returns ok

- GIVEN PostgreSQL is running and reachable
- WHEN `GET /health` is called
- THEN response status code is 200
- AND response body is `{"status": "ok"}`

#### Scenario: database unreachable returns error

- GIVEN PostgreSQL is not running or unreachable
- WHEN `GET /health` is called
- THEN response status code is 503
- AND response body is `{"status": "error"}`

### Requirement: Database Connectivity Verification

The health check SHALL verify connectivity by executing a simple query (`SELECT 1`) via a dependency-injected database session.

#### Scenario: SELECT 1 succeeds

- GIVEN a valid database session from `get_db`
- WHEN `SELECT 1` is executed
- THEN the query returns `[1]`
- AND health status is `"ok"`

#### Scenario: connection timeout

- GIVEN the database is unreachable
- WHEN the health check attempts `SELECT 1`
- THEN a connection exception is caught
- AND health status is `"error"`

### Requirement: Integration with main.py

The `/health` route SHALL be registered in `backend/src/main.py`. The skeleton example code SHALL be removed.

#### Scenario: endpoint is accessible

- GIVEN the FastAPI app starts successfully
- WHEN `TestClient(app).get("/health")` is called
- THEN the endpoint responds
- AND the old skeleton routes are not present

## Acceptance Criteria

- [ ] `GET /health` returns `{"status": "ok"}` with status 200 when DB is reachable
- [ ] `GET /health` returns `{"status": "error"}` with status 503 when DB is unreachable
- [ ] Health check uses `Depends(get_db)` for session injection
- [ ] Skeleton code in `main.py` is removed
- [ ] Health check test passes via TestClient
