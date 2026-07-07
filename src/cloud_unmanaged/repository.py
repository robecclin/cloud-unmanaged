from sqlalchemy import delete, exists, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine import Connection

from cloud_index.resource import LogicalResource, PhysicalResource, ResourceType
from cloud_unmanaged.db import logical_resource_table, physical_resource_table


def clear(connection: Connection) -> None:
    connection.execute(delete(physical_resource_table))
    connection.execute(delete(logical_resource_table))


def save(connection: Connection, resource: PhysicalResource | LogicalResource) -> bool:
    if isinstance(resource, PhysicalResource):
        stmt = insert(physical_resource_table).values(
            account=resource.account,
            region=resource.region,
            cloud=resource.type.cloud,
            service=resource.type.service,
            type=resource.type.kind,
            identifier=resource.identifier,
            system=resource.system,
        )
    else:
        stmt = insert(logical_resource_table).values(
            account=resource.account,
            region=resource.region,
            cloud=resource.type.cloud,
            service=resource.type.service,
            type=resource.type.kind,
            identifier=resource.identifier,
            locator=resource.locator,
            name=resource.name,
        )
    result = connection.execute(stmt.on_conflict_do_nothing())
    return result.rowcount > 0


def load_physical(
    connection: Connection,
    include_system: bool = False,
    region: str | None = None,
    managed: bool | None = None,
) -> list[PhysicalResource]:
    stmt = select(physical_resource_table).order_by(
        physical_resource_table.c.account,
        physical_resource_table.c.region,
        physical_resource_table.c.cloud,
        physical_resource_table.c.service,
        physical_resource_table.c.type,
        physical_resource_table.c.identifier,
    )
    if not include_system:
        stmt = stmt.where(physical_resource_table.c.system.is_(False))
    if region:
        stmt = stmt.where(physical_resource_table.c.region == region)
    if managed is not None:
        match_exists = exists().where(
            logical_resource_table.c.account == physical_resource_table.c.account,
            logical_resource_table.c.region == physical_resource_table.c.region,
            logical_resource_table.c.cloud == physical_resource_table.c.cloud,
            logical_resource_table.c.service == physical_resource_table.c.service,
            logical_resource_table.c.type == physical_resource_table.c.type,
            logical_resource_table.c.identifier == physical_resource_table.c.identifier,
        )
        stmt = stmt.where(match_exists if managed else ~match_exists)

    rows = connection.execute(stmt).mappings()
    return [
        PhysicalResource(
            account=row.account,
            region=row.region,
            type=ResourceType(row.cloud, row.service, row.type),
            identifier=row.identifier,
            system=row.system,
        )
        for row in rows
    ]
