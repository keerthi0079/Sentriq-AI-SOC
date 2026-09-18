import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.core.database import async_engine
from app.main import app


@pytest_asyncio.fixture(scope="function")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    # Ensure all pooled connections are cleanly closed before the test loop terminates
    await async_engine.dispose()

