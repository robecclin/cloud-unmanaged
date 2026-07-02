from cloud_index.resource import ResourceType


def test_resource_type_str() -> None:
    assert str(ResourceType("aws", "s3", "bucket")) == "aws:s3:bucket"
