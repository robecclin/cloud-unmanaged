from rich.console import Console
from rich.table import Table
from typer import Exit, Option

from cloud_index.aws import get_available_regions
from cloud_unmanaged.app import app
from cloud_unmanaged.db import DatabaseError, transaction
from cloud_unmanaged.repository import load_physical

console = Console()
err_console = Console(stderr=True, highlight=False)


@app.command(help="Display indexed resources")
def show(
    include_system: bool = Option(False, "--include-system", help="Include system resources managed by AWS"),
    region: str | None = Option(None, "--region", help="Filter resources by AWS region"),
    unmanaged: bool = Option(False, "--unmanaged", help="Only show resources not managed by IaC"),
    managed: bool = Option(False, "--managed", help="Only show resources managed by IaC"),
) -> None:
    if managed and unmanaged:
        err_console.print("--managed and --unmanaged cannot be used together", style="red", markup=False)
        raise Exit(1)

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
            managed_filter = True if managed else False if unmanaged else None
            for resource in load_physical(
                connection,
                include_system=include_system,
                region=region,
                managed=managed_filter,
            ):
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
