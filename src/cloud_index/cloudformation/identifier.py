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

    match resource_type.service, resource_type.kind:
        case "ec2", "security-group-rule" if not physical_id.startswith("sgr-"):
            # Older templates report a pseudo id that does not identify the rule
            return None
        case "sqs", "queue":
            # The physical id is the queue URL
            return physical_id.rsplit("/", 1)[-1]
        case "ssm", "parameter":
            # Normalize to match created resource, which retains a slash prefix
            # only if it is hierarchical
            name = physical_id.removeprefix("/")
            return "/" + name if "/" in name else name
        case _:
            return physical_id
