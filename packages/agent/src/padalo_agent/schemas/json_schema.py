from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import BaseModel


def strict_json_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Convert a Pydantic schema into the strict subset expected by Responses."""

    schema = deepcopy(model.model_json_schema())
    _normalize(schema)
    return schema


def _normalize(value: Any) -> None:
    if isinstance(value, dict):
        if value.get("type") == "object":
            properties = value.get("properties")
            if isinstance(properties, dict):
                value["required"] = list(properties)
            value["additionalProperties"] = False

        value.pop("default", None)
        for nested in value.values():
            _normalize(nested)
    elif isinstance(value, list):
        for nested in value:
            _normalize(nested)
