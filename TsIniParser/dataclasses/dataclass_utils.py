
from typing import Any, Type, Dict
from dataclasses import asdict


def from_existing(existing, type: Type, new_fields: Dict[str, Any]):
    fields = asdict(existing)
    for key, value in new_fields.items():
        fields[key] = value
    return type(**fields)
