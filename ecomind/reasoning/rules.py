"""Loading and matching the transparent environmental relationship rules."""

import json
from pathlib import Path
from typing import Any

KNOWLEDGE_PATH = Path(__file__).parents[1] / "data" / "environmental_knowledge.json"


def load_rules() -> list[dict[str, Any]]:
    return json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))["relationships"]


def _matches_value(value: Any, expected: Any) -> bool:
    if value is None or value == "":
        return False
    if isinstance(expected, dict):
        try:
            number = float(value)
        except (TypeError, ValueError):
            return False
        return ("min" not in expected or number >= expected["min"]) and ("max" not in expected or number <= expected["max"])
    return str(value).strip().lower() in {str(item).lower() for item in expected}


def matching_rules(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [rule for rule in load_rules() if all(_matches_value(data.get(key), value) for key, value in rule["conditions"].items())]
