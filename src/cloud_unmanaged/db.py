from collections.abc import Generator
from contextlib import contextmanager
from os import environ
from pathlib import Path

from sqlalchemy import Boolean, Column, MetaData, Table, Text, UniqueConstraint, create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError

metadata = MetaData()

resource_table = Table(
    "resource",
    metadata,
    Column("account", Text(), nullable=False),
    Column("region", Text(), nullable=False),
    Column("cloud", Text(), nullable=False),
    Column("service", Text(), nullable=False),
    Column("type", Text(), nullable=False),
    Column("identifier", Text(), nullable=False),
    Column("system", Boolean(), nullable=False),
    UniqueConstraint("account", "region", "cloud", "service", "type", "identifier"),
)


class DatabaseError(Exception):
    pass


def get_db_path() -> Path:
    data_dir = (Path(environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "cloud-unmanaged").expanduser()
    data_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    return data_dir / "database.sqlite"


def get_db_dsn() -> str:
    return f"sqlite:///{get_db_path()}"


def init_db(engine: Engine) -> None:
    metadata.create_all(engine)


@contextmanager
def transaction() -> Generator[Connection]:
    try:
        engine = create_engine(get_db_dsn())
    except (OSError, SQLAlchemyError) as error:
        raise DatabaseError(f"Unable to access resource database: {error}") from error

    try:
        init_db(engine)
        with engine.begin() as connection:
            yield connection
    except (OSError, SQLAlchemyError) as error:
        raise DatabaseError(f"Unable to access resource database: {error}") from error
    finally:
        engine.dispose()
