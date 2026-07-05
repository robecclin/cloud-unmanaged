from rich.console import Console
from rich.table import Table
from typer import Exit, Option

from cloud_index.aws import get_available_regions
from cloud_unmanaged.app import app
from cloud_unmanaged.db import DatabaseError, transaction
from cloud_unmanaged.repository import load

console = Console()
err_console = Console(stderr=True, highlight=False)


@app.command(help="Display indexed resources")
def show(
    include_system: bool = Option(False, "--include-system", help="Include system resources managed by AWS"),
    region: str | None = Option(None, "--region", help="Filter resources by AWS region"),
) -> None:
    if region and region not in get_available_regions():
        err_console.print(f"Invalid region: {region}", style="red", markup=False)
        raise Exit(1)

    table = Table()
    table.add_column("Account")
    table.add_column("Region")
    table.add_column("Type")
    table.add_column("ID")

    try:
        with transaction() as connection:
            for resource in load(connection, include_system=include_system, region=region):
                table.add_row(
                    resource.account,
                    resource.region,
                    str(resource.type),
                    resource.identifier,
                )
    except DatabaseError as error:
        err_console.print(str(error), style="red", markup=False)
        raise Exit(1) from error

    if table.row_count == 0:
        console.print("No resources found")
        raise Exit()

    console.print(table)
