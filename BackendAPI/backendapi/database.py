from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from backendapi.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)


async def create_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
