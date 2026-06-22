
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from backend.core.settings import settings

database_url = 'postgresql://faroosha:jQmyUKKVpfppyc5xUGk7X6JfAm3Jhi5u@dpg-d8sdv6e7r5hc73fcg1o0-a.frankfurt-postgres.render.com/chatdatabase_a7jq'


# Create async database engine
engine = create_async_engine(
    database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True
)


# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

async def init_db() -> None :
    ''' Initialize database tables '''
    import backend.models  # noqa: F401 — register all ORM models

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

async def close_db() -> None :
    ''' Close database connections'''
    await engine.dispose()

