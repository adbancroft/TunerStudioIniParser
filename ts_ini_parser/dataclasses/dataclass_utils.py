
from typing import Any, Type, Dict
from dataclasses import fields


def from_existing(existing, new_type: Type, new_fields: Dict[str, Any]):
    for f in fields(existing):
        new_fields[f.name] = getattr(existing, f.name)
    return new_type(**new_fields)
