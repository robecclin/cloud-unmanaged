from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceType:
    cloud: str
    service: str
    kind: str

    def __str__(self) -> str:
        return f"{self.cloud}:{self.service}:{self.kind}"


@dataclass(frozen=True)
class Resource:
    type: ResourceType
    account: str
    region: str
    identifier: str


@dataclass(frozen=True)
class PhysicalResource(Resource):
    system: bool


@dataclass(frozen=True)
class LogicalResource(Resource):
    locator: str
    name: str
