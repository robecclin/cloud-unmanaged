from cloud_index.error import CloudIndexError


class NoAggregatorIndexFoundError(CloudIndexError):
    def __init__(self) -> None:
        super().__init__("No aggregator index found - enable cross-region search in AWS Resource Explorer")


class AwsAccessError(CloudIndexError):
    pass
