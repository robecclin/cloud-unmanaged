from unittest.mock import patch

from cloud_index.resource import LogicalResource, PhysicalResource, ResourceType
from cloud_unmanaged.db import DatabaseError
from tests.cloud_unmanaged.conftest import RunCli, store


def logical_resource(identifier: str, region: str = "us-east-1") -> LogicalResource:
    return LogicalResource(
        account="123456789012",
        region=region,
        type=ResourceType("aws", "s3", "bucket"),
        identifier=identifier,
        locator=f"arn:aws:cloudformation:{region}:123456789012:stack/MyStack/stack-id",
        name=f"{identifier.title()}Bucket",
    )


def test_show_missing(run_cli: RunCli) -> None:
    missing_resource = logical_resource("missing")
    matched_resource = logical_resource("matched")
    system_resource = logical_resource("system")
    store(
        missing_resource,
        matched_resource,
        system_resource,
        PhysicalResource(
            account=matched_resource.account,
            region=matched_resource.region,
            type=matched_resource.type,
            identifier=matched_resource.identifier,
            system=False,
        ),
        PhysicalResource(
            account=system_resource.account,
            region=system_resource.region,
            type=system_resource.type,
            identifier=system_resource.identifier,
            system=True,
        ),
    )

    result = run_cli("show-missing")

    assert result.exit_code == 0
    assert "No resources found" not in result.stdout
    for column in ("Account", "Region", "Type", "ID", "Locator", "Name"):
        assert column in result.stdout
    assert missing_resource.account in result.stdout
    assert missing_resource.region in result.stdout
    assert str(missing_resource.type) in result.stdout
    assert missing_resource.identifier in result.stdout
    assert missing_resource.locator in result.stdout
    assert missing_resource.name in result.stdout
    assert matched_resource.identifier not in result.stdout
    assert system_resource.identifier not in result.stdout


def test_show_missing_region(run_cli: RunCli) -> None:
    us_east_resource = logical_resource("east", region="us-east-1")
    us_west_resource = logical_resource("west", region="us-west-2")
    store(us_east_resource, us_west_resource)

    result = run_cli("show-missing", "--region", "us-east-1")

    assert result.exit_code == 0
    assert us_east_resource.identifier in result.stdout
    assert us_west_resource.identifier not in result.stdout


def test_show_missing_order(run_cli: RunCli) -> None:
    second_resource = logical_resource("second", region="us-west-2")
    first_resource = logical_resource("first", region="us-east-1")
    store(second_resource, first_resource)

    result = run_cli("show-missing")

    assert result.exit_code == 0
    assert result.stdout.index(first_resource.identifier) < result.stdout.index(second_resource.identifier)


def test_show_missing_region_no_matches(run_cli: RunCli) -> None:
    store(logical_resource("missing"))

    result = run_cli("show-missing", "--region", "eu-west-1")

    assert result.exit_code == 0
    assert "No resources found" in result.stdout


def test_show_missing_invalid_region(run_cli: RunCli) -> None:
    result = run_cli("show-missing", "--region", "invalid-region-1")

    assert result.exit_code == 1
    assert "Invalid region: invalid-region-1" in result.stderr


def test_show_missing_database_error(run_cli: RunCli) -> None:
    with patch(
        "cloud_unmanaged.command.show_missing.transaction",
        side_effect=DatabaseError("Unable to access resource database"),
    ):
        result = run_cli("show-missing")

    assert result.exit_code == 1
    assert "Unable to access resource database" in result.stderr
