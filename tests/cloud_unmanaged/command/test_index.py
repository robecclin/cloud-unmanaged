from collections.abc import Iterator
from io import StringIO
from unittest.mock import patch

from rich.console import Console
from rich.text import Text
from sqlalchemy import create_engine, select

from cloud_index.aws import NoAggregatorIndexFoundError
from cloud_index.progress import ProgressEvent, ProgressReporter
from cloud_index.resource import Resource, ResourceType
from cloud_unmanaged.db import DatabaseError, get_db_dsn, resource_table
from tests.cloud_unmanaged.conftest import RunCli


def saved_resource_ids() -> list[str]:
    engine = create_engine(get_db_dsn())
    try:
        with engine.connect() as connection:
            stmt = select(resource_table.c.identifier).order_by(resource_table.c.identifier)
            return list(connection.execute(stmt).scalars())
    finally:
        engine.dispose()


def test_index(run_cli: RunCli) -> None:
    resources = [
        Resource(
            account="123456789012",
            region="us-east-1",
            type=ResourceType("aws", "s3", "bucket"),
            identifier="us-east-bucket",
            system=False,
        ),
        Resource(
            account="123456789012",
            region="us-west-2",
            type=ResourceType("aws", "s3", "bucket"),
            identifier="us-west-bucket",
            system=False,
        ),
    ]
    progress_output = StringIO()
    progress_console = Console(file=progress_output, force_terminal=True, color_system=None)

    def index_with_progress(progress: ProgressReporter) -> list[Resource]:
        progress(ProgressEvent("Finding resources using Resource Explorer"))
        progress(ProgressEvent("Indexing resources", count=len(resources)))
        return resources

    with (
        patch("cloud_unmanaged.command.index.err_console", progress_console),
        patch("cloud_unmanaged.command.index.index_aws", side_effect=index_with_progress),
    ):
        result = run_cli("index")

    assert result.exit_code == 0
    assert Text.from_ansi(result.stdout).plain == "Indexed 2 resources\n"
    assert "Indexing resources (Found 2)" in progress_output.getvalue()
    assert saved_resource_ids() == ["us-east-bucket", "us-west-bucket"]

    result = run_cli("show")
    assert result.exit_code == 0
    assert "aws:s3:bucket" in result.stdout
    assert "us-east-bucket" in result.stdout
    assert "us-west-bucket" in result.stdout


def test_index_no_resources(run_cli: RunCli) -> None:
    with patch("cloud_unmanaged.command.index.index_aws", return_value=iter([])):
        result = run_cli("index")

    assert result.exit_code == 0
    assert Text.from_ansi(result.stdout).plain == "Indexed 0 resources\n"
    assert saved_resource_ids() == []


def test_index_existing_resources(run_cli: RunCli) -> None:
    previous_resource = Resource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="previous-bucket",
        system=False,
    )
    with patch("cloud_unmanaged.command.index.index_aws", return_value=iter([previous_resource])):
        run_cli("index")

    current_resource = Resource(
        account="123456789012",
        region="us-west-2",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="current-bucket",
        system=False,
    )
    with patch("cloud_unmanaged.command.index.index_aws", return_value=iter([current_resource])):
        result = run_cli("index")

    assert result.exit_code == 0
    assert saved_resource_ids() == ["current-bucket"]


def test_index_duplicate_resources(run_cli: RunCli) -> None:
    resource = Resource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="my-bucket",
        system=False,
    )
    with patch("cloud_unmanaged.command.index.index_aws", return_value=iter([resource, resource])):
        result = run_cli("index")

    assert result.exit_code == 0
    assert Text.from_ansi(result.stdout).plain == "Indexed 1 resource\n"
    assert saved_resource_ids() == ["my-bucket"]


def test_index_error_after_resource(run_cli: RunCli) -> None:
    previous_resource = Resource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="previous-bucket",
        system=False,
    )
    with patch("cloud_unmanaged.command.index.index_aws", return_value=iter([previous_resource])):
        run_cli("index")

    new_resource = Resource(
        account="123456789012",
        region="us-west-2",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="new-bucket",
        system=False,
    )

    def fail_after_resource(progress: ProgressReporter) -> Iterator[Resource]:
        yield new_resource
        raise NoAggregatorIndexFoundError()

    with patch("cloud_unmanaged.command.index.index_aws", side_effect=fail_after_resource):
        result = run_cli("index")

    assert result.exit_code == 1
    assert saved_resource_ids() == ["previous-bucket"]


def test_index_no_aggregator_region(run_cli: RunCli) -> None:
    def fail_after_progress(progress: ProgressReporter) -> list[Resource]:
        progress(ProgressEvent("Finding resources using Resource Explorer"))
        raise NoAggregatorIndexFoundError()

    with patch("cloud_unmanaged.command.index.index_aws", side_effect=fail_after_progress):
        result = run_cli("index")

    assert result.exit_code == 1
    assert "No aggregator index found" in result.stderr
    assert "Finding resources" not in result.stderr


def test_index_database_error(run_cli: RunCli) -> None:
    with patch(
        "cloud_unmanaged.command.index.transaction",
        side_effect=DatabaseError("Unable to access resource database"),
    ):
        result = run_cli("index")

    assert result.exit_code == 1
    assert "Unable to access resource database" in result.stderr
