"""Соединение и работа с базой данных."""
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta

DATABASE_URL = os.getenv("POSTGRES_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
Base: DeclarativeMeta = declarative_base()


async def init_db() -> None:
    """Инициирование таблиц БД на основании ORM моделей."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def shutdown_db() -> None:
    """Завершение работы с БД."""
    await engine.dispose()
