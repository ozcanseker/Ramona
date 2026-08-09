from collections.abc import Callable

from .registry import registry, ModelCheck


def modelcheck(
    name: str,
    description: str | None = None,
):
    def decorator(function: Callable):

        check = ModelCheck(
            name=name,
            description=description,
            function=function,
        )

        registry.register(check)

        return function

    return decorator