from rich.console import Console
from rich.table import Table
from typer import Exit, Option

from cloud_index.aws import get_available_regions
from cloud_unmanaged.app import app
from cloud_unmanaged.db import DatabaseError, transaction
from cloud_unmanaged.repository import get_latest_index_run_id, load_missing_logical

console = Console()
err_console = Console(stderr=True, highlight=False)


@app.command(help="Display resources defined by IaC that appear to be missing in the cloud")
def show_missing(
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
    table.add_column("Locator")
    table.add_column("Name")

    try:
        with transaction() as connection:
            index_run_id = get_latest_index_run_id(connection)
            if index_run_id is None:
                console.print("No index runs found")
                raise Exit()

            for resource in load_missing_logical(connection, index_run_id, region=region):
                table.add_row(
                    resource.account,
                    resource.region,
                    str(resource.type),
                    resource.identifier,
                    resource.locator,
                    resource.name,
                )
    except DatabaseError as error:
        err_console.print(str(error), style="red", markup=False)
        raise Exit(1) from error

    if table.row_count == 0:
        console.print("No resources found")
        raise Exit()

    console.print(table)
