from collections.abc import Callable
from typing import Any


Model = dict[str, Any]
Condition = Callable[[Model], bool]

