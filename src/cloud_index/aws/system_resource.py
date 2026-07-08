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
    match resource_type.service:
        case "apprunner" if resource_type.kind == "auto-scaling-configuration":
            return resource_id.startswith("DefaultConfiguration/")
        case "athena":
            match resource_type.kind:
                case "data-catalog":
                    return resource_id == "AwsDataCatalog"
                case "workgroup":
                    return resource_id == "primary"
                case _:
                    return False
        case "backup" if resource_type.kind == "backup-vault":
            return resource_id == "Default"
        case "elasticache":
            match resource_type.kind:
                case "user":
                    return resource_id == "default"
                case _:
                    return False
        case "events" if resource_type.kind == "event-bus":
            return resource_id == "default"
        case "iam" if resource_type.kind == "role":
            return resource_id.startswith("aws-service-role/")
        case "glue" if resource_type.kind == "database":
            return resource_id == "default"
        case "kms":
            # Keys are the only KMS resource type returned by AWS Resource Explorer
            progress(ProgressEvent(f"Checking KMS key {resource_id} in {region}"))
            return is_system_kms_key(session, region, resource_id)
        case "memorydb":
            match resource_type.kind:
                case "acl":
                    return resource_id == "open-access"
                case "parameter-group":
                    return resource_id.startswith("default.")
                case "user":
                    return resource_id == "default"
                case _:
                    return False
        case "rds":
            match resource_type.kind:
                case "db-cluster-parameter-group" | "db-parameter-group":
                    return resource_id.startswith("default.")
                case "option-group":
                    return resource_id.startswith("default:")
                case "db-security-group" | "db-subnet-group":
                    return resource_id == "default"
                case _:
                    return False
        case "s3" if resource_type.kind == "storage-lens":
            return resource_id == "default-account-dashboard"
        case "xray" if resource_type.kind == "sampling-rule":
            return resource_id == "Default"
        case _:
            return False


def is_system_kms_key(session: Session, region: str, resource_id: str) -> bool:
    return get_kms_key(session, region, resource_id).key_manager == "AWS"
