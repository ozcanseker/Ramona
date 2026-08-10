from ramona.modelcheck.classes.types import Condition
from ramona.modelcheck.classes.ModelCheckClass import ModelCheck

def modelcheck(
    name: str,
    description: str | None = None,
    severity: str | None = None,
    conditions: list[Condition] | None = None,
):
    def decorator(function):

        function.__modelcheck__ = ModelCheck(
            name=name,
            description=description,
            severity=severity,
            function=function,
            conditions=conditions
        )

        return function

    return decorator