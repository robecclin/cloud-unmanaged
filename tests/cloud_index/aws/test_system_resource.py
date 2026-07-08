from unittest.mock import patch

import pytest
from boto3 import Session

from cloud_index.aws.client import KeyManager, KmsKey
from cloud_index.aws.system_resource import is_system_resource
from cloud_index.progress import ProgressEvent
from cloud_index.resource import ResourceType


@pytest.mark.parametrize(
    ("service", "kind", "resource_id", "expected"),
    [
        ("apprunner", "auto-scaling-configuration", "DefaultConfiguration/1/00000000000000000000000000000001", True),
        ("apprunner", "auto-scaling-configuration", "MyConfiguration/1/00000000000000000000000000000001", False),
        ("athena", "data-catalog", "AwsDataCatalog", True),
        ("athena", "data-catalog", "MyDataCatalog", False),
        ("athena", "named-query", "12345678-1234-1234-1234-123456789012", False),
        ("athena", "workgroup", "primary", True),
        ("athena", "workgroup", "my-workgroup", False),
        ("backup", "backup-vault", "Default", True),
        ("backup", "backup-vault", "MyBackupVault", False),
        ("elasticache", "user", "default", True),
        ("elasticache", "user", "my-user", False),
        ("elasticache", "cache-cluster", "my-cluster", False),
        ("events", "event-bus", "default", True),
        ("events", "event-bus", "my-event-bus", False),
        (
            "iam",
            "managed-policy",
            "service-role/AWSLambdaBasicExecutionRole-d2d4afb7-d9b8-4376-aa24-59dd4bbbe9e0",
            False,
        ),
        ("iam", "role", "aws-service-role/globalaccelerator.amazonaws.com/AWSServiceRoleForGlobalAccelerator", True),
        ("iam", "role", "MyRole", False),
        ("iam", "user", "MyUser", False),
        ("glue", "database", "default", True),
        ("glue", "database", "my-database", False),
        ("memorydb", "acl", "open-access", True),
        ("memorydb", "acl", "my-acl", False),
        ("memorydb", "cluster", "my-cluster", False),
        ("memorydb", "parameter-group", "default.memorydb-redis6", True),
        ("memorydb", "parameter-group", "my-parameter-group", False),
        ("memorydb", "user", "default", True),
        ("memorydb", "user", "my-user", False),
        ("rds", "db-cluster-parameter-group", "default.postgres17", True),
        ("rds", "db-cluster-parameter-group", "my-cluster-pg", False),
        ("rds", "db-parameter-group", "default.postgres17", True),
        ("rds", "db-parameter-group", "my-pg", False),
        ("rds", "option-group", "default:postgres17", True),
        ("rds", "option-group", "my-og", False),
        ("rds", "db-security-group", "default", True),
        ("rds", "db-security-group", "my-secgrp", False),
        ("rds", "db-subnet-group", "default", True),
        ("rds", "db-subnet-group", "my-subgrp", False),
        ("rds", "db-instance", "my-db-instance", False),
        ("s3", "storage-lens", "default-account-dashboard", True),
        ("s3", "storage-lens", "my-storage-lens", False),
        ("s3", "bucket", "my-bucket", False),
        ("xray", "sampling-rule", "Default", True),
        ("xray", "sampling-rule", "my-sampling-rule", False),
    ],
)
def test_is_system_resource(
    offline_session: Session, service: str, kind: str, resource_id: str, expected: bool
) -> None:
    resource_type = ResourceType("aws", service, kind)
    assert is_system_resource(offline_session, resource_type, "us-east-1", resource_id, lambda _: None) is expected


@pytest.mark.parametrize(
    ("key_manager", "expected"),
    [
        ("AWS", True),
        ("CUSTOMER", False),
    ],
)
def test_is_system_resource_kms_key(offline_session: Session, key_manager: KeyManager, expected: bool) -> None:
    resource_type = ResourceType("aws", "kms", "key")
    key_id = "72068baa-d0af-4942-abb9-bb08ad502707"
    progress_events: list[ProgressEvent] = []

    with patch("cloud_index.aws.system_resource.get_kms_key", return_value=KmsKey(key_manager)) as get_kms_key:
        actual = is_system_resource(offline_session, resource_type, "us-east-1", key_id, progress_events.append)
    assert actual is expected
    get_kms_key.assert_called_once_with(offline_session, "us-east-1", key_id)
    assert progress_events == [ProgressEvent(f"Checking KMS key {key_id} in us-east-1")]
