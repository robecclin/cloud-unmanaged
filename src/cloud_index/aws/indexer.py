from collections.abc import Generator

from cloud_index.progress import ProgressEvent, ProgressReporter
from cloud_index.resource import PhysicalResource, ResourceType

from .arn import parse_arn
from .client import create_session, get_aggregator_region, get_resources
from .identifier import parse_identifier
from .resource_type import parse_resource_type
from .system_resource import is_system_resource

GLOBAL_REGION = "aws-global"


def index(progress: ProgressReporter = lambda _: None) -> Generator[PhysicalResource]:
    session = create_session()
    progress(ProgressEvent("Finding Resource Explorer aggregator index"))
    aggregator_region = get_aggregator_region(session)
    progress(ProgressEvent("Finding resources using Resource Explorer"))
    for aws_resource in get_resources(session, aggregator_region):
        resource_type = parse_resource_type(aws_resource.type)
        identifier = parse_identifier(resource_type, parse_arn(aws_resource.arn).resource_id)
        region = resolve_region(resource_type, aws_resource.region)
        resource = PhysicalResource(
            account=aws_resource.account_id,
            region=region,
            type=resource_type,
            identifier=identifier,
            system=is_system_resource(session, resource_type, region, identifier, progress),
        )
        progress(ProgressEvent("Indexing resources"))
        yield resource


def resolve_region(resource_type: ResourceType, region: str) -> str:
    if region == "global":
        return GLOBAL_REGION
    if resource_type.service in {"ce", "cloudfront", "iam", "route53"}:
        return GLOBAL_REGION
    if resource_type.service == "cloudwatch" and resource_type.kind == "dashboard":
        return GLOBAL_REGION
    return region
