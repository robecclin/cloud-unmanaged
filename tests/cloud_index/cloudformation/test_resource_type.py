import pytest

from cloud_index.cloudformation.resource_type import parse_resource_type
from cloud_index.resource import ResourceType


@pytest.mark.parametrize(
    "resource_type,expected",
    [
        ("AWS::EC2::VPC", ResourceType("aws", "ec2", "vpc")),
        ("AWS::IAM::ManagedPolicy", ResourceType("aws", "iam", "managed-policy")),
        ("AWS::Logs::LogGroup", ResourceType("aws", "logs", "log-group")),
        ("AWS::RDS::DBInstance", ResourceType("aws", "rds", "db-instance")),
        ("AWS::S3::Bucket", ResourceType("aws", "s3", "bucket")),
    ],
)
def test_parse_resource_type(resource_type: str, expected: ResourceType) -> None:
    assert parse_resource_type(resource_type) == expected


@pytest.mark.parametrize(
    "resource_type,expected",
    [
        ("AWS::Athena::WorkGroup", ResourceType("aws", "athena", "workgroup")),
        (
            "AWS::CloudFront::CloudFrontOriginAccessIdentity",
            ResourceType("aws", "cloudfront", "origin-access-identity"),
        ),
        ("AWS::EC2::EIP", ResourceType("aws", "ec2", "elastic-ip")),
        ("AWS::EC2::EIPAssociation", ResourceType("aws", "ec2", "elastic-ip-association")),
        ("AWS::EC2::SecurityGroupEgress", ResourceType("aws", "ec2", "security-group-rule")),
        ("AWS::EC2::SecurityGroupIngress", ResourceType("aws", "ec2", "security-group-rule")),
    ],
)
def test_parse_resource_type_canonical_type(resource_type: str, expected: ResourceType) -> None:
    assert parse_resource_type(resource_type) == expected


@pytest.mark.parametrize(
    "resource_type,expected",
    [
        ("AWS::Elasticsearch::Domain", ResourceType("aws", "opensearchservice", "domain")),
        ("AWS::KinesisFirehose::DeliveryStream", ResourceType("aws", "firehose", "delivery-stream")),
    ],
)
def test_parse_resource_type_renamed_service(resource_type: str, expected: ResourceType) -> None:
    assert parse_resource_type(resource_type) == expected


@pytest.mark.parametrize(
    "resource_type",
    [
        "Alexa::ASK::Skill",
        "AWS::CloudFormation",
        "AWS::CloudFormation::Stack::Extra",
        "Custom::Widget",
    ],
)
def test_parse_resource_type_unsupported(resource_type: str) -> None:
    assert parse_resource_type(resource_type) is None
