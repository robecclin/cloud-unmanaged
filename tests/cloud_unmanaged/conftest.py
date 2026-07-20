from collections.abc import Iterator
from os import environ
from pathlib import Path
from typing import Protocol
from unittest.mock import patch
from uuid import UUID

import pytest
from typer.testing import CliRunner, Result

from cloud_index.resource import LogicalResource, PhysicalResource
from cloud_unmanaged.db import transaction
from cloud_unmanaged.main import app
from cloud_unmanaged.repository import end_index_run, save, start_index_run


class RunCli(Protocol):
    def __call__(self, *args: str) -> Result: ...


def store(*resources: PhysicalResource | LogicalResource) -> UUID:
    with transaction() as connection:
        index_run_id = start_index_run(connection)
        for resource in resources:
            save(connection, index_run_id, resource)
        end_index_run(connection, index_run_id)
    return index_run_id


@pytest.fixture
def run_cli(tmp_path: Path) -> Iterator[RunCli]:
    runner = CliRunner()

    def run(*args: str) -> Result:
        return runner.invoke(app, list(args), env={"COLUMNS": "240"})

    with patch.dict(environ, {"XDG_DATA_HOME": str(tmp_path)}):
        yield run
