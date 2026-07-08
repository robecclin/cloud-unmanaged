from botocore import xform_name

from cloud_index.resource import ResourceType

TYPE_MAP: dict[tuple[str, str], tuple[str, str]] = {
    ("athena", "work-group"): ("athena", "workgroup"),
    ("cloudfront", "cloud-front-origin-access-identity"): ("cloudfront", "origin-access-identity"),
    ("ec2", "eip"): ("ec2", "elastic-ip"),
    ("ec2", "eip-association"): ("ec2", "elastic-ip-association"),
    # Ingress and egress rules are directions of one physical resource type, not separate resources
    ("ec2", "security-group-egress"): ("ec2", "security-group-rule"),
    ("ec2", "security-group-ingress"): ("ec2", "security-group-rule"),
}

SERVICE_MAP: dict[str, str] = {
    "elasticsearch": "opensearchservice",
    "kinesisfirehose": "firehose",
}


def parse_resource_type(type_name: str) -> ResourceType | None:
    """
    Parses a CloudFormation resource type into a canonical ResourceType,
    e.g. `AWS::KinesisFirehose::DeliveryStream` becomes `aws:firehose:delivery-stream`.

    Returns None for unsupported resource types, such as custom resources.
    """
    parts = type_name.split("::")
    if len(parts) != 3 or parts[0] != "AWS":
        return None

    service = parts[1].lower()
    kind = xform_name(parts[2], "-")
    if canonical := TYPE_MAP.get((service, kind)):
        service, kind = canonical
    else:
        service = SERVICE_MAP.get(service, service)
    return ResourceType("aws", service, kind)
