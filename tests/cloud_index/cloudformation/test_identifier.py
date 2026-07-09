import pytest

from cloud_index.cloudformation.identifier import parse_identifier
from cloud_index.resource import ResourceType


@pytest.mark.parametrize(
    "resource_type,physical_id,expected",
    [
        (ResourceType("aws", "dynamodb", "table"), "MyTable", "MyTable"),
        (ResourceType("aws", "ec2", "security-group-rule"), "MyIngress", None),
        (ResourceType("aws", "ec2", "security-group-rule"), "sgr-04d366fdc35a0a4b3", "sgr-04d366fdc35a0a4b3"),
        (ResourceType("aws", "cloudformation", "custom-resource"), "arn:my-resource", "arn:my-resource"),
        (ResourceType("aws", "ec2", "vpc"), "vpc-0e19a7a49b325abc2", "vpc-0e19a7a49b325abc2"),
        (ResourceType("aws", "sns", "topic"), "arn:aws:sns:us-east-1:123456789012:MyTopic", "MyTopic"),
        (ResourceType("aws", "sqs", "queue"), "https://sqs.us-east-1.amazonaws.com/123456789012/MyQueue", "MyQueue"),
        (ResourceType("aws", "ssm", "parameter"), "my-param", "my-param"),
        (ResourceType("aws", "ssm", "parameter"), "/my-param", "my-param"),
        (ResourceType("aws", "ssm", "parameter"), "/parent/child", "/parent/child"),
    ],
)
def test_parse_identifier(resource_type: ResourceType, physical_id: str, expected: str | None) -> None:
    assert parse_identifier(resource_type, physical_id) == expected
