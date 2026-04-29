import pytest
from philiprehberger_dict_merge import (
    MergeConflictError,
    Strategy,
    flatten,
    merge,
    unflatten,
)


def test_simple_merge():
    result = merge({"a": 1}, {"b": 2})
    assert result == {"a": 1, "b": 2}


def test_deep_merge():
    base = {"db": {"host": "localhost", "port": 5432}}
    override = {"db": {"port": 3306, "name": "mydb"}}
    result = merge(base, override)
    assert result == {"db": {"host": "localhost", "port": 3306, "name": "mydb"}}


def test_override_scalar():
    result = merge({"a": 1}, {"a": 2})
    assert result == {"a": 2}


def test_keep_first():
    result = merge({"a": 1}, {"a": 2}, strategy=Strategy.KEEP_FIRST)
    assert result == {"a": 1}


def test_error_on_conflict():
    with pytest.raises(MergeConflictError):
        merge({"a": 1}, {"a": 2}, strategy=Strategy.ERROR)


def test_no_conflict_with_error():
    result = merge({"a": 1}, {"a": 1}, strategy=Strategy.ERROR)
    assert result == {"a": 1}


def test_multiple_dicts():
    result = merge({"a": 1}, {"b": 2}, {"c": 3})
    assert result == {"a": 1, "b": 2, "c": 3}


def test_list_replace():
    result = merge({"a": [1, 2]}, {"a": [3, 4]})
    assert result == {"a": [3, 4]}


def test_list_append():
    result = merge({"a": [1, 2]}, {"a": [3, 4]}, list_strategy="append")
    assert result == {"a": [1, 2, 3, 4]}


def test_list_unique():
    result = merge({"a": [1, 2, 3]}, {"a": [2, 3, 4]}, list_strategy="unique")
    assert result == {"a": [1, 2, 3, 4]}


def test_non_mutating():
    original = {"a": {"b": 1}}
    merge(original, {"a": {"b": 2}})
    assert original == {"a": {"b": 1}}


def test_empty_merge():
    assert merge() == {}


def test_single_dict():
    result = merge({"a": 1})
    assert result == {"a": 1}


def test_callback_picks_larger_int():
    result = merge(
        {"a": 1, "b": 5},
        {"a": 4, "b": 2},
        strategy=Strategy.CALLBACK,
        on_conflict=lambda _key, left, right: max(left, right),
    )
    assert result == {"a": 4, "b": 5}


def test_callback_receives_full_key_path():
    seen_keys: list[str] = []

    def cb(key: str, left, right):
        seen_keys.append(key)
        return right

    merge(
        {"db": {"host": "a", "port": 1}},
        {"db": {"host": "b", "port": 2}},
        strategy=Strategy.CALLBACK,
        on_conflict=cb,
    )
    assert "db.host" in seen_keys
    assert "db.port" in seen_keys


def test_callback_can_return_complex_value():
    result = merge(
        {"tags": "a"},
        {"tags": "b"},
        strategy=Strategy.CALLBACK,
        on_conflict=lambda _k, left, right: [left, right],
    )
    assert result == {"tags": ["a", "b"]}


def test_callback_strategy_requires_callback():
    with pytest.raises(ValueError, match="requires an on_conflict callback"):
        merge({"a": 1}, {"a": 2}, strategy=Strategy.CALLBACK)


def test_flatten_simple():
    assert flatten({"a": 1, "b": 2}) == {"a": 1, "b": 2}


def test_flatten_nested():
    assert flatten({"db": {"host": "x", "port": 5432}}) == {
        "db.host": "x",
        "db.port": 5432,
    }


def test_flatten_deep():
    assert flatten({"a": {"b": {"c": 1}}}) == {"a.b.c": 1}


def test_flatten_custom_sep():
    assert flatten({"a": {"b": 1}}, sep="/") == {"a/b": 1}


def test_flatten_empty_dict():
    assert flatten({}) == {}


def test_flatten_does_not_descend_into_lists():
    assert flatten({"a": [1, 2, 3]}) == {"a": [1, 2, 3]}


def test_unflatten_simple():
    assert unflatten({"a": 1, "b": 2}) == {"a": 1, "b": 2}


def test_unflatten_nested():
    assert unflatten({"db.host": "x", "db.port": 5432}) == {
        "db": {"host": "x", "port": 5432}
    }


def test_unflatten_deep():
    assert unflatten({"a.b.c": 1}) == {"a": {"b": {"c": 1}}}


def test_unflatten_custom_sep():
    assert unflatten({"a/b": 1}, sep="/") == {"a": {"b": 1}}


def test_flatten_unflatten_round_trip():
    original = {"db": {"host": "x", "port": 5432}, "debug": True}
    assert unflatten(flatten(original)) == original


def test_unflatten_conflict_raises():
    with pytest.raises(ValueError):
        unflatten({"a": 1, "a.b": 2})


def test_merge_with_flatten():
    a = flatten({"db": {"host": "x", "port": 5432}})
    b = flatten({"db": {"port": 3306}})
    merged = merge(a, b)
    assert unflatten(merged) == {"db": {"host": "x", "port": 3306}}
