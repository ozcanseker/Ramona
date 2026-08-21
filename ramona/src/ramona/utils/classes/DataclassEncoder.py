import json
from dataclasses import asdict, is_dataclass
from pathlib import Path


class DataclassEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)

        if obj.__class__.__name__ == "Object":
            return "Object"

        if isinstance(obj, Path) :
            return str(obj)
        
        return super().default(obj)