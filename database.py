from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import config


class Base(DeclarativeBase):
    pass


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def _build_engine(url: str):
    kwargs = {"echo": False}
    if _is_sqlite(url):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_async_engine(url, **kwargs)


engine = _build_engine(config.DATABASE_URL)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session


@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _connection_record):
    if _is_sqlite(config.DATABASE_URL):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async def init_db():
    async with engine.begin() as conn:
        if _is_sqlite(config.DATABASE_URL):
            await conn.execute(text("PRAGMA foreign_keys=ON"))
        from models import Account, Order  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)

        # Migration: add stop_loss column to orders table if missing
        if _is_sqlite(config.DATABASE_URL):
            result = await conn.execute(text("PRAGMA table_info(orders)"))
            columns = [row[1] for row in result.fetchall()]
            if "stop_loss" not in columns:
                await conn.execute(text("ALTER TABLE orders ADD COLUMN stop_loss FLOAT DEFAULT 0"))
