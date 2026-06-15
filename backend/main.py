"""Compatibility shim used by tests.

This module ensures the code under `backend/src/` can be imported both as
top-level packages (e.g. `import auth.router`) and as the `src` package
(e.g. `import src.database`). It then re-exports the FastAPI `app`.
"""

import os
import sys
import types

_here = os.path.dirname(__file__)
_src_path = os.path.join(_here, "src")

# Ensure the source dir is on sys.path so imports like `import auth.router`
# resolve against backend/src.
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

# Create a synthetic package module named 'src' that points to the same
# directory so imports like `import src.database` also work.
if "src" not in sys.modules:
    src_pkg = types.ModuleType("src")
    src_pkg.__path__ = [_src_path]
    sys.modules["src"] = src_pkg

# Import and re-export the FastAPI application from the source package.
# Prefer `src.main` to avoid importing this shim recursively.
try:
    from src.main import app  # re-export the FastAPI application
except Exception:
    # If importing fails, surface the error when tests or runtime import `app`.
    raise

__all__ = ["app"]
