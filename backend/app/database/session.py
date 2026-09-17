from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config.settings import settings

Base = declarative_base()

# Convert provider database URLs to the asyncpg SQLAlchemy driver.
database_url = settings.DATABASE_URL
for scheme in ("postgres://", "postgresql://"):
    if database_url.startswith(scheme):
        database_url = database_url.replace(scheme, "postgresql+asyncpg://", 1)
        break

engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
