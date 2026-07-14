from collections.abc import Generator
from dataclasses import dataclass
from functools import cache
from typing import get_args

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from types_boto3_account import AccountClient
from types_boto3_cloudformation import CloudFormationClient
from types_boto3_cloudformation.literals import ResourceStatusType, StackStatusType

from cloud_index.aws.client import DEFAULT_REGION
from cloud_index.aws.error import AwsAccessError

INACTIVE_STACK_STATUSES: set[StackStatusType] = {
    # Stack has been deleted
    "DELETE_COMPLETE",
    # Change set created but nothing provisioned
    "REVIEW_IN_PROGRESS",
    # Failed creation fully rolled back, resources deleted
    "ROLLBACK_COMPLETE",
}

INACTIVE_RESOURCE_STATUSES: set[ResourceStatusType] = {
    # Resource was not created
    "CREATE_FAILED",
    # Resource has been deleted
    "DELETE_COMPLETE",
    # Resource retained in the account but no longer managed by the stack
    "DELETE_SKIPPED",
    # Resource moved to another stack, which reports it as IMPORT_COMPLETE
    "EXPORT_COMPLETE",
    # Import never took effect, resource not managed by the stack
    "IMPORT_FAILED",
    "IMPORT_ROLLBACK_COMPLETE",
}

ACTIVE_STACK_STATUSES: list[StackStatusType] = sorted(set(get_args(StackStatusType)) - INACTIVE_STACK_STATUSES)

ACTIVE_RESOURCE_STATUSES: set[ResourceStatusType] = set(get_args(ResourceStatusType)) - INACTIVE_RESOURCE_STATUSES


@dataclass(frozen=True)
class StackResource:
    logical_id: str
    physical_id: str
    type: str


def get_account_client(session: Session) -> AccountClient:
    client: AccountClient = session.client("account", region_name=DEFAULT_REGION)
    return client


@cache
def get_cloudformation_client(session: Session, region: str) -> CloudFormationClient:
    client: CloudFormationClient = session.client("cloudformation", region_name=region)
    return client


def get_enabled_regions(session: Session) -> Generator[str]:
    try:
        client = get_account_client(session)
        paginator = client.get_paginator("list_regions")
        for page in paginator.paginate(RegionOptStatusContains=["ENABLED_BY_DEFAULT"]):
            for region in page["Regions"]:
                assert "RegionName" in region
                yield region["RegionName"]
    except (BotoCoreError, ClientError) as error:
        raise AwsAccessError(f"Could not list AWS regions: {error}") from error


def get_stacks(session: Session, region: str) -> Generator[str]:
    try:
        client = get_cloudformation_client(session, region)
        paginator = client.get_paginator("list_stacks")
        for page in paginator.paginate(StackStatusFilter=ACTIVE_STACK_STATUSES):
            for stack_summary in page["StackSummaries"]:
                assert "StackId" in stack_summary
                yield stack_summary["StackId"]
    except (BotoCoreError, ClientError) as error:
        raise AwsAccessError(f"Could not query CloudFormation in {region}: {error}") from error


def get_stack_resources(session: Session, region: str, stack_id: str) -> Generator[StackResource]:
    try:
        client = get_cloudformation_client(session, region)
        paginator = client.get_paginator("list_stack_resources")
        for page in paginator.paginate(StackName=stack_id):
            for summary in page["StackResourceSummaries"]:
                if summary["ResourceStatus"] not in ACTIVE_RESOURCE_STATUSES:
                    continue
                # A resource that failed to provision may have no physical id
                if "PhysicalResourceId" not in summary:
                    continue
                yield StackResource(
                    logical_id=summary["LogicalResourceId"],
                    physical_id=summary["PhysicalResourceId"],
                    type=summary["ResourceType"],
                )
    except (BotoCoreError, ClientError) as error:
        raise AwsAccessError(f"Could not query CloudFormation in {region}: {error}") from error
