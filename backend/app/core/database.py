import logging
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Base class for all ORM models
Base = declarative_base()

# Async Engine (Primary for FastAPI handlers)
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Synchronous Engine (For migrations, seed scripts, or synchronous workers)
try:
    sync_engine = create_engine(
        settings.SYNC_DATABASE_URL,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )
    SyncSessionLocal = sessionmaker(
        bind=sync_engine,
        autocommit=False,
        autoflush=False,
    )
except Exception as e:
    logger.warning(f"Sync database engine could not be initialized: {e}")
    sync_engine = None
    SyncSessionLocal = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session for FastAPI endpoints."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Creates all database tables defined in the models."""
    async with async_engine.begin() as conn:
        logger.info("Initializing database tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")


async def check_db_health() -> bool:
    """Checks if PostgreSQL is reachable and answering queries."""
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def close_db() -> None:
    """Closes and disposes of the connection pool."""
    await async_engine.dispose()
    if sync_engine:
        sync_engine.dispose()

