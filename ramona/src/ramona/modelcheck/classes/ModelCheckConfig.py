from dataclasses import dataclass, field
from .types import Condition


@dataclass
class ModelCheckConfig:
    severity: str = "error"
    conditions: list[Condition] = field(default_factory=list)

