from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class CheckResult:
    check: str
    success: bool
    message: str
    path: str | None = None


@dataclass
class CheckContext:
    model: dict
    source_file: str
    environment: str
    config: dict


class ModelChecker:
    def __init__(self):
        self.checks: list[Callable] = []

    def register(self, check):
        self.checks.append(check)
        return check

    def run(self, model: Any) -> list[CheckResult]:
        results = []

        for check in self.checks:
            result = check(model)

            if isinstance(result, CheckResult):
                results.append(result)
            else:
                results.append(
                    CheckResult(
                        check=check.__name__,
                        success=bool(result),
                        message="Check failed" if not result else "OK",
                    )
                )

        return results


def run_modelcheck(args):

    models = load_models(args.input)

    runner = CheckRunner(
        strict=args.strict,
    )

    results = runner.run(models)

    for result in results:
        print(result)

    if any(result.failed for result in results):
        return 1

    return 0