# Tasks: Fix SQLAlchemy Verification Warnings

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~20 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | single PR |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: Testing — RED (TDD)

- [ ] 1.1 Write `test_get_db_rollback_on_error` in `backend/tests/test_database.py` — mock session that raises on close, verify `db.rollback()` is called before close
- [ ] 1.2 Run test — confirm it fails (RED) because `rollback()` is not yet implemented

## Phase 2: Core Implementation — GREEN

- [ ] 2.1 Fix `backend/src/database.py` — add `db.rollback()` in `finally` block before `db.close()`
- [ ] 2.2 Fix `backend/src/database.py` — reorder imports: stdlib (`collections.abc`) before third-party (`sqlalchemy`) to resolve ruff I001 violation
- [ ] 2.3 Add `python-dotenv>=1.0.0` to `backend/requirements.txt`

## Phase 3: Verification

- [ ] 3.1 Run `pytest backend/tests/test_database.py::test_get_db_rollback_on_error -v` — passes (GREEN)
- [ ] 3.2 Run `ruff check backend/src/database.py` — zero violations
- [ ] 3.3 Run full suite `pytest backend/tests/ -v` — all 137 tests pass
