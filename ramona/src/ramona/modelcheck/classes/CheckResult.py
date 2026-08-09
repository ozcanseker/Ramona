from dataclasses import dataclass


@dataclass
class CheckResult:
    passed: bool
    message: str | None = None
    path: str | None = None

    @classmethod
    def success(cls):
        return cls(passed=True)

    @classmethod
    def failure(
        cls,
        message: str,
        path: str | None = None,
    ):
        return cls(
            passed=False,
            message=message,
            path=path,
        )