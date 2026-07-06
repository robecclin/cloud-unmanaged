from dataclasses import dataclass


@dataclass
class ResourceType:
    cloud: str
    service: str
    kind: str

    def __str__(self) -> str:
        return f"{self.cloud}:{self.service}:{self.kind}"


@dataclass
class Resource:
    type: ResourceType
    account: str
    region: str
    identifier: str


@dataclass
class PhysicalResource(Resource):
    system: bool


@dataclass
class LogicalResource(Resource):
    locator: str
    name: str
