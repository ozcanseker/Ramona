
from dataclasses import dataclass
from collections.abc import Callable


@dataclass
class ModelCheck:
    name: str
    description: str | None
    function: Callable


class CheckRegistry:

    def __init__(self):
        self._checks: list[ModelCheck] = []

    def register(self, check: ModelCheck):
        self._checks.append(check)

    def get_checks(self) -> list[ModelCheck]:
        return self._checks


registry = CheckRegistry()