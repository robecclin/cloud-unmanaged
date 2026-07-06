from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    message: str


type ProgressReporter = Callable[[ProgressEvent], None]
