import pytest
from boto3 import Session
from botocore.stub import Stubber

from cloud_index.aws.client import get_kms_key_manager
from cloud_index.aws.error import AwsAccessError
from tests.cloud_index.aws.stubs import stub_describe_key


def test_get_kms_key_manager(session: Session) -> None:
    key_id = "ea386976-3b3e-4c6a-a277-e7c9aa2b8dff"
    with Stubber(session.client("kms", region_name="us-east-1")) as stubber:
        stub_describe_key(stubber, key_id, "AWS")
        assert get_kms_key_manager(session, "us-east-1", key_id) == "AWS"
        stubber.assert_no_pending_responses()


def test_get_kms_key_manager_access_denied(session: Session) -> None:
    key_id = "2a3e09b2-d4d9-41fb-8eb2-f4ecd7e180e0"
    with Stubber(session.client("kms", region_name="us-east-1")) as stubber:
        stubber.add_client_error("describe_key", service_error_code="AccessDeniedException", http_status_code=403)
        with pytest.raises(AwsAccessError):
            get_kms_key_manager(session, "us-east-1", key_id)
        stubber.assert_no_pending_responses()
