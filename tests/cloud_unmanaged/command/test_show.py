from unittest.mock import patch

from cloud_index.resource import Resource, ResourceType
from cloud_unmanaged.db import DatabaseError, transaction
from cloud_unmanaged.repository import save
from tests.cloud_unmanaged.conftest import RunCli


def store(*resources: Resource) -> None:
    with transaction() as connection:
        for resource in resources:
            save(connection, resource)


def test_show(run_cli: RunCli) -> None:
    system_resource = Resource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "iam", "role"),
        identifier="aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS",
        system=True,
    )
    non_system_resource = Resource(
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
    system_resource = Resource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "iam", "role"),
        identifier="aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS",
        system=True,
    )
    non_system_resource = Resource(
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
    us_east_resource = Resource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="us-east-bucket",
        system=False,
    )
    us_west_resource = Resource(
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


def test_show_order(run_cli: RunCli) -> None:
    second_resource = Resource(
        account="123456789012",
        region="us-west-2",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="second",
        system=False,
    )
    first_resource = Resource(
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
        Resource(
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


def test_show_database_error(run_cli: RunCli) -> None:
    with patch(
        "cloud_unmanaged.command.show.transaction",
        side_effect=DatabaseError("Unable to access resource database"),
    ):
        result = run_cli("show")

    assert result.exit_code == 1
    assert "Unable to access resource database" in result.stderr
