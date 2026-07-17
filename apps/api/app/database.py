from functools import lru_cache

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models.base import Base

metadata = Base.metadata


@lru_cache
def create_database_engine() -> Engine | None:
    settings = get_settings()
    database_url = settings.database_url
    if settings.uses_local_demo_database:
        database_url = settings.local_demo_database_url
    if not database_url:
        return None

    if database_url.startswith("sqlite"):
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(engine, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine

    connect_args = {}
    if "neon.tech" in database_url and "sslmode=" not in database_url:
        connect_args["sslmode"] = "require"

    return create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)


@lru_cache
def create_session_factory() -> sessionmaker[Session] | None:
    engine = create_database_engine()
    if engine is None:
        return None

    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
