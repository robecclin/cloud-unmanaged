from collections.abc import Generator
from contextlib import contextmanager
from os import environ
from pathlib import Path

from sqlalchemy import UUID, Boolean, Column, MetaData, Table, Text, UniqueConstraint, create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError

metadata = MetaData()

index_run_table = Table(
    "index_run",
    metadata,
    Column("id", UUID(), nullable=False, primary_key=True),
    Column("started_at", Text(), nullable=False),
    Column("ended_at", Text(), nullable=True),
)

physical_resource_table = Table(
    "physical_resource",
    metadata,
    Column("index_run_id", UUID(), nullable=False),
    Column("account", Text(), nullable=False),
    Column("region", Text(), nullable=False),
    Column("cloud", Text(), nullable=False),
    Column("service", Text(), nullable=False),
    Column("type", Text(), nullable=False),
    Column("identifier", Text(), nullable=False),
    Column("system", Boolean(), nullable=False),
    UniqueConstraint("index_run_id", "account", "region", "cloud", "service", "type", "identifier"),
)

logical_resource_table = Table(
    "logical_resource",
    metadata,
    Column("index_run_id", UUID(), nullable=False),
    Column("account", Text(), nullable=False),
    Column("region", Text(), nullable=False),
    Column("cloud", Text(), nullable=False),
    Column("service", Text(), nullable=False),
    Column("type", Text(), nullable=False),
    Column("identifier", Text(), nullable=False),
    Column("locator", Text(), nullable=False),
    Column("name", Text(), nullable=False),
    UniqueConstraint("index_run_id", "locator", "name"),
)


class DatabaseError(Exception):
    pass


def get_db_path() -> Path:
    data_dir = (Path(environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "cloud-unmanaged").expanduser()
    data_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    db_path = data_dir / "database.sqlite"
    db_path.touch(mode=0o600, exist_ok=True)
    return db_path


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
