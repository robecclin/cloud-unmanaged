from collections.abc import Generator

from cloud_index.progress import ProgressEvent, ProgressReporter
from cloud_index.resource import PhysicalResource

from .arn import parse_arn
from .client import create_session, get_aggregator_region, get_resources
from .resource_type import parse_resource_type
from .system_resource import is_system_resource


def index(progress: ProgressReporter = lambda _: None) -> Generator[PhysicalResource]:
    session = create_session()
    progress(ProgressEvent("Finding Resource Explorer aggregator index"))
    aggregator_region = get_aggregator_region(session)
    progress(ProgressEvent("Finding resources using Resource Explorer"))
    for aws_resource in get_resources(session, aggregator_region):
        arn = parse_arn(aws_resource.arn)
        resource_type = parse_resource_type(aws_resource.type)
        region = resolve_region(aws_resource.region)
        resource = PhysicalResource(
            account=aws_resource.account_id,
            region=region,
            type=resource_type,
            identifier=arn.resource_id,
            system=is_system_resource(session, resource_type, region, arn.resource_id, progress),
        )
        progress(ProgressEvent("Indexing resources"))
        yield resource


def resolve_region(region: str) -> str:
    if region == "global":
        return "aws-global"
    return region
