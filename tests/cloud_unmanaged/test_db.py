from os import environ
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError

from cloud_unmanaged.db import DatabaseError, get_db_dsn, get_db_path, init_db, transaction


def test_get_db_path_xdg_data_home(tmp_path: Path) -> None:
    with patch.dict(environ, {"XDG_DATA_HOME": str(tmp_path)}):
        actual = get_db_path()

    assert actual == tmp_path / "cloud-unmanaged/database.sqlite"
    assert actual.parent.is_dir()
    assert actual.parent.stat().st_mode & 0o777 == 0o700


def test_get_db_path_expands_user(tmp_path: Path) -> None:
    with patch.dict(environ, {"HOME": str(tmp_path), "XDG_DATA_HOME": "~/data"}):
        actual = get_db_path()

    assert actual == tmp_path / "data/cloud-unmanaged/database.sqlite"
    assert actual.parent.is_dir()


def test_get_db_path_xdg_data_home_unset(tmp_path: Path) -> None:
    with (
        patch.dict(environ, {}, clear=True),
        patch("cloud_unmanaged.db.Path.home", return_value=tmp_path),
    ):
        actual = get_db_path()

    assert actual == tmp_path / ".local/share/cloud-unmanaged/database.sqlite"
    assert actual.parent.is_dir()


def test_init_db(tmp_path: Path) -> None:
    with patch.dict(environ, {"XDG_DATA_HOME": str(tmp_path)}):
        assert get_db_dsn() == f"sqlite:///{tmp_path}/cloud-unmanaged/database.sqlite"

        engine = create_engine(get_db_dsn())
        try:
            init_db(engine)
            assert inspect(engine).get_table_names() == ["logical_resource", "physical_resource"]
        finally:
            engine.dispose()


def test_transaction_database_error() -> None:
    engine = create_engine("sqlite://")
    with (
        patch("cloud_unmanaged.db.create_engine", return_value=engine),
        patch("cloud_unmanaged.db.init_db", side_effect=SQLAlchemyError("write failed")),
        pytest.raises(DatabaseError, match="Unable to access resource database: write failed"),
        transaction(),
    ):
        pass


def test_transaction_database_path_error() -> None:
    with (
        patch("cloud_unmanaged.db.create_engine", side_effect=OSError("path failed")),
        pytest.raises(DatabaseError, match="Unable to access resource database: path failed"),
        transaction(),
    ):
        pass
