from cloud_index.aws.indexer import resolve_region


def test_resolve_region() -> None:
    assert resolve_region("global") == "aws-global"
    assert resolve_region("us-east-1") == "us-east-1"
    assert resolve_region("eu-west-1") == "eu-west-1"
