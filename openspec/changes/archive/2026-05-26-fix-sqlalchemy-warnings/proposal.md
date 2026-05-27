# Proposal: Fix SQLAlchemy Verification Warnings

## Intent

The `sqlalchemy-models` change passed verification with 3 warnings that must be resolved: a missing dependency, a lint violation, and an untested rollback path. These are small but real — the missing dependency will break fresh installs, the lint violation will fail CI, and the untested rollback path leaves a spec gap.

## Scope

### In Scope
- Add `python-dotenv>=1.0.0` to `backend/requirements.txt`
- Fix ruff I001 import-order violation in `backend/src/database.py`
- Add `test_get_db_rollback_on_error` test to `backend/tests/test_database.py`

### Out of Scope
- Creating `backend/.env.example` (separate concern, tracked in verify report)
- Refactoring conftest to use `POSTGRES_TEST_DB` (design deviation, not a warning fix)
- Any model or schema changes

## Capabilities

### New Capabilities
None

### Modified Capabilities
- `database-connection`: adding explicit rollback-before-close behavior in `get_db` and a covering test for the "session rollback on error" scenario
- `testing-infrastructure`: adding `python-dotenv` as a declared test dependency

## Approach

1. **requirements.txt** — append `python-dotenv>=1.0.0` (conftest.py already imports it)
2. **database.py** — reorder imports so stdlib (`collections.abc`) precedes third-party (`sqlalchemy`), then add `db.rollback()` before `db.close()` in `get_db`'s finally block
3. **test_database.py** — add `test_get_db_rollback_on_error` that forces an exception inside `get_db` and asserts rollback was called

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/requirements.txt` | Modified | Add python-dotenv dependency |
| `backend/src/database.py` | Modified | Reorder imports, add explicit rollback |
| `backend/tests/test_database.py` | Modified | Add rollback-on-error test |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Adding rollback changes `get_db` behavior | Low | rollback-before-close is idempotent; uncommitted sessions already roll back on close |

## Rollback Plan

Revert the 3 files: `git checkout HEAD -- backend/requirements.txt backend/src/database.py backend/tests/test_database.py`

## Dependencies

- None beyond the existing sqlalchemy-models change

## Success Criteria

- [ ] `ruff check backend/src/database.py` passes with zero violations
- [ ] `pytest backend/tests/test_database.py::test_get_db_rollback_on_error` passes
- [ ] `python-dotenv` appears in `backend/requirements.txt`
- [ ] All existing 136 tests still pass