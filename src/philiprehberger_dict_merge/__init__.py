"""Deep merge dictionaries safely with conflict resolution."""

from __future__ import annotations

import copy
from enum import Enum
from typing import Any, Callable


__all__ = [
    "merge",
    "Strategy",
    "MergeConflictError",
    "flatten",
    "unflatten",
]


class Strategy(Enum):
    """Conflict resolution strategy for non-dict values."""

    REPLACE = "replace"
    KEEP_FIRST = "keep_first"
    ERROR = "error"
    CALLBACK = "callback"


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
    on_conflict: Callable[[str, Any, Any], Any] | None = None,
) -> dict[str, Any]:
    """Deep merge multiple dictionaries into a new dict.

    Later dicts take precedence over earlier ones (unless *strategy*
    says otherwise).

    Args:
        *dicts: Two or more dictionaries to merge.
        strategy: How to handle conflicting non-dict values.
        list_strategy: How to handle list values:
            ``"replace"`` (default), ``"append"``, ``"unique"``, or ``"concat"``.
        on_conflict: Required when *strategy* is ``Strategy.CALLBACK``. Called
            as ``on_conflict(full_key, left, right)`` and its return value is
            used as the merged value.

    Returns:
        A new merged dictionary.

    Raises:
        MergeConflictError: When *strategy* is ``ERROR`` and values conflict.
        ValueError: When *strategy* is ``CALLBACK`` and *on_conflict* is None.
    """
    if strategy is Strategy.CALLBACK and on_conflict is None:
        raise ValueError("Strategy.CALLBACK requires an on_conflict callback")

    if not dicts:
        return {}
    if len(dicts) == 1:
        return copy.deepcopy(dicts[0])

    result = copy.deepcopy(dicts[0])
    for d in dicts[1:]:
        _merge_into(result, d, strategy, list_strategy, on_conflict, prefix="")
    return result


def _merge_into(
    target: dict[str, Any],
    source: dict[str, Any],
    strategy: Strategy,
    list_strategy: str,
    on_conflict: Callable[[str, Any, Any], Any] | None,
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
            _merge_into(target_value, source_value, strategy, list_strategy, on_conflict, full_key)
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
            case Strategy.CALLBACK:
                assert on_conflict is not None  # validated in merge()
                target[key] = copy.deepcopy(on_conflict(full_key, target_value, source_value))


def flatten(data: dict[str, Any], sep: str = ".") -> dict[str, Any]:
    """Flatten a nested dict into one with separator-joined keys.

    Args:
        data: Nested dictionary to flatten.
        sep: Separator joining nested keys (default ``"."``).

    Returns:
        A flat dict where nested paths become single keys joined by *sep*.
        Non-dict values are kept as-is; lists are not descended into.
    """
    result: dict[str, Any] = {}

    def _walk(d: dict[str, Any], prefix: str) -> None:
        for key, value in d.items():
            full_key = f"{prefix}{sep}{key}" if prefix else key
            if isinstance(value, dict):
                _walk(value, full_key)
            else:
                result[full_key] = value

    _walk(data, "")
    return result


def unflatten(data: dict[str, Any], sep: str = ".") -> dict[str, Any]:
    """Reverse of :func:`flatten` — expand separator-joined keys into nested dicts.

    Args:
        data: Flat dictionary with separator-joined keys.
        sep: Separator that joins key segments (default ``"."``).

    Returns:
        A nested dictionary.

    Raises:
        ValueError: If a key conflicts with an existing non-dict value
            during expansion (e.g. ``{"a": 1, "a.b": 2}``).
    """
    result: dict[str, Any] = {}
    for key, value in data.items():
        parts = key.split(sep)
        target = result
        for part in parts[:-1]:
            existing = target.get(part)
            if existing is None:
                target[part] = {}
                target = target[part]
            elif isinstance(existing, dict):
                target = existing
            else:
                raise ValueError(
                    f"Cannot unflatten: key {key!r} conflicts with existing value at {part!r}"
                )
        last = parts[-1]
        if last in target and isinstance(target[last], dict) and not isinstance(value, dict):
            raise ValueError(
                f"Cannot unflatten: key {key!r} conflicts with existing nested dict"
            )
        target[last] = value
    return result


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
