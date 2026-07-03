from dataclasses import dataclass


@dataclass
class Arn:
    partition: str
    service: str
    region: str | None
    account_id: str | None
    resource_type: str | None
    resource_id: str


def parse_arn(arn: str) -> Arn:
    """
    Parses an ARN into its components.
    """
    parts = arn.split(":", 5)
    if len(parts) != 6:
        raise ValueError(f"Invalid ARN: {arn}")
    if parts[0] != "arn":
        raise ValueError(f"Invalid ARN: {arn}")

    region: str | None
    account_id: str | None

    _, partition, service, region, account_id, resource = parts

    region = region or None
    account_id = account_id or None

    resource_type, resource_id = parse_resource(service, resource)

    return Arn(partition, service, region, account_id, resource_type, resource_id)


def parse_resource(service: str, resource: str) -> tuple[str | None, str]:
    """
    Parses the resource part of an ARN into resource type and resource ID.

    A resource type and resource ID are separated by either a `/` or a `:`, the first occurrence of
    either character is used as the separator. If neither character is present, the entire resource
    string is treated as the resource ID.

    :param resource: The resource part of the ARN.
    :return: A tuple containing the resource type (or None if not present) and the resource ID.
    """
    colon = resource.find(":")
    slash = resource.find("/")

    if colon == -1 and slash == -1:
        return (None, resource)

    if slash == -1:
        separator = ":"
    elif colon == -1:
        separator = "/"
    else:
        separator = ":" if colon < slash else "/"

    resource_type, resource_id = resource.split(separator, 1)

    # Special handling for SSM parameters
    if service == "ssm" and resource_type == "parameter":
        resource_id = "/" + resource_id

    return (resource_type, resource_id)
