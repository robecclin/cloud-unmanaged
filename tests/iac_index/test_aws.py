from datetime import datetime
from unittest.mock import patch

import pytest
from boto3 import Session
from botocore.stub import Stubber
from types_boto3_resource_explorer_2.type_defs import ListIndexesOutputTypeDef, ListResourcesOutputTypeDef

from cloud_index.aws import AwsAccessError, NoAggregatorIndexFoundError, index
from cloud_index.resource import Resource, ResourceType


def test_index() -> None:
    session = Session()
    client = session.client("resource-explorer-2", region_name="us-east-1")
    with Stubber(client) as stubber, patch.object(session, "client", return_value=client):
        response_indexes: ListIndexesOutputTypeDef = {
            "Indexes": [
                {
                    "Type": "AGGREGATOR",
                    "Region": "us-east-1",
                }
            ],
            "ResponseMetadata": {
                "RequestId": "",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {},
                "RetryAttempts": 0,
            },
        }
        stubber.add_response("list_indexes", response_indexes, {})
        response: ListResourcesOutputTypeDef = {
            "Resources": [
                {
                    "Arn": "arn:aws:dynamodb:us-east-1:123456789012:table/MyTable",
                    "OwningAccountId": "123456789012",
                    "Region": "us-east-1",
                    "ResourceType": "dynamodb:table",
                    "Service": "dynamodb",
                    "LastReportedAt": datetime(2020, 1, 1),
                },
                {
                    "Arn": (
                        "arn:aws:resource-explorer-2:us-east-1:123456789012:index/0238d232-7a99-41b9-9e3e-d71e97d571c5"
                    ),
                    "OwningAccountId": "123456789012",
                    "Region": "us-east-1",
                    "ResourceType": "resource-explorer-2:index",
                    "Service": "resource-explorer-2",
                    "LastReportedAt": datetime(2020, 1, 1),
                },
                {
                    "Arn": "arn:aws:iam::123456789012:role/MyRole",
                    "OwningAccountId": "123456789012",
                    "Region": "global",
                    "ResourceType": "iam:role",
                    "Service": "iam",
                    "LastReportedAt": datetime(2020, 1, 1),
                },
            ],
            "ResponseMetadata": {
                "RequestId": "",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {},
                "RetryAttempts": 0,
            },
            "ViewArn": (
                "arn:aws:resource-explorer-2:us-east-1:123456789012:view/us-east-1/367b491a-1e6d-41b1-9065-1de5d7f63d65"
            ),
        }
        stubber.add_response("list_resources", response, {})
        actual = list(index(session))
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


def test_index_marks_system_resources() -> None:
    session = Session()
    client = session.client("resource-explorer-2", region_name="us-east-1")
    with Stubber(client) as stubber, patch.object(session, "client", return_value=client):
        response_indexes: ListIndexesOutputTypeDef = {
            "Indexes": [
                {
                    "Type": "AGGREGATOR",
                    "Region": "us-east-1",
                }
            ],
            "ResponseMetadata": {
                "RequestId": "",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {},
                "RetryAttempts": 0,
            },
        }
        stubber.add_response("list_indexes", response_indexes, {})
        response: ListResourcesOutputTypeDef = {
            "Resources": [
                {
                    "Arn": "arn:aws:iam::123456789012:role/aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS",
                    "OwningAccountId": "123456789012",
                    "Region": "us-east-1",
                    "ResourceType": "iam:role",
                    "Service": "iam",
                    "LastReportedAt": datetime(2020, 1, 1),
                },
                {
                    "Arn": "arn:aws:s3:::my-bucket",
                    "OwningAccountId": "123456789012",
                    "Region": "us-east-1",
                    "ResourceType": "s3:bucket",
                    "Service": "s3",
                    "LastReportedAt": datetime(2020, 1, 1),
                },
            ],
            "ResponseMetadata": {
                "RequestId": "",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {},
                "RetryAttempts": 0,
            },
            "ViewArn": (
                "arn:aws:resource-explorer-2:us-east-1:123456789012:view/us-east-1/367b491a-1e6d-41b1-9065-1de5d7f63d65"
            ),
        }
        stubber.add_response("list_resources", response, {})
        actual = list(index(session))
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


def test_index_no_aggregator_index() -> None:
    session = Session()
    client = session.client("resource-explorer-2", region_name="us-east-1")
    with Stubber(client) as stubber, patch.object(session, "client", return_value=client):
        response_indexes: ListIndexesOutputTypeDef = {
            "Indexes": [
                {
                    "Type": "LOCAL",
                    "Region": "us-east-1",
                }
            ],
            "ResponseMetadata": {
                "RequestId": "",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {},
                "RetryAttempts": 0,
            },
        }
        stubber.add_response("list_indexes", response_indexes, {})
        with pytest.raises(NoAggregatorIndexFoundError):
            list(index(session))
        stubber.assert_no_pending_responses()


def test_index_access_denied() -> None:
    session = Session()
    client = session.client("resource-explorer-2", region_name="us-east-1")
    with Stubber(client) as stubber, patch.object(session, "client", return_value=client):
        stubber.add_client_error("list_indexes", service_error_code="AccessDeniedException", http_status_code=403)
        with pytest.raises(AwsAccessError):
            list(index(session))
        stubber.assert_no_pending_responses()
