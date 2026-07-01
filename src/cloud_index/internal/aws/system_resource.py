from cloud_index.resource import ResourceType


def is_system_resource(resource_type: ResourceType, resource_id: str) -> bool:
    """
    Returns true if a resource is a system resource, i.e., managed by AWS and cannot be deleted.
    This does not include implicit resources, which are resources that exist because they are
    created automatically by another resource type, e.g., a default subnet in a VPC.
    """
    match resource_type.service:
        case "apprunner" if resource_type.kind == "autoscalingconfiguration":
            return resource_id.startswith("DefaultConfiguration/")
        case "athena":
            match resource_type.kind:
                case "datacatalog":
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
        case "iam":
            match resource_type.kind:
                case "policy":
                    return resource_id.startswith("service-role/")
                case "role":
                    return resource_id.startswith("aws-service-role/")
                case _:
                    return False
        case "glue" if resource_type.kind == "database":
            return resource_id == "default"
        case "memorydb":
            match resource_type.kind:
                case "acl":
                    return resource_id == "open-access"
                case "parametergroup":
                    return resource_id.startswith("default.")
                case "user":
                    return resource_id == "default"
                case _:
                    return False
        case "rds":
            match resource_type.kind:
                case "cluster-pg" | "pg":
                    return resource_id.startswith("default.")
                case "og":
                    return resource_id.startswith("default:")
                case "secgrp" | "subgrp":
                    return resource_id == "default"
                case _:
                    return False
        case "s3" if resource_type.kind == "storage-lens":
            return resource_id == "default-account-dashboard"
        case "xray" if resource_type.kind == "sampling-rule":
            return resource_id == "Default"
        case _:
            return False
