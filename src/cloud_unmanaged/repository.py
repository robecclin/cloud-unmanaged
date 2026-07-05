from sqlalchemy import delete, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine import Connection

from cloud_index.resource import Resource, ResourceType
from cloud_unmanaged.db import resource_table


def clear(connection: Connection) -> None:
    connection.execute(delete(resource_table))


def save(connection: Connection, resource: Resource) -> bool:
    stmt = insert(resource_table).values(
        account=resource.account,
        region=resource.region,
        cloud=resource.type.cloud,
        service=resource.type.service,
        type=resource.type.kind,
        identifier=resource.identifier,
        system=resource.system,
    )
    result = connection.execute(stmt.on_conflict_do_nothing())
    return result.rowcount > 0


def load(connection: Connection, include_system: bool = False, region: str | None = None) -> list[Resource]:
    stmt = select(resource_table).order_by(
        resource_table.c.account,
        resource_table.c.region,
        resource_table.c.cloud,
        resource_table.c.service,
        resource_table.c.type,
        resource_table.c.identifier,
    )
    if not include_system:
        stmt = stmt.where(resource_table.c.system.is_(False))
    if region:
        stmt = stmt.where(resource_table.c.region == region)

    rows = connection.execute(stmt).mappings()
    return [
        Resource(
            account=row.account,
            region=row.region,
            type=ResourceType(row.cloud, row.service, row.type),
            identifier=row.identifier,
            system=row.system,
        )
        for row in rows
    ]
