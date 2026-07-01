from cloud_index.resource import ResourceType


def parse_resource_type(resource_type: str) -> ResourceType:
    service, type = resource_type.split(":", 1)
    return ResourceType("aws", service, type)
