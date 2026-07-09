import pytest

from cloud_index.aws.identifier import parse_identifier
from cloud_index.resource import ResourceType


@pytest.mark.parametrize(
    "resource_type,resource_id,expected",
    [
        (ResourceType("aws", "dynamodb", "table"), "MyTable", "MyTable"),
        (ResourceType("aws", "ssm", "parameter"), "my-param", "my-param"),
        (ResourceType("aws", "ssm", "parameter"), "parent/child", "/parent/child"),
        (
            ResourceType("aws", "autoscaling", "auto-scaling-group"),
            "0206294a-4ae8-481d-87bf-4cce402ac008:autoScalingGroupName/my-group",
            "my-group",
        ),
    ],
)
def test_parse_identifier(resource_type: ResourceType, resource_id: str, expected: str) -> None:
    assert parse_identifier(resource_type, resource_id) == expected
