from collections.abc import Iterator
from os import environ
from pathlib import Path
from typing import Protocol
from unittest.mock import patch

import pytest
from typer.testing import CliRunner, Result

from cloud_unmanaged.main import app


class RunCli(Protocol):
    def __call__(self, *args: str) -> Result: ...


@pytest.fixture
def run_cli(tmp_path: Path) -> Iterator[RunCli]:
    runner = CliRunner()

    def run(*args: str) -> Result:
        return runner.invoke(app, list(args))

    with patch.dict(environ, {"XDG_DATA_HOME": str(tmp_path)}):
        yield run
