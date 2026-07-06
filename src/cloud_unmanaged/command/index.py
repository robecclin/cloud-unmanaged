from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from typer import Exit

from cloud_index.aws import index as index_aws
from cloud_index.cloudformation import index as index_cloudformation
from cloud_index.error import CloudIndexError
from cloud_index.progress import ProgressEvent
from cloud_index.resource import PhysicalResource
from cloud_unmanaged.app import app
from cloud_unmanaged.db import DatabaseError, transaction
from cloud_unmanaged.repository import clear, save

console = Console()
err_console = Console(stderr=True, highlight=False)


@app.command(help="Discover and save resources using AWS Resource Explorer and CloudFormation")
def index() -> None:
    physical_count = 0
    logical_count = 0
    try:
        with (
            transaction() as connection,
            Progress(
                SpinnerColumn(),
                TextColumn("{task.description}"),
                TextColumn("{task.fields[count]}"),
                console=err_console,
                transient=True,
                disable=not err_console.is_terminal,
            ) as progress,
        ):
            clear(connection)
            task = progress.add_task("Indexing AWS resources", count="(Found 0)")
            found = 0

            def update_progress(event: ProgressEvent) -> None:
                progress.update(task, description=event.message)

            for indexer in (index_aws, index_cloudformation):
                for resource in indexer(update_progress):
                    found += 1
                    progress.update(task, count=f"(Found {found})")
                    if save(connection, resource):
                        if isinstance(resource, PhysicalResource):
                            physical_count += 1
                        else:
                            logical_count += 1
    except (CloudIndexError, DatabaseError) as error:
        err_console.print(str(error), style="red", markup=False)
        raise Exit(1) from error

    total_count = physical_count + logical_count
    noun = "resource" if total_count == 1 else "resources"
    console.print(f"Indexed {total_count} {noun} ({physical_count} physical, {logical_count} logical)")
