from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from typer import Exit

from cloud_index.aws import index as index_aws
from cloud_index.error import CloudIndexError
from cloud_index.progress import ProgressEvent
from cloud_unmanaged.app import app
from cloud_unmanaged.db import DatabaseError, transaction
from cloud_unmanaged.repository import clear, save

console = Console()
err_console = Console(stderr=True, highlight=False)


@app.command(help="Discover and save resources using AWS Resource Explorer")
def index() -> None:
    count = 0
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

            def update_progress(event: ProgressEvent) -> None:
                if event.count is None:
                    progress.update(task, description=event.message)
                else:
                    progress.update(
                        task,
                        description=event.message,
                        count=f"(Found {event.count})",
                    )

            for resource in index_aws(update_progress):
                if save(connection, resource):
                    count += 1
    except (CloudIndexError, DatabaseError) as error:
        err_console.print(str(error), style="red", markup=False)
        raise Exit(1) from error

    noun = "resource" if count == 1 else "resources"
    console.print(f"Indexed {count} {noun}")
