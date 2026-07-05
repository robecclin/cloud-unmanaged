from cloud_unmanaged.app import app
from cloud_unmanaged.command.index import index
from cloud_unmanaged.command.show import show


@app.callback()
def callback() -> None:
    """Identify cloud resources not managed by infrastructure as code (IaC)"""


__all__ = ["app", "callback", "index", "show"]

if __name__ == "__main__":
    app()  # pragma: no cover
