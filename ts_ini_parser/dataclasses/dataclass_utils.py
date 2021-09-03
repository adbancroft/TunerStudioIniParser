
from typing import Any, Type, Dict
from dataclasses import fields


def from_existing(existing, new_type: Type, new_fields: Dict[str, Any]):
    for field in fields(existing):
        new_fields[field.name] = getattr(existing, field.name)
    return new_type(**new_fields)
