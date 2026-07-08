from cloud_index.aws.arn import parse_arn
from cloud_index.resource import ResourceType


def parse_identifier(resource_type: ResourceType, physical_id: str) -> str | None:
    """
    Parses the physical resource id reported by CloudFormation into the resource identifier
    used by AWS Resource Explorer.

    Returns None when the physical id does not identify the resource.
    """
    try:
        return parse_arn(physical_id).resource_id
    except ValueError:
        pass

    match resource_type.service:
        case "ec2" if resource_type.kind == "security-group-rule" and not physical_id.startswith("sgr-"):
            # Older templates report a pseudo id that does not identify the rule
            return None
        case "sqs" if resource_type.kind == "queue":
            # The physical id is the queue URL
            return physical_id.rsplit("/", 1)[-1]
        case _:
            return physical_id
