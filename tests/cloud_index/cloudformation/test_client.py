from typing import get_args
from unittest.mock import patch

import pytest
from boto3 import Session
from botocore.stub import Stubber
from types_boto3_cloudformation.literals import ResourceStatusType, StackStatusType

from cloud_index.aws.error import AwsAccessError
from cloud_index.cloudformation.client import (
    ACTIVE_RESOURCE_STATUSES,
    ACTIVE_STACK_STATUSES,
    INACTIVE_RESOURCE_STATUSES,
    INACTIVE_STACK_STATUSES,
    get_cloudformation_client,
    get_enabled_regions,
    get_stack_resources,
    get_stacks,
)

STACK_ID = "arn:aws:cloudformation:us-east-1:123456789012:stack/MyStack/9264fd82-c31b-49e9-b4a5-a7b6a6b984b3"


def test_active_stack_statuses() -> None:
    assert set(ACTIVE_STACK_STATUSES) | INACTIVE_STACK_STATUSES == set(get_args(StackStatusType))
    assert not set(ACTIVE_STACK_STATUSES) & INACTIVE_STACK_STATUSES
    assert "CREATE_COMPLETE" in ACTIVE_STACK_STATUSES
    assert "UPDATE_ROLLBACK_COMPLETE" in ACTIVE_STACK_STATUSES


def test_active_resource_statuses() -> None:
    assert set(get_args(ResourceStatusType)) == ACTIVE_RESOURCE_STATUSES | INACTIVE_RESOURCE_STATUSES
    assert not ACTIVE_RESOURCE_STATUSES & INACTIVE_RESOURCE_STATUSES
    assert "CREATE_COMPLETE" in ACTIVE_RESOURCE_STATUSES
    assert "UPDATE_ROLLBACK_COMPLETE" in ACTIVE_RESOURCE_STATUSES


def test_get_cloudformation_client_repeated_region(session: Session) -> None:
    with patch.object(session, "client", wraps=session.client) as create_client:
        get_cloudformation_client(session, "us-east-1")
        get_cloudformation_client(session, "us-east-1")

    create_client.assert_called_once_with("cloudformation", region_name="us-east-1")


def test_get_enabled_regions_access_denied(session: Session) -> None:
    with Stubber(session.client("account", region_name="us-east-1")) as stubber:
        stubber.add_client_error("list_regions", service_error_code="AccessDeniedException", http_status_code=403)
        with pytest.raises(AwsAccessError, match="Could not list AWS regions"):
            list(get_enabled_regions(session))
        stubber.assert_no_pending_responses()


def test_get_stacks_access_denied(session: Session) -> None:
    with Stubber(session.client("cloudformation", region_name="us-east-1")) as stubber:
        stubber.add_client_error("list_stacks", service_error_code="AccessDeniedException", http_status_code=403)
        with pytest.raises(AwsAccessError):
            list(get_stacks(session, "us-east-1"))
        stubber.assert_no_pending_responses()


def test_get_stack_resources_access_denied(session: Session) -> None:
    with Stubber(session.client("cloudformation", region_name="us-east-1")) as stubber:
        stubber.add_client_error(
            "list_stack_resources", service_error_code="AccessDeniedException", http_status_code=403
        )
        with pytest.raises(AwsAccessError):
            list(get_stack_resources(session, "us-east-1", STACK_ID))
        stubber.assert_no_pending_responses()
