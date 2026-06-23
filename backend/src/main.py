"""FastAPI application entry point."""

from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from database import get_db
from routers.admin import router as admin_router
from routers.auth import router as auth_router
from routers.impresiones import router as impresiones_router
from routers.semestres import router as semestres_router

app = FastAPI(title="ContruSoftware API")

# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(impresiones_router)
app.include_router(semestres_router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that validates database connectivity."""
    try:
        # Execute a simple query to verify database connectivity
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except OperationalError as e:
        # Extract the original exception message
        detail = str(e.orig) if e.orig else str(e)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "detail": detail},
        )
