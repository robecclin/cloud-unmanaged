from cloud_index.resource import ResourceType


def parse_identifier(resource_type: ResourceType, resource_id: str) -> str:
    """
    Parses the resource ID of an ARN into the identifier that names the resource.
    """
    match resource_type.service, resource_type.kind:
        case "ssm", "parameter" if "/" in resource_id:
            # Hierarchical parameter names are fully qualified with a leading slash
            return "/" + resource_id
        case "autoscaling", "auto-scaling-group":
            # The group name is prefixed with a uuid and "autoScalingGroupName"
            return resource_id.split(":autoScalingGroupName/", 1)[-1]
        case _:
            return resource_id
