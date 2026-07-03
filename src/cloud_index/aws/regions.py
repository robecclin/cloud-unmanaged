from botocore.session import Session


def get_available_regions() -> set[str]:
    loader = Session().get_component("data_loader")
    partitions = loader.load_data("partitions")
    regions: set[str] = set()
    for partition in partitions["partitions"]:
        regions.update(partition["regions"])
    return regions


def resolve_region(region: str) -> str:
    if region == "global":
        return "aws-global"
    return region
