from collections.abc import Generator

from boto3 import Session

from cloud_index.resource import Resource

from .arn import parse_arn
from .client import get_resources
from .regions import resolve_region
from .resource_type import parse_resource_type
from .system_resource import is_system_resource


def index(session: Session) -> Generator[Resource]:
    for resource in get_resources(session):
        arn = parse_arn(resource.arn)
        resource_type = parse_resource_type(resource.type)
        region = resolve_region(resource.region)
        yield Resource(
            account=resource.account_id,
            region=region,
            type=resource_type,
            identifier=arn.resource_id,
            system=is_system_resource(session, resource_type, region, arn.resource_id),
        )
