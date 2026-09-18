from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.core.database import check_db_health
from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Returns application status and database connectivity."""
    db_connected = await check_db_health()
    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        database="connected" if db_connected else "disconnected",
        database_engine="PostgreSQL 16 (Docker Desktop)",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

