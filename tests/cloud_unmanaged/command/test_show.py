from unittest.mock import patch

from cloud_index.resource import LogicalResource, PhysicalResource, ResourceType
from cloud_unmanaged.db import DatabaseError
from tests.cloud_unmanaged.conftest import RunCli, store


def test_show(run_cli: RunCli) -> None:
    system_resource = PhysicalResource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "iam", "role"),
        identifier="aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS",
        system=True,
    )
    non_system_resource = PhysicalResource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="my-bucket",
        system=False,
    )
    store(system_resource, non_system_resource)

    result = run_cli("show")

    assert result.exit_code == 0
    assert "No resources found" not in result.stdout
    assert str(system_resource.type) not in result.stdout
    assert str(non_system_resource.type) in result.stdout


def test_show_include_system(run_cli: RunCli) -> None:
    system_resource = PhysicalResource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "iam", "role"),
        identifier="aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS",
        system=True,
    )
    non_system_resource = PhysicalResource(
        account="123456789012",
        region="us-west-2",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="my-bucket",
        system=False,
    )
    store(system_resource, non_system_resource)

    result = run_cli("show", "--include-system")

    assert result.exit_code == 0
    assert str(system_resource.type) in result.stdout
    assert str(non_system_resource.type) in result.stdout


def test_show_region(run_cli: RunCli) -> None:
    us_east_resource = PhysicalResource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="us-east-bucket",
        system=False,
    )
    us_west_resource = PhysicalResource(
        account="123456789012",
        region="us-west-2",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="us-west-bucket",
        system=False,
    )
    store(us_east_resource, us_west_resource)

    result = run_cli("show", "--region", "us-east-1")

    assert result.exit_code == 0
    assert us_east_resource.identifier in result.stdout
    assert us_west_resource.identifier not in result.stdout


def test_show_unmanaged(run_cli: RunCli) -> None:
    managed_resource = PhysicalResource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="matched-bucket",
        system=False,
    )
    unmanaged_resource = PhysicalResource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="loose-bucket",
        system=False,
    )
    store(
        managed_resource,
        unmanaged_resource,
        LogicalResource(
            account=managed_resource.account,
            region=managed_resource.region,
            type=managed_resource.type,
            identifier=managed_resource.identifier,
            locator="arn:aws:cloudformation:us-east-1:123456789012:stack/MyStack/managed",
            name="MatchedBucket",
        ),
        LogicalResource(
            account=unmanaged_resource.account,
            region="us-west-2",
            type=unmanaged_resource.type,
            identifier=unmanaged_resource.identifier,
            locator="arn:aws:cloudformation:us-west-2:123456789012:stack/MyStack/unmanaged",
            name="LooseBucket",
        ),
    )

    result = run_cli("show", "--unmanaged")

    assert result.exit_code == 0
    assert unmanaged_resource.identifier in result.stdout
    assert managed_resource.identifier not in result.stdout


def test_show_managed(run_cli: RunCli) -> None:
    managed_resource = PhysicalResource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="matched-bucket",
        system=False,
    )
    unmanaged_resource = PhysicalResource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="loose-bucket",
        system=False,
    )
    store(
        managed_resource,
        unmanaged_resource,
        LogicalResource(
            account=managed_resource.account,
            region=managed_resource.region,
            type=managed_resource.type,
            identifier=managed_resource.identifier,
            locator="arn:aws:cloudformation:us-east-1:123456789012:stack/MyStack/managed",
            name="MatchedBucket",
        ),
        LogicalResource(
            account=unmanaged_resource.account,
            region=unmanaged_resource.region,
            type=ResourceType("aws", "sqs", "queue"),
            identifier=unmanaged_resource.identifier,
            locator="arn:aws:cloudformation:us-east-1:123456789012:stack/MyStack/unmanaged",
            name="LooseQueue",
        ),
    )

    result = run_cli("show", "--managed")

    assert result.exit_code == 0
    assert managed_resource.identifier in result.stdout
    assert unmanaged_resource.identifier not in result.stdout


def test_show_order(run_cli: RunCli) -> None:
    second_resource = PhysicalResource(
        account="123456789012",
        region="us-west-2",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="second",
        system=False,
    )
    first_resource = PhysicalResource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="first",
        system=False,
    )
    store(second_resource, first_resource)

    result = run_cli("show")

    assert result.exit_code == 0
    assert result.stdout.index(first_resource.identifier) < result.stdout.index(second_resource.identifier)


def test_show_region_no_matches(run_cli: RunCli) -> None:
    store(
        PhysicalResource(
            account="123456789012",
            region="us-east-1",
            type=ResourceType("aws", "s3", "bucket"),
            identifier="my-bucket",
            system=False,
        )
    )

    result = run_cli("show", "--region", "eu-west-1")

    assert result.exit_code == 0
    assert "No resources found" in result.stdout


def test_show_invalid_region(run_cli: RunCli) -> None:
    result = run_cli("show", "--region", "invalid-region-1")

    assert result.exit_code == 1
    assert "Invalid region: invalid-region-1" in result.stderr


def test_show_conflicting_management_filters(run_cli: RunCli) -> None:
    result = run_cli("show", "--managed", "--unmanaged")

    assert result.exit_code == 1
    assert "--managed and --unmanaged cannot be used together" in result.stderr


def test_show_database_error(run_cli: RunCli) -> None:
    with patch(
        "cloud_unmanaged.command.show.transaction",
        side_effect=DatabaseError("Unable to access resource database"),
    ):
        result = run_cli("show")

    assert result.exit_code == 1
    assert "Unable to access resource database" in result.stderr
