from unittest.mock import patch

import pytest
from boto3 import Session

from cloud_index.aws.system_resource import is_system_resource
from cloud_index.resource import ResourceType


@pytest.mark.parametrize(
    ("service", "kind", "resource_id", "expected"),
    [
        ("apprunner", "autoscalingconfiguration", "DefaultConfiguration/1/00000000000000000000000000000001", True),
        ("apprunner", "autoscalingconfiguration", "MyConfiguration/1/00000000000000000000000000000001", False),
        ("athena", "datacatalog", "AwsDataCatalog", True),
        ("athena", "datacatalog", "MyDataCatalog", False),
        ("athena", "namedquery", "12345678-1234-1234-1234-123456789012", False),
        ("athena", "workgroup", "primary", True),
        ("athena", "workgroup", "my-workgroup", False),
        ("backup", "backup-vault", "Default", True),
        ("backup", "backup-vault", "MyBackupVault", False),
        ("elasticache", "user", "default", True),
        ("elasticache", "user", "my-user", False),
        ("elasticache", "cluster", "my-cluster", False),
        ("events", "event-bus", "default", True),
        ("events", "event-bus", "my-event-bus", False),
        ("iam", "policy", "service-role/AWSLambdaBasicExecutionRole-d2d4afb7-d9b8-4376-aa24-59dd4bbbe9e0", True),
        ("iam", "policy", "MyPolicy", False),
        ("iam", "role", "aws-service-role/globalaccelerator.amazonaws.com/AWSServiceRoleForGlobalAccelerator", True),
        ("iam", "role", "MyRole", False),
        ("iam", "user", "MyUser", False),
        ("glue", "database", "default", True),
        ("glue", "database", "my-database", False),
        ("memorydb", "acl", "open-access", True),
        ("memorydb", "acl", "my-acl", False),
        ("memorydb", "cluster", "my-cluster", False),
        ("memorydb", "parametergroup", "default.memorydb-redis6", True),
        ("memorydb", "parametergroup", "my-parameter-group", False),
        ("memorydb", "user", "default", True),
        ("memorydb", "user", "my-user", False),
        ("rds", "cluster-pg", "default.postgres17", True),
        ("rds", "cluster-pg", "my-cluster-pg", False),
        ("rds", "pg", "default.postgres17", True),
        ("rds", "pg", "my-pg", False),
        ("rds", "og", "default:postgres17", True),
        ("rds", "og", "my-og", False),
        ("rds", "secgrp", "default", True),
        ("rds", "secgrp", "my-secgrp", False),
        ("rds", "subgrp", "default", True),
        ("rds", "subgrp", "my-subgrp", False),
        ("rds", "dbinstance", "my-db-instance", False),
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
    assert is_system_resource(offline_session, resource_type, "us-east-1", resource_id) is expected


@pytest.mark.parametrize(
    ("key_manager", "expected"),
    [
        ("AWS", True),
        ("CUSTOMER", False),
    ],
)
def test_is_system_resource_kms_key(offline_session: Session, key_manager: str, expected: bool) -> None:
    resource_type = ResourceType("aws", "kms", "key")
    key_id = "72068baa-d0af-4942-abb9-bb08ad502707"
    with patch("cloud_index.aws.system_resource.get_kms_key_manager", return_value=key_manager) as get_key_manager:
        assert is_system_resource(offline_session, resource_type, "us-east-1", key_id) is expected
    get_key_manager.assert_called_once_with(offline_session, "us-east-1", key_id)
