from unittest.mock import patch

from boto3 import Session
from botocore.stub import Stubber

from cloud_index.cloudformation import index
from cloud_index.progress import ProgressEvent
from cloud_index.resource import LogicalResource, ResourceType
from tests.cloud_index.cloudformation.stubs import (
    stack_resource,
    stub_list_regions,
    stub_list_stack_resources,
    stub_list_stacks,
)

STACK_ID = "arn:aws:cloudformation:us-east-1:123456789012:stack/MyStack/9264fd82-c31b-49e9-b4a5-a7b6a6b984b3"


def test_index(session: Session) -> None:
    progress_events: list[ProgressEvent] = []
    with (
        patch("cloud_index.cloudformation.indexer.create_session", return_value=session),
        Stubber(session.client("account", region_name="us-east-1")) as account_stubber,
        Stubber(session.client("cloudformation", region_name="us-east-1")) as cloudformation_stubber,
    ):
        stub_list_regions(account_stubber, "us-east-1")
        stub_list_stacks(cloudformation_stubber, STACK_ID)
        stub_list_stack_resources(
            cloudformation_stubber,
            STACK_ID,
            stack_resource("MyTable", "AWS::DynamoDB::Table", "MyTable"),
            stack_resource("MyDeletedBucket", "AWS::S3::Bucket", "my-deleted-bucket", status="DELETE_COMPLETE"),
            stack_resource("MyFailedBucket", "AWS::S3::Bucket"),
        )
        actual = list(index(progress_events.append))
        account_stubber.assert_no_pending_responses()
        cloudformation_stubber.assert_no_pending_responses()

    assert actual == [
        LogicalResource(
            type=ResourceType("aws", "dynamodb", "table"),
            account="123456789012",
            region="us-east-1",
            identifier="MyTable",
            locator=STACK_ID,
            name="MyTable",
        ),
    ]
    assert progress_events == [
        ProgressEvent("Finding enabled regions"),
        ProgressEvent("Finding CloudFormation stacks in us-east-1"),
        ProgressEvent("Indexing resources in stack MyStack"),
    ]


def test_index_unsupported_resources(session: Session) -> None:
    progress_events: list[ProgressEvent] = []
    with (
        patch("cloud_index.cloudformation.indexer.create_session", return_value=session),
        Stubber(session.client("account", region_name="us-east-1")) as account_stubber,
        Stubber(session.client("cloudformation", region_name="us-east-1")) as cloudformation_stubber,
    ):
        stub_list_regions(account_stubber, "us-east-1")
        stub_list_stacks(cloudformation_stubber, STACK_ID)
        stub_list_stack_resources(
            cloudformation_stubber,
            STACK_ID,
            stack_resource("MyCustom", "Custom::Widget", "MyWidget"),
            stack_resource("MyIngress", "AWS::EC2::SecurityGroupIngress", "MyIngress"),
        )
        actual = list(index(progress_events.append))
        account_stubber.assert_no_pending_responses()
        cloudformation_stubber.assert_no_pending_responses()

    assert actual == []
    assert progress_events == [
        ProgressEvent("Finding enabled regions"),
        ProgressEvent("Finding CloudFormation stacks in us-east-1"),
        ProgressEvent("Indexing resources in stack MyStack"),
        ProgressEvent("Skipping unsupported resource type Custom::Widget"),
        ProgressEvent("Skipping unsupported resource MyIngress"),
    ]
