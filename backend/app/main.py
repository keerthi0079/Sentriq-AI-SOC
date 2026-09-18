import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.api.v1.ws import router as ws_router
from app.core.config import settings
from app.core.database import close_db, init_db
from app.services.streamer import background_streamer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sentriq")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to handle application startup and shutdown."""
    logger.info("Starting Sentriq AI-SOC Backend...")
    try:
        await init_db()
        logger.info("Sentriq database tables initialized on PostgreSQL (Docker Desktop).")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    yield
    logger.info("Shutting down Sentriq AI-SOC Backend...")
    try:
        await background_streamer.stop()
    except Exception as e:
        logger.warning(f"Error stopping background streamer: {e}")
    await close_db()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
app.include_router(ws_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "docs": "/docs",
        "api_v1": settings.API_V1_PREFIX,
        "database": "PostgreSQL 16 via Docker Desktop",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
