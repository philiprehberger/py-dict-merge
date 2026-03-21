"""Deep merge dictionaries safely with conflict resolution."""

from __future__ import annotations

import copy
from enum import Enum
from typing import Any


__all__ = [
    "merge",
    "Strategy",
    "MergeConflictError",
]


class Strategy(Enum):
    """Conflict resolution strategy for non-dict values."""

    REPLACE = "replace"
    KEEP_FIRST = "keep_first"
    ERROR = "error"


class MergeConflictError(ValueError):
    """Raised when Strategy.ERROR encounters a conflict."""

    def __init__(self, key: str, left: Any, right: Any) -> None:
        self.key = key
        self.left = left
        self.right = right
        super().__init__(f"Merge conflict at '{key}': {left!r} vs {right!r}")


def merge(
    *dicts: dict[str, Any],
    strategy: Strategy = Strategy.REPLACE,
    list_strategy: str = "replace",
) -> dict[str, Any]:
    """Deep merge multiple dictionaries into a new dict.

    Later dicts take precedence over earlier ones (unless *strategy*
    says otherwise).

    Args:
        *dicts: Two or more dictionaries to merge.
        strategy: How to handle conflicting non-dict values.
        list_strategy: How to handle list values:
            ``"replace"`` (default), ``"append"``, ``"unique"``, or ``"concat"``.

    Returns:
        A new merged dictionary.

    Raises:
        MergeConflictError: When *strategy* is ``ERROR`` and values conflict.
    """
    if not dicts:
        return {}
    if len(dicts) == 1:
        return copy.deepcopy(dicts[0])

    result = copy.deepcopy(dicts[0])
    for d in dicts[1:]:
        _merge_into(result, d, strategy, list_strategy, prefix="")
    return result


def _merge_into(
    target: dict[str, Any],
    source: dict[str, Any],
    strategy: Strategy,
    list_strategy: str,
    prefix: str,
) -> None:
    for key, source_value in source.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if key not in target:
            target[key] = copy.deepcopy(source_value)
            continue

        target_value = target[key]

        # Both dicts → recurse
        if isinstance(target_value, dict) and isinstance(source_value, dict):
            _merge_into(target_value, source_value, strategy, list_strategy, full_key)
            continue

        # Both lists → apply list strategy
        if isinstance(target_value, list) and isinstance(source_value, list):
            target[key] = _merge_lists(target_value, source_value, list_strategy)
            continue

        # Scalar conflict
        match strategy:
            case Strategy.REPLACE:
                target[key] = copy.deepcopy(source_value)
            case Strategy.KEEP_FIRST:
                pass  # keep target_value
            case Strategy.ERROR:
                if target_value != source_value:
                    raise MergeConflictError(full_key, target_value, source_value)


def _merge_lists(left: list, right: list, strategy: str) -> list:
    match strategy:
        case "replace":
            return copy.deepcopy(right)
        case "append" | "concat":
            return copy.deepcopy(left) + copy.deepcopy(right)
        case "unique":
            seen: set[int] = set()
            result: list = []
            for item in [*left, *right]:
                item_id = id(item) if not isinstance(item, (str, int, float, bool, type(None))) else hash(item)
                if item_id not in seen:
                    seen.add(item_id)
                    result.append(copy.deepcopy(item))
            return result
        case _:
            return copy.deepcopy(right)
