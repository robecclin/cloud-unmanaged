import pytest

from cloud_index.internal.aws.resource_type import parse_resource_type
from cloud_index.resource import ResourceType


@pytest.mark.parametrize(
    "resource_type,expected",
    [
        ("dynamodb:table", ResourceType("aws", "dynamodb", "table")),
        ("resource-explorer-2:index", ResourceType("aws", "resource-explorer-2", "index")),
        ("s3:bucket", ResourceType("aws", "s3", "bucket")),
    ],
)
def test_parse_resource_type(resource_type: str, expected: ResourceType) -> None:
    assert parse_resource_type(resource_type) == expected
