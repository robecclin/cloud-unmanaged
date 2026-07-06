from botocore import xform_name

from cloud_index.resource import ResourceType


def parse_resource_type(type_name: str) -> ResourceType | None:
    """
    Parses a CloudFormation resource type such as `AWS::EC2::VPC` into a ResourceType.

    Returns None for unsupported resource types, such as custom resources.
    """
    parts = type_name.split("::")
    if len(parts) != 3 or parts[0] != "AWS":
        return None

    service = parts[1].lower()
    kind = xform_name(parts[2], "-")
    return ResourceType("aws", service, kind)
