from unittest.mock import patch

import pytest
from boto3 import Session
from botocore.exceptions import ProfileNotFound
from botocore.stub import Stubber

from cloud_index.aws.client import (
    KmsKey,
    create_session,
    get_aggregator_region,
    get_available_regions,
    get_kms_client,
    get_kms_key,
    get_resources,
)
from cloud_index.aws.error import AwsAccessError
from tests.cloud_index.aws.stubs import stub_describe_key


def test_create_session_configuration_error() -> None:
    with (
        patch("cloud_index.aws.client.Session", side_effect=ProfileNotFound(profile="missing")),
        pytest.raises(AwsAccessError, match="Could not configure AWS session"),
    ):
        create_session()


def test_get_available_regions() -> None:
    regions = get_available_regions()
    assert isinstance(regions, set)
    assert len(regions) > 0
    assert "us-east-1" in regions
    assert "us-west-2" in regions
    assert "eu-west-1" in regions
    assert "aws-global" in regions


def test_get_kms_client_caches_clients(session: Session) -> None:
    with patch.object(session, "client", wraps=session.client) as create_client:
        get_kms_client(session, "us-east-1")
        get_kms_client(session, "us-east-1")

    create_client.assert_called_once_with("kms", region_name="us-east-1")


def test_get_kms_key(session: Session) -> None:
    key_id = "ea386976-3b3e-4c6a-a277-e7c9aa2b8dff"
    with Stubber(session.client("kms", region_name="us-east-1")) as stubber:
        stub_describe_key(stubber, key_id, "AWS")
        assert get_kms_key(session, "us-east-1", key_id) == KmsKey(key_manager="AWS")
        stubber.assert_no_pending_responses()


def test_get_kms_key_access_denied(session: Session) -> None:
    key_id = "2a3e09b2-d4d9-41fb-8eb2-f4ecd7e180e0"
    with Stubber(session.client("kms", region_name="us-east-1")) as stubber:
        stubber.add_client_error("describe_key", service_error_code="AccessDeniedException", http_status_code=403)
        with pytest.raises(AwsAccessError):
            get_kms_key(session, "us-east-1", key_id)
        stubber.assert_no_pending_responses()


def test_get_aggregator_region_access_denied(session: Session) -> None:
    with Stubber(session.client("resource-explorer-2", region_name="us-east-1")) as stubber:
        stubber.add_client_error("list_indexes", service_error_code="AccessDeniedException", http_status_code=403)
        with pytest.raises(AwsAccessError):
            get_aggregator_region(session)
        stubber.assert_no_pending_responses()


def test_get_resources_access_denied(session: Session) -> None:
    with Stubber(session.client("resource-explorer-2", region_name="us-east-1")) as stubber:
        stubber.add_client_error("list_resources", service_error_code="AccessDeniedException", http_status_code=403)
        with pytest.raises(AwsAccessError):
            list(get_resources(session, "us-east-1"))
        stubber.assert_no_pending_responses()
