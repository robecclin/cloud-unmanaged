from cloud_index.error import cloudIndexError


class NoAggregatorIndexFoundError(cloudIndexError):
    def __init__(self) -> None:
        super().__init__("No aggregator index found - enable cross-region search in AWS Resource Explorer")


class AwsAccessError(cloudIndexError):
    pass
