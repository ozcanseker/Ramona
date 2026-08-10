from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ramona.modelcheck.classes.CheckResult import CheckResult
from ramona.modelcheck.classes.types import Condition

@dataclass
class ModelCheck:
    name: str
    description: str | None
    severity: str
    function: Callable[[dict], Any]
    conditions: list[Condition] = field(default_factory=list)
    results: list[CheckResult] = field(default_factory=list)
    filepath: Path | None = None

    def should_run(self, model: dict) -> bool:
        return all(
            condition(model) for condition in self.conditions
        )

    def run(self, model: dict) -> CheckResult:
        check_results=None

        if self.should_run(model):
            check_results=self.function(model)
        else:
            check_results=CheckResult.skipped()

        if not isinstance(check_results, CheckResult):
            raise Exception("Return of the modelcheck should be CheckResult.")

        check_results.model=model
        
        return check_results