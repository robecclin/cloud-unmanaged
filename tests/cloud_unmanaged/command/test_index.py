from collections.abc import Iterator
from io import StringIO
from unittest.mock import patch

from rich.console import Console
from rich.text import Text
from sqlalchemy import create_engine, select

from cloud_index.aws import NoAggregatorIndexFoundError
from cloud_index.progress import ProgressEvent, ProgressReporter
from cloud_index.resource import LogicalResource, PhysicalResource, ResourceType
from cloud_unmanaged.db import DatabaseError, get_db_dsn, logical_resource_table, physical_resource_table
from tests.cloud_unmanaged.conftest import RunCli


def physical_resource(identifier: str, region: str = "us-east-1") -> PhysicalResource:
    return PhysicalResource(
        account="123456789012",
        region=region,
        type=ResourceType("aws", "s3", "bucket"),
        identifier=identifier,
        system=False,
    )


def logical_resource(name: str, region: str = "us-east-1") -> LogicalResource:
    return LogicalResource(
        account="123456789012",
        region=region,
        type=ResourceType("aws", "s3", "bucket"),
        identifier=name.lower(),
        locator="arn:aws:cloudformation:us-east-1:123456789012:stack/MyStack/9264fd82-c31b-49e9-b4a5-a7b6a6b984b3",
        name=name,
    )


def saved_physical_resource_ids() -> list[str]:
    engine = create_engine(get_db_dsn())
    try:
        with engine.connect() as connection:
            stmt = select(physical_resource_table.c.identifier).order_by(physical_resource_table.c.identifier)
            return list(connection.execute(stmt).scalars())
    finally:
        engine.dispose()


def saved_logical_resource_names() -> list[str]:
    engine = create_engine(get_db_dsn())
    try:
        with engine.connect() as connection:
            stmt = select(logical_resource_table.c.name).order_by(logical_resource_table.c.name)
            return list(connection.execute(stmt).scalars())
    finally:
        engine.dispose()


def test_index(run_cli: RunCli) -> None:
    resources = [
        physical_resource("us-east-bucket"),
        physical_resource("us-west-bucket", region="us-west-2"),
    ]
    logical_resources = [
        logical_resource("MyTable"),
        logical_resource("MyQueue"),
    ]
    progress_output = StringIO()
    progress_console = Console(file=progress_output, force_terminal=True, color_system=None)

    def index_with_progress(progress: ProgressReporter) -> list[PhysicalResource]:
        progress(ProgressEvent("Finding resources using Resource Explorer"))
        progress(ProgressEvent("Indexing resources"))
        return resources

    with (
        patch("cloud_unmanaged.command.index.err_console", progress_console),
        patch("cloud_unmanaged.command.index.index_aws", side_effect=index_with_progress),
        patch("cloud_unmanaged.command.index.index_cloudformation", return_value=iter(logical_resources)),
    ):
        result = run_cli("index")

    assert result.exit_code == 0
    assert Text.from_ansi(result.stdout).plain == "Indexed 4 resources (2 physical, 2 logical)\n"
    assert "Indexing resources (Found 4)" in progress_output.getvalue()
    assert saved_physical_resource_ids() == ["us-east-bucket", "us-west-bucket"]
    assert saved_logical_resource_names() == ["MyQueue", "MyTable"]

    result = run_cli("show")
    assert result.exit_code == 0
    assert "aws:s3:bucket" in result.stdout
    assert "us-east-bucket" in result.stdout
    assert "us-west-bucket" in result.stdout


def test_index_no_resources(run_cli: RunCli) -> None:
    with (
        patch("cloud_unmanaged.command.index.index_aws", return_value=iter([])),
        patch("cloud_unmanaged.command.index.index_cloudformation", return_value=iter([])),
    ):
        result = run_cli("index")

    assert result.exit_code == 0
    assert Text.from_ansi(result.stdout).plain == "Indexed 0 resources (0 physical, 0 logical)\n"
    assert saved_physical_resource_ids() == []
    assert saved_logical_resource_names() == []


def test_index_existing_resources(run_cli: RunCli) -> None:
    with (
        patch("cloud_unmanaged.command.index.index_aws", return_value=iter([physical_resource("previous-bucket")])),
        patch(
            "cloud_unmanaged.command.index.index_cloudformation",
            return_value=iter([logical_resource("PreviousBucket")]),
        ),
    ):
        run_cli("index")

    with (
        patch("cloud_unmanaged.command.index.index_aws", return_value=iter([physical_resource("current-bucket")])),
        patch(
            "cloud_unmanaged.command.index.index_cloudformation",
            return_value=iter([logical_resource("CurrentBucket")]),
        ),
    ):
        result = run_cli("index")

    assert result.exit_code == 0
    assert saved_physical_resource_ids() == ["current-bucket"]
    assert saved_logical_resource_names() == ["CurrentBucket"]


def test_index_duplicate_resources(run_cli: RunCli) -> None:
    resource = physical_resource("my-bucket")
    duplicate_logical_resource = logical_resource("MyBucket")
    with (
        patch("cloud_unmanaged.command.index.index_aws", return_value=iter([resource, resource])),
        patch(
            "cloud_unmanaged.command.index.index_cloudformation",
            return_value=iter([duplicate_logical_resource, duplicate_logical_resource]),
        ),
    ):
        result = run_cli("index")

    assert result.exit_code == 0
    assert Text.from_ansi(result.stdout).plain == "Indexed 2 resources (1 physical, 1 logical)\n"
    assert saved_physical_resource_ids() == ["my-bucket"]
    assert saved_logical_resource_names() == ["MyBucket"]


def test_index_error_after_resource(run_cli: RunCli) -> None:
    with (
        patch("cloud_unmanaged.command.index.index_aws", return_value=iter([physical_resource("previous-bucket")])),
        patch(
            "cloud_unmanaged.command.index.index_cloudformation",
            return_value=iter([logical_resource("PreviousBucket")]),
        ),
    ):
        run_cli("index")

    def fail_after_resource(progress: ProgressReporter) -> Iterator[LogicalResource]:
        yield logical_resource("NewBucket")
        raise NoAggregatorIndexFoundError()

    with (
        patch("cloud_unmanaged.command.index.index_aws", return_value=iter([physical_resource("new-bucket")])),
        patch("cloud_unmanaged.command.index.index_cloudformation", side_effect=fail_after_resource),
    ):
        result = run_cli("index")

    assert result.exit_code == 1
    assert saved_physical_resource_ids() == ["previous-bucket"]
    assert saved_logical_resource_names() == ["PreviousBucket"]


def test_index_database_error(run_cli: RunCli) -> None:
    with patch(
        "cloud_unmanaged.command.index.transaction",
        side_effect=DatabaseError("Unable to access resource database"),
    ):
        result = run_cli("index")

    assert result.exit_code == 1
    assert "Unable to access resource database" in result.stderr


def test_index_no_aggregator_region(run_cli: RunCli) -> None:
    def fail_after_progress(progress: ProgressReporter) -> list[PhysicalResource]:
        progress(ProgressEvent("Finding resources using Resource Explorer"))
        raise NoAggregatorIndexFoundError()

    with patch("cloud_unmanaged.command.index.index_aws", side_effect=fail_after_progress):
        result = run_cli("index")

    assert result.exit_code == 1
    assert "No aggregator index found" in result.stderr
    assert "Finding resources" not in result.stderr
