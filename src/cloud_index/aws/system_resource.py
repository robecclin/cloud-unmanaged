from boto3 import Session

from cloud_index.progress import ProgressEvent, ProgressReporter
from cloud_index.resource import ResourceType

from .client import get_kms_key


def is_system_resource(
    session: Session,
    resource_type: ResourceType,
    region: str,
    resource_id: str,
    progress: ProgressReporter,
) -> bool:
    """
    Returns true if a resource is a system resource, i.e., managed by AWS and cannot be deleted.
    This does not include implicit resources, which are resources that exist because they are
    created automatically by another resource type, e.g., a default subnet in a VPC.
    """
    match resource_type.service, resource_type.kind:
        case "apprunner", "auto-scaling-configuration":
            return resource_id.startswith("DefaultConfiguration/")
        case "athena", "data-catalog":
            return resource_id == "AwsDataCatalog"
        case "athena", "workgroup":
            return resource_id == "primary"
        case "backup", "backup-vault":
            return resource_id == "Default"
        case "elasticache", "user":
            return resource_id == "default"
        case "events", "event-bus":
            return resource_id == "default"
        case "iam", "role":
            return resource_id.startswith("aws-service-role/")
        case "glue", "database":
            return resource_id == "default"
        case "kms", "key":
            progress(ProgressEvent(f"Checking KMS key {resource_id} in {region}"))
            return is_system_kms_key(session, region, resource_id)
        case "memorydb", "acl":
            return resource_id == "open-access"
        case "memorydb", "parameter-group":
            return resource_id.startswith("default.")
        case "memorydb", "user":
            return resource_id == "default"
        case "rds", "db-cluster-parameter-group" | "db-parameter-group":
            return resource_id.startswith("default.")
        case "rds", "option-group":
            return resource_id.startswith("default:")
        case "rds", "db-security-group" | "db-subnet-group":
            return resource_id == "default"
        case "s3", "storage-lens":
            return resource_id == "default-account-dashboard"
        case "xray", "sampling-rule":
            return resource_id == "Default"
        case _:
            return False


def is_system_kms_key(session: Session, region: str, resource_id: str) -> bool:
    return get_kms_key(session, region, resource_id).key_manager == "AWS"
