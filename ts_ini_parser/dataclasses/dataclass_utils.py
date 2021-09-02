
from typing import Any, Type, Dict
from dataclasses import asdict


def from_existing(existing, new_type: Type, new_fields: Dict[str, Any]):
    fields = asdict(existing)
    for key, value in new_fields.items():
        fields[key] = value
    return new_type(**fields)
