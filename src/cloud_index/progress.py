from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    message: str
    count: int | None = None


type ProgressReporter = Callable[[ProgressEvent], None]
