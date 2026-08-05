from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from instagram_agent.config import Settings
from instagram_agent.models import Base


def make_engine(settings: Settings):  # type: ignore[no-untyped-def]
    connect_args = (
        {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    )
    return create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)


def create_schema(settings: Settings) -> None:
    Base.metadata.create_all(make_engine(settings))


def session_scope(settings: Settings) -> Iterator[Session]:
    factory = sessionmaker(bind=make_engine(settings), expire_on_commit=False)
    with factory.begin() as session:
        yield session
