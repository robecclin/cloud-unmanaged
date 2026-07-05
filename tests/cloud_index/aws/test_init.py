from unittest.mock import patch

import pytest
from boto3 import Session
from botocore.stub import Stubber

from cloud_index.aws import NoAggregatorIndexFoundError, index
from cloud_index.progress import ProgressEvent
from cloud_index.resource import Resource, ResourceType
from tests.cloud_index.aws.stubs import (
    aws_resource,
    stub_describe_key,
    stub_list_indexes,
    stub_list_resources,
)


def test_index(session: Session) -> None:
    progress_events: list[ProgressEvent] = []
    with (
        patch("cloud_index.aws.indexer.create_session", return_value=session),
        Stubber(session.client("resource-explorer-2", region_name="us-east-1")) as stubber,
    ):
        stub_list_resources(
            stubber,
            aws_resource("arn:aws:dynamodb:us-east-1:123456789012:table/MyTable", "dynamodb:table"),
            aws_resource(
                "arn:aws:resource-explorer-2:us-east-1:123456789012:index/0238d232-7a99-41b9-9e3e-d71e97d571c5",
                "resource-explorer-2:index",
            ),
            aws_resource("arn:aws:iam::123456789012:role/MyRole", "iam:role", region="global"),
        )
        actual = list(index(progress_events.append))
        stubber.assert_no_pending_responses()

    assert len(actual) == 3
    assert actual[0] == Resource(
        type=ResourceType("aws", "dynamodb", "table"),
        account="123456789012",
        region="us-east-1",
        identifier="MyTable",
        system=False,
    )
    assert actual[1] == Resource(
        type=ResourceType("aws", "resource-explorer-2", "index"),
        account="123456789012",
        region="us-east-1",
        identifier="0238d232-7a99-41b9-9e3e-d71e97d571c5",
        system=False,
    )
    assert actual[2] == Resource(
        type=ResourceType("aws", "iam", "role"),
        account="123456789012",
        region="aws-global",
        identifier="MyRole",
        system=False,
    )
    assert progress_events == [
        ProgressEvent("Finding Resource Explorer aggregator index"),
        ProgressEvent("Finding resources using Resource Explorer"),
        ProgressEvent("Indexing resources", count=1),
        ProgressEvent("Indexing resources", count=2),
        ProgressEvent("Indexing resources", count=3),
    ]


def test_index_system_resources(session: Session) -> None:
    with (
        patch("cloud_index.aws.indexer.create_session", return_value=session),
        Stubber(session.client("resource-explorer-2", region_name="us-east-1")) as stubber,
    ):
        stub_list_resources(
            stubber,
            aws_resource(
                "arn:aws:iam::123456789012:role/aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS",
                "iam:role",
            ),
            aws_resource("arn:aws:s3:::my-bucket", "s3:bucket"),
        )
        actual = list(index())
        stubber.assert_no_pending_responses()

    assert len(actual) == 2
    assert actual[0] == Resource(
        type=ResourceType("aws", "iam", "role"),
        account="123456789012",
        region="us-east-1",
        identifier="aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS",
        system=True,
    )
    assert actual[1] == Resource(
        type=ResourceType("aws", "s3", "bucket"),
        account="123456789012",
        region="us-east-1",
        identifier="my-bucket",
        system=False,
    )


def test_index_system_kms_key(session: Session) -> None:
    key_id = "eee9232a-d9fb-44d7-908b-c58069fb405e"
    progress_events: list[ProgressEvent] = []
    with (
        patch("cloud_index.aws.indexer.create_session", return_value=session),
        Stubber(session.client("resource-explorer-2", region_name="us-east-1")) as resource_explorer_stubber,
        Stubber(session.client("kms", region_name="eu-west-1")) as kms_stubber,
    ):
        stub_list_resources(
            resource_explorer_stubber,
            aws_resource(f"arn:aws:kms:eu-west-1:123456789012:key/{key_id}", "kms:key", region="eu-west-1"),
        )
        stub_describe_key(kms_stubber, key_id, "AWS")
        actual = list(index(progress_events.append))
        resource_explorer_stubber.assert_no_pending_responses()
        kms_stubber.assert_no_pending_responses()

    assert len(actual) == 1
    assert actual[0] == Resource(
        type=ResourceType("aws", "kms", "key"),
        account="123456789012",
        region="eu-west-1",
        identifier=key_id,
        system=True,
    )
    assert progress_events == [
        ProgressEvent("Finding Resource Explorer aggregator index"),
        ProgressEvent("Finding resources using Resource Explorer"),
        ProgressEvent(f"Checking KMS key {key_id} in eu-west-1"),
        ProgressEvent("Indexing resources", count=1),
    ]


def test_index_no_aggregator_index(session: Session) -> None:
    with (
        patch("cloud_index.aws.indexer.create_session", return_value=session),
        Stubber(session.client("resource-explorer-2", region_name="us-east-1")) as stubber,
    ):
        stub_list_indexes(stubber, "LOCAL")
        with pytest.raises(NoAggregatorIndexFoundError):
            list(index(lambda event: None))
        stubber.assert_no_pending_responses()
