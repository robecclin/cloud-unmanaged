from boto3 import Session
from rich.console import Console
from rich.table import Table
from typer import Exit, Option

from cloud_index.aws import get_available_regions
from cloud_index.aws import index as index_aws
from cloud_index.error import CloudIndexError
from cloud_unmanaged.app import app

console = Console()
err_console = Console(stderr=True)


@app.command(help="Discover resources using AWS Resource Explorer")
def index(
    include_system: bool = Option(False, "--include-system", help="Include system resources managed by AWS"),
    region: str | None = Option(None, "--region", help="Filter resources by AWS region"),
) -> None:
    if region and region not in get_available_regions():
        err_console.print(f"Invalid region: {region}", style="red", markup=False)
        raise Exit(1)

    session = Session()

    table = Table()
    table.add_column("Account")
    table.add_column("Region")
    table.add_column("Type")
    table.add_column("ID")

    try:
        for resource in index_aws(session):
            if not include_system and resource.system:
                continue
            if region and resource.region != region:
                continue
            table.add_row(
                resource.account,
                resource.region,
                str(resource.type),
                resource.identifier,
            )
    except CloudIndexError as error:
        err_console.print(str(error), style="red", markup=False)
        raise Exit(1) from error

    if table.row_count == 0:
        console.print("No resources found")
        raise Exit()

    console.print(table)
