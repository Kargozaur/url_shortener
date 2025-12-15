from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from settings import settings

SQL_ALCHEMY_DB_URL = settings.DATABASE_URL

engine = create_async_engine(
    url=SQL_ALCHEMY_DB_URL, max_overflow=10, future=True
)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, autoflush=False  # type: ignore
)  # type: ignore


async def get_db():
    async with AsyncSessionLocal() as session:  # type: ignore
        try:
            yield session
        finally:
            await session.close()
