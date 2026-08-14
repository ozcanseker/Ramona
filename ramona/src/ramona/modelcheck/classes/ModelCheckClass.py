from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ramona.model.classes.RamonaProject import Object
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

    def should_run(self, object: Object) -> bool:
        return all(
            condition(object) for condition in self.conditions
        )

    def run(self, object: Object) -> CheckResult:
        check_results=None

        if self.should_run(object):
            check_results=self.function(object)
        else:
            check_results=CheckResult.skipped()

        if not isinstance(check_results, CheckResult):
            raise Exception("Return of the modelcheck should be CheckResult.")

        check_results.object=object
        
        return check_results