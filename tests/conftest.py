from typing import Protocol

import pytest
from typer.testing import CliRunner, Result

from cloud_unmanaged.main import app


class RunCli(Protocol):
    def __call__(self, *args: str) -> Result: ...


@pytest.fixture
def run_cli() -> RunCli:
    runner = CliRunner()

    def _run(*args: str) -> Result:
        return runner.invoke(app, list(args))

    return _run
