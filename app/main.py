import logging

from fastapi import FastAPI, status
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging import setup_logging
from app.routers import invoices, timesheet


# =========================================================
# Logging
# =========================================================

setup_logging()

logger = logging.getLogger(__name__)


# =========================================================
# FastAPI Application
# =========================================================

app = FastAPI(
    title="Invoice Service",
    description="Timesheet and Invoice Management Microservice",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)


# =========================================================
# Application Startup
# =========================================================

@app.on_event("startup")
def startup() -> None:
    try:
        Base.metadata.create_all(
            bind=engine,
        )

        logger.info(
            "%s started successfully on port %s",
            settings.app_name,
            settings.app_port,
        )

    except SQLAlchemyError:
        logger.exception(
            "Database startup failed."
        )
        raise


# =========================================================
# Health Check
# =========================================================

@app.get(
    "/health",
    tags=["Health"],
)
def health_check():

    return {
        "success": True,
        "status_code": status.HTTP_200_OK,
        "message": "Invoice service is healthy.",
        "data": {
            "service": settings.app_name,
            "status": "UP",
        },
        "errors": [],
    }


# =========================================================
# Routers
# =========================================================

app.include_router(
    timesheet.router,
)

app.include_router(
    invoices.router,
)