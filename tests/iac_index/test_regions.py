from cloud_index.internal.aws.regions import get_available_regions, resolve_region


def test_get_available_regions() -> None:
    regions = get_available_regions()
    assert isinstance(regions, set)
    assert len(regions) > 0
    assert "us-east-1" in regions
    assert "us-west-2" in regions
    assert "eu-west-1" in regions
    assert "aws-global" in regions


def test_resolve_region() -> None:
    assert resolve_region("global") == "aws-global"
    assert resolve_region("us-east-1") == "us-east-1"
    assert resolve_region("eu-west-1") == "eu-west-1"
