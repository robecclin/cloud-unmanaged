from collections.abc import Generator
from dataclasses import dataclass
from functools import cache
from typing import Literal

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from botocore.session import Session as BotoCoreSession
from types_boto3_kms import KMSClient
from types_boto3_resource_explorer_2 import ResourceExplorerClient

from .error import AwsAccessError, NoAggregatorIndexFoundError

DEFAULT_REGION = "us-east-1"

type KeyManager = Literal["AWS", "CUSTOMER"]


@dataclass
class AwsResource:
    arn: str
    account_id: str
    region: str
    type: str


@dataclass
class KmsKey:
    key_manager: KeyManager


def create_session() -> Session:
    try:
        return Session()
    except BotoCoreError as error:
        raise AwsAccessError(f"Could not configure AWS session: {error}") from error


def get_available_regions() -> set[str]:
    loader = BotoCoreSession().get_component("data_loader")
    partitions = loader.load_data("partitions")
    regions: set[str] = set()
    for partition in partitions["partitions"]:
        regions.update(partition["regions"])
    return regions


def get_resource_explorer_client(session: Session, region: str) -> ResourceExplorerClient:
    client: ResourceExplorerClient = session.client("resource-explorer-2", region_name=region)
    return client


@cache
def get_kms_client(session: Session, region: str) -> KMSClient:
    client: KMSClient = session.client("kms", region_name=region)
    return client


def get_kms_key(session: Session, region: str, key_id: str) -> KmsKey:
    client = get_kms_client(session, region)
    try:
        metadata = client.describe_key(KeyId=key_id)["KeyMetadata"]
    except (BotoCoreError, ClientError) as error:
        raise AwsAccessError(f"Could not describe KMS key {key_id}: {error}") from error
    assert "KeyManager" in metadata
    return KmsKey(key_manager=metadata["KeyManager"])


def get_aggregator_region(session: Session) -> str:
    try:
        client = get_resource_explorer_client(session, DEFAULT_REGION)
        paginator = client.get_paginator("list_indexes")
        for page in paginator.paginate():
            for idx in page["Indexes"]:
                assert "Type" in idx
                assert "Region" in idx
                if idx["Type"] == "AGGREGATOR":
                    return idx["Region"]
    except (BotoCoreError, ClientError) as error:
        raise AwsAccessError(f"Could not query AWS Resource Explorer: {error}") from error
    raise NoAggregatorIndexFoundError()


def get_resources(session: Session, region: str) -> Generator[AwsResource]:
    try:
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
