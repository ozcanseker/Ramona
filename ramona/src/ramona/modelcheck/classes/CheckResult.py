from dataclasses import dataclass
from enum import Enum

from ramona.model.classes.RamonaProject import Object


class CheckStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class CheckResult:
    status: CheckStatus
    message: str | None = None
    object: Object | None = None

    @classmethod
    def success(cls):
        return cls(status=CheckStatus.PASSED)

    @classmethod
    def failure(cls, message: str):
        return cls(status=CheckStatus.FAILED, message=message)

    @classmethod
    def skipped(cls):
        return cls(status=CheckStatus.SKIPPED)
