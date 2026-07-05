from unittest.mock import patch

from tests.cloud_unmanaged.conftest import RunCli


def test_main(run_cli: RunCli) -> None:
    with patch("cloud_unmanaged.command.index.index_aws", return_value=iter([])):
        result = run_cli("index")
    assert result.exit_code == 0
    assert result.stderr == ""


def test_main_no_subcommand(run_cli: RunCli) -> None:
    result = run_cli()
    assert result.exit_code == 2
    assert "Usage:" in result.stdout
    assert "index" in result.stdout
    assert "show" in result.stdout
    assert result.stderr == ""


def test_main_unknown_subcommand(run_cli: RunCli) -> None:
    result = run_cli("unknown")
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "No such command 'unknown'." in result.stderr


def test_main_help(run_cli: RunCli) -> None:
    result = run_cli("--help")
    assert result.exit_code == 0
    assert "index" in result.stdout
    assert "show" in result.stdout
    assert result.stderr == ""
