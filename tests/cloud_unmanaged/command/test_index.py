from unittest.mock import patch

from cloud_index.aws import NoAggregatorIndexFoundError
from cloud_index.resource import Resource, ResourceType
from tests.cloud_unmanaged.conftest import RunCli


def test_main_index(run_cli: RunCli) -> None:
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
    with patch("cloud_unmanaged.command.index.index_aws", return_value=iter(resources)):
        result = run_cli("index")
        assert result.exit_code == 0
        assert "aws:s3:bucket" in result.stdout
        assert "us-east-bucket" in result.stdout
        assert "us-west-bucket" in result.stdout


def test_index_no_aggregator_region(run_cli: RunCli) -> None:
    with patch("cloud_unmanaged.command.index.index_aws", side_effect=NoAggregatorIndexFoundError()):
        result = run_cli("index")
        assert result.exit_code == 1
        assert "No aggregator index found" in result.stderr


def test_main_index_zero_resources(run_cli: RunCli) -> None:
    with patch("cloud_unmanaged.command.index.index_aws", return_value=iter([])):
        result = run_cli("index")
        assert result.exit_code == 0
        assert "No resources found" in result.stdout


def test_index_excludes_system_resources_by_default(run_cli: RunCli) -> None:
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
    with patch(
        "cloud_unmanaged.command.index.index_aws",
        return_value=iter([system_resource, non_system_resource]),
    ):
        result = run_cli("index")
    assert result.exit_code == 0
    assert "No resources found" not in result.stdout
    assert str(system_resource.type) not in result.stdout
    assert str(non_system_resource.type) in result.stdout


def test_index_includes_system_resources_with_include_system_flag(run_cli: RunCli) -> None:
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
    with patch(
        "cloud_unmanaged.command.index.index_aws",
        return_value=iter([system_resource, non_system_resource]),
    ):
        result = run_cli("index", "--include-system")
    assert result.exit_code == 0
    assert "No resources found" not in result.stdout
    assert str(system_resource.type) in result.stdout
    assert str(non_system_resource.type) in result.stdout


def test_index_filters_by_region(run_cli: RunCli) -> None:
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
    with patch(
        "cloud_unmanaged.command.index.index_aws",
        return_value=iter([us_east_resource, us_west_resource]),
    ):
        result = run_cli("index", "--region", "us-east-1")
    assert result.exit_code == 0
    assert "No resources found" not in result.stdout
    assert us_east_resource.identifier in result.stdout
    assert us_west_resource.identifier not in result.stdout


def test_index_region_filter_no_matches(run_cli: RunCli) -> None:
    resource = Resource(
        account="123456789012",
        region="us-east-1",
        type=ResourceType("aws", "s3", "bucket"),
        identifier="my-bucket",
        system=False,
    )
    with patch(
        "cloud_unmanaged.command.index.index_aws",
        return_value=iter([resource]),
    ):
        result = run_cli("index", "--region", "eu-west-1")
    assert result.exit_code == 0
    assert "No resources found" in result.stdout


def test_index_invalid_region(run_cli: RunCli) -> None:
    result = run_cli("index", "--region", "invalid-region-1")
    assert result.exit_code == 1
    assert "Invalid region: invalid-region-1" in result.stderr
