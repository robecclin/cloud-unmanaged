import pytest

from cloud_index.aws.arn import parse_arn
from cloud_index.aws.identifier import parse_identifier as parse_physical_identifier
from cloud_index.cloudformation.identifier import parse_identifier as parse_logical_identifier
from cloud_index.resource import ResourceType


@pytest.mark.parametrize(
    "resource_type,physical_id,arn",
    [
        (
            ResourceType("aws", "autoscaling", "auto-scaling-group"),
            "my-group",
            "arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:0206294a-4ae8-481d-87bf-4cce402ac008:autoScalingGroupName/my-group",
        ),
        (
            ResourceType("aws", "ssm", "parameter"),
            "my-param",
            "arn:aws:ssm:us-east-1:123456789012:parameter/my-param",
        ),
        (
            ResourceType("aws", "ssm", "parameter"),
            "/my-param",
            "arn:aws:ssm:us-east-1:123456789012:parameter/my-param",
        ),
        (
            ResourceType("aws", "ssm", "parameter"),
            "/parent/child",
            "arn:aws:ssm:us-east-1:123456789012:parameter/parent/child",
        ),
        (
            ResourceType("aws", "sqs", "queue"),
            "https://sqs.us-east-1.amazonaws.com/123456789012/MyQueue",
            "arn:aws:sqs:us-east-1:123456789012:MyQueue",
        ),
    ],
)
def test_identifier_convergence(resource_type: ResourceType, physical_id: str, arn: str) -> None:
    physical_identifier = parse_physical_identifier(resource_type, parse_arn(arn).resource_id)
    assert parse_logical_identifier(resource_type, physical_id) == physical_identifier
