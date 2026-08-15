import pytest
from app.db.session import AsyncSessionLocal, get_db


@pytest.mark.asyncio
async def test_async_session_factory():
    """Verify that AsyncSessionLocal generates a valid SQLAlchemy AsyncSession instance."""
    session = AsyncSessionLocal()
    assert session is not None
    await session.close()


@pytest.mark.asyncio
async def test_get_db_generator():
    """Verify that get_db generator yields an async database session."""
    gen = get_db()
    session = await anext(gen)
    assert session is not None
    try:
        await anext(gen)
    except StopAsyncIteration:
        pass
