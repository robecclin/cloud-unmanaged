from collections.abc import Generator
from dataclasses import dataclass

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from types_boto3_resource_explorer_2 import ResourceExplorerClient

from .error import AwsAccessError, NoAggregatorIndexFoundError

DEFAULT_REGION = "us-east-1"


@dataclass
class AwsResource:
    arn: str
    account_id: str
    region: str
    type: str


def get_resource_explorer_client(session: Session, region: str) -> ResourceExplorerClient:
    client: ResourceExplorerClient = session.client("resource-explorer-2", region_name=region)
    return client


def get_aggregator_region(session: Session) -> str:
    client = get_resource_explorer_client(session, DEFAULT_REGION)
    paginator = client.get_paginator("list_indexes")
    for page in paginator.paginate():
        for idx in page["Indexes"]:
            assert "Type" in idx
            assert "Region" in idx
            if idx["Type"] == "AGGREGATOR":
                return idx["Region"]
    raise NoAggregatorIndexFoundError()


def get_resources(session: Session) -> Generator[AwsResource]:
    try:
        region = get_aggregator_region(session)
        client = get_resource_explorer_client(session, region)
        paginator = client.get_paginator("list_resources")
        for page in paginator.paginate():
            for resource in page["Resources"]:
                assert "Arn" in resource
                assert "OwningAccountId" in resource
                assert "Region" in resource
                assert "ResourceType" in resource
                yield AwsResource(
                    arn=resource["Arn"],
                    account_id=resource["OwningAccountId"],
                    region=resource["Region"],
                    type=resource["ResourceType"],
                )
    except (BotoCoreError, ClientError) as error:
        raise AwsAccessError(f"Could not query AWS Resource Explorer: {error}") from error
