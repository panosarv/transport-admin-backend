# app/db/session.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Engine: cast the Pydantic PostgresDsn to a plain string URL
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=True,     # set False in production
    future=True,
)

# Session factory for async sessions
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # prevents attribute expiration on commit
)

# Dependency to inject DB sessions into your path operations
async def get_db():
    async with async_session() as session:
        yield session
