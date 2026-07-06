from datetime import UTC, datetime

from botocore.stub import Stubber
from types_boto3_account.type_defs import ListRegionsResponseTypeDef
from types_boto3_cloudformation.literals import ResourceStatusType
from types_boto3_cloudformation.type_defs import (
    ListStackResourcesOutputTypeDef,
    ListStacksOutputTypeDef,
    StackResourceSummaryTypeDef,
)

from cloud_index.cloudformation.client import ACTIVE_STACK_STATUSES
from tests.cloud_index.aws.stubs import RESPONSE_METADATA

TIMESTAMP = datetime(2026, 1, 1, tzinfo=UTC)


def stack_resource(
    logical_id: str,
    resource_type: str,
    physical_id: str | None = None,
    status: ResourceStatusType = "CREATE_COMPLETE",
) -> StackResourceSummaryTypeDef:
    summary: StackResourceSummaryTypeDef = {
        "LogicalResourceId": logical_id,
        "ResourceType": resource_type,
        "ResourceStatus": status,
        "LastUpdatedTimestamp": TIMESTAMP,
    }
    if physical_id is not None:
        summary["PhysicalResourceId"] = physical_id
    return summary


def stub_list_regions(stubber: Stubber, *regions: str) -> None:
    response: ListRegionsResponseTypeDef = {
        "Regions": [{"RegionName": region, "RegionOptStatus": "ENABLED_BY_DEFAULT"} for region in regions],
        "ResponseMetadata": RESPONSE_METADATA,
    }
    stubber.add_response("list_regions", response, {"RegionOptStatusContains": ["ENABLED_BY_DEFAULT"]})


def stub_list_stacks(stubber: Stubber, *stack_ids: str) -> None:
    response: ListStacksOutputTypeDef = {
        "StackSummaries": [
            {
                "StackId": stack_id,
                "StackName": stack_id.split("/")[1],
                "CreationTime": TIMESTAMP,
                "StackStatus": "CREATE_COMPLETE",
            }
            for stack_id in stack_ids
        ],
        "ResponseMetadata": RESPONSE_METADATA,
    }
    stubber.add_response("list_stacks", response, {"StackStatusFilter": ACTIVE_STACK_STATUSES})


def stub_list_stack_resources(stubber: Stubber, stack_id: str, *resources: StackResourceSummaryTypeDef) -> None:
    response: ListStackResourcesOutputTypeDef = {
        "StackResourceSummaries": list(resources),
        "ResponseMetadata": RESPONSE_METADATA,
    }
    stubber.add_response("list_stack_resources", response, {"StackName": stack_id})
