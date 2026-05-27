from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.auth.dependencies import oauth2_scheme  # noqa: F401
from src.database import get_db

app = FastAPI()


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Verify database connectivity and return health status."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": str(exc)},
        )
    return {"status": "ok"}
