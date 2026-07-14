from collections.abc import Generator

from cloud_index.aws.arn import parse_arn
from cloud_index.aws.client import create_session
from cloud_index.aws.indexer import resolve_region
from cloud_index.progress import ProgressEvent, ProgressReporter
from cloud_index.resource import LogicalResource

from .client import get_enabled_regions, get_stack_resources, get_stacks
from .identifier import parse_identifier
from .resource_type import parse_resource_type


def index(progress: ProgressReporter = lambda _: None) -> Generator[LogicalResource]:
    session = create_session()
    progress(ProgressEvent("Finding enabled regions"))
    for region in get_enabled_regions(session):
        progress(ProgressEvent(f"Finding CloudFormation stacks in {region}"))
        for stack_id in get_stacks(session, region):
            arn = parse_arn(stack_id)
            account = arn.account_id
            assert account is not None
            stack_name = arn.resource_id.split("/")[0]
            progress(ProgressEvent(f"Indexing resources in stack {stack_name}"))
            for stack_resource in get_stack_resources(session, region, stack_id):
                resource_type = parse_resource_type(stack_resource.type)
                if resource_type is None:
                    progress(ProgressEvent(f"Skipping unsupported resource type {stack_resource.type}"))
                    continue
                identifier = parse_identifier(resource_type, stack_resource.physical_id)
                if identifier is None:
                    progress(ProgressEvent(f"Skipping unsupported resource {stack_resource.logical_id}"))
                    continue
                yield LogicalResource(
                    type=resource_type,
                    account=account,
                    region=resolve_region(resource_type, region),
                    identifier=identifier,
                    locator=stack_id,
                    name=stack_resource.logical_id,
                )
