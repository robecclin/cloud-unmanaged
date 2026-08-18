from collections.abc import Iterator
from datetime import UTC, datetime

from sqlalchemy import exists, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine import Connection

from cloud_index.resource import LogicalResource, PhysicalResource, ResourceType
from cloud_unmanaged.db import logical_resource_table, physical_resource_table


def current_timestamp() -> str:
    return datetime.now(UTC).replace(tzinfo=None).isoformat(sep=" ", timespec="milliseconds")


def save(connection: Connection, resource: PhysicalResource | LogicalResource) -> None:
    last_indexed_at = current_timestamp()
    if isinstance(resource, PhysicalResource):
        stmt = insert(physical_resource_table).values(
            account=resource.account,
            region=resource.region,
            cloud=resource.type.cloud,
            service=resource.type.service,
            type=resource.type.kind,
            identifier=resource.identifier,
            system=resource.system,
            last_indexed_at=last_indexed_at,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=(
                physical_resource_table.c.account,
                physical_resource_table.c.region,
                physical_resource_table.c.cloud,
                physical_resource_table.c.service,
                physical_resource_table.c.type,
                physical_resource_table.c.identifier,
            ),
            set_={
                "system": stmt.excluded.system,
                "last_indexed_at": stmt.excluded.last_indexed_at,
            },
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
            last_indexed_at=last_indexed_at,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=(logical_resource_table.c.locator, logical_resource_table.c.name),
            set_={
                "account": stmt.excluded.account,
                "region": stmt.excluded.region,
                "cloud": stmt.excluded.cloud,
                "service": stmt.excluded.service,
                "type": stmt.excluded.type,
                "identifier": stmt.excluded.identifier,
                "last_indexed_at": stmt.excluded.last_indexed_at,
            },
        )
    connection.execute(stmt)


def load_physical(
    connection: Connection,
    include_system: bool = False,
    region: str | None = None,
    managed: bool | None = None,
) -> Iterator[PhysicalResource]:
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
    for row in rows:
        yield PhysicalResource(
            account=row.account,
            region=row.region,
            type=ResourceType(row.cloud, row.service, row.type),
            identifier=row.identifier,
            system=row.system,
        )


def load_missing_logical(
    connection: Connection,
    region: str | None = None,
) -> Iterator[LogicalResource]:
    match_exists = exists().where(
        physical_resource_table.c.account == logical_resource_table.c.account,
        physical_resource_table.c.region == logical_resource_table.c.region,
        physical_resource_table.c.cloud == logical_resource_table.c.cloud,
        physical_resource_table.c.service == logical_resource_table.c.service,
        physical_resource_table.c.type == logical_resource_table.c.type,
        physical_resource_table.c.identifier == logical_resource_table.c.identifier,
    )
    stmt = (
        select(logical_resource_table)
        .where(~match_exists)
        .order_by(
            logical_resource_table.c.account,
            logical_resource_table.c.region,
            logical_resource_table.c.cloud,
            logical_resource_table.c.service,
            logical_resource_table.c.type,
            logical_resource_table.c.identifier,
            logical_resource_table.c.locator,
            logical_resource_table.c.name,
        )
    )
    if region:
        stmt = stmt.where(logical_resource_table.c.region == region)

    rows = connection.execute(stmt).mappings()
    for row in rows:
        yield LogicalResource(
            account=row.account,
            region=row.region,
            type=ResourceType(row.cloud, row.service, row.type),
            identifier=row.identifier,
            locator=row.locator,
            name=row.name,
        )
