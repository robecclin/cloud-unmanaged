from collections.abc import Iterator
from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlalchemy import exists, select, update
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine import Connection

from cloud_index.resource import LogicalResource, PhysicalResource, ResourceType
from cloud_unmanaged.db import index_run_table, logical_resource_table, physical_resource_table


def current_timestamp() -> str:
    return datetime.now(UTC).replace(tzinfo=None).isoformat(sep=" ", timespec="milliseconds")


def start_index_run(connection: Connection) -> UUID:
    index_run_id = uuid7()
    connection.execute(
        insert(index_run_table).values(
            id=index_run_id,
            started_at=current_timestamp(),
            ended_at="",
        )
    )
    return index_run_id


def end_index_run(connection: Connection, index_run_id: UUID) -> None:
    connection.execute(
        update(index_run_table).where(index_run_table.c.id == index_run_id).values(ended_at=current_timestamp())
    )


def get_latest_index_run_id(connection: Connection) -> UUID | None:
    stmt = (
        select(index_run_table.c.id)
        .where(index_run_table.c.ended_at != "")
        .order_by(index_run_table.c.ended_at.desc(), index_run_table.c.id.desc())
        .limit(1)
    )
    return connection.execute(stmt).scalar_one_or_none()


def save(connection: Connection, index_run_id: UUID, resource: PhysicalResource | LogicalResource) -> bool:
    if isinstance(resource, PhysicalResource):
        stmt = insert(physical_resource_table).values(
            index_run_id=index_run_id,
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
            index_run_id=index_run_id,
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
    index_run_id: UUID,
    include_system: bool = False,
    region: str | None = None,
    managed: bool | None = None,
) -> Iterator[PhysicalResource]:
    stmt = (
        select(physical_resource_table)
        .where(physical_resource_table.c.index_run_id == index_run_id)
        .order_by(
            physical_resource_table.c.account,
            physical_resource_table.c.region,
            physical_resource_table.c.cloud,
            physical_resource_table.c.service,
            physical_resource_table.c.type,
            physical_resource_table.c.identifier,
        )
    )
    if not include_system:
        stmt = stmt.where(physical_resource_table.c.system.is_(False))
    if region:
        stmt = stmt.where(physical_resource_table.c.region == region)
    if managed is not None:
        match_exists = exists().where(
            logical_resource_table.c.index_run_id == physical_resource_table.c.index_run_id,
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
    index_run_id: UUID,
    region: str | None = None,
) -> Iterator[LogicalResource]:
    match_exists = exists().where(
        physical_resource_table.c.index_run_id == logical_resource_table.c.index_run_id,
        physical_resource_table.c.account == logical_resource_table.c.account,
        physical_resource_table.c.region == logical_resource_table.c.region,
        physical_resource_table.c.cloud == logical_resource_table.c.cloud,
        physical_resource_table.c.service == logical_resource_table.c.service,
        physical_resource_table.c.type == logical_resource_table.c.type,
        physical_resource_table.c.identifier == logical_resource_table.c.identifier,
    )
    stmt = (
        select(logical_resource_table)
        .where(
            logical_resource_table.c.index_run_id == index_run_id,
            ~match_exists,
        )
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
