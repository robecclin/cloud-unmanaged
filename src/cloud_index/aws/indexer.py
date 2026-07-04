from collections.abc import Generator

from cloud_index.progress import ProgressEvent, ProgressReporter
from cloud_index.resource import Resource

from .arn import parse_arn
from .client import create_session, get_aggregator_region, get_resources
from .regions import resolve_region
from .resource_type import parse_resource_type
from .system_resource import is_system_resource


def index(progress: ProgressReporter = lambda _: None) -> Generator[Resource]:
    session = create_session()
    progress(ProgressEvent("Finding Resource Explorer aggregator index"))
    aggregator_region = get_aggregator_region(session)
    progress(ProgressEvent("Finding resources using Resource Explorer"))
    for n, aws_resource in enumerate(get_resources(session, aggregator_region), start=1):
        arn = parse_arn(aws_resource.arn)
        resource_type = parse_resource_type(aws_resource.type)
        region = resolve_region(aws_resource.region)
        resource = Resource(
            account=aws_resource.account_id,
            region=region,
            type=resource_type,
            identifier=arn.resource_id,
            system=is_system_resource(session, resource_type, region, arn.resource_id, progress),
        )
        progress(ProgressEvent("Indexing resources", count=n))
        yield resource
