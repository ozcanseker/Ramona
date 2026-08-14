import json
from dataclasses import asdict, is_dataclass


class DataclassEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)

        if obj.__class__.__name__ == "Object":
            return "Object"
        
        return super().default(obj)