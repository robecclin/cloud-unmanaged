from cloud_index.aws.indexer import resolve_region
from cloud_index.resource import ResourceType


def test_resolve_region() -> None:
    assert resolve_region(ResourceType("aws", "s3", "bucket"), "global") == "aws-global"
    assert resolve_region(ResourceType("aws", "cloudfront", "distribution"), "us-east-1") == "aws-global"
    assert resolve_region(ResourceType("aws", "cloudwatch", "alarm"), "us-east-1") == "us-east-1"
    assert resolve_region(ResourceType("aws", "cloudwatch", "dashboard"), "us-east-1") == "aws-global"
    assert resolve_region(ResourceType("aws", "iam", "role"), "us-east-1") == "aws-global"
    assert resolve_region(ResourceType("aws", "s3", "bucket"), "eu-west-1") == "eu-west-1"
