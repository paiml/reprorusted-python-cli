"""Tests for func_maybe_cli.py"""

import pytest
from func_maybe_cli import (
    Nothing,
    Some,
    cat_maybes,
    from_optional,
    lift,
    lift2,
    maybe,
    nothing,
    safe_div,
    safe_float,
    safe_get,
    safe_head,
    safe_index,
    safe_int,
    safe_last,
    sequence,
    simulate_maybe,
    some,
    traverse,
)


class TestSome:
    def test_create(self):
        s = Some(5)
        assert s.value == 5

    def test_is_some(self):
        assert Some(5).is_some()

    def test_is_none(self):
        assert not Some(5).is_none()

    def test_map(self):
        result = Some(5).map(lambda x: x * 2)
        assert result == Some(10)

    def test_flat_map(self):
        result = Some(5).flat_map(lambda x: Some(x * 2))
        assert result == Some(10)

    def test_flat_map_to_nothing(self):
        result = Some(5).flat_map(lambda x: nothing())
        assert result.is_none()

    def test_filter_pass(self):
        result = Some(6).filter(lambda x: x % 2 == 0)
        assert result == Some(6)

    def test_filter_fail(self):
        result = Some(5).filter(lambda x: x % 2 == 0)
        assert result.is_none()

    def test_get(self):
        assert Some(5).get() == 5

    def test_get_or(self):
        assert Some(5).get_or(0) == 5

    def test_get_or_else(self):
        assert Some(5).get_or_else(lambda: 0) == 5

    def test_or_else(self):
        result = Some(5).or_else(lambda: Some(10))
        assert result == Some(5)

    def test_to_list(self):
        assert Some(5).to_list() == [5]

    def test_repr(self):
        assert repr(Some(5)) == "Some(5)"

    def test_equality(self):
        assert Some(5) == Some(5)
        assert Some(5) != Some(10)


class TestNothing:
    def test_is_some(self):
        assert not Nothing().is_some()

    def test_is_none(self):
        assert Nothing().is_none()

    def test_map(self):
        result = Nothing().map(lambda x: x * 2)
        assert result.is_none()

    def test_flat_map(self):
        result = Nothing().flat_map(lambda x: Some(x * 2))
        assert result.is_none()

    def test_filter(self):
        result = Nothing().filter(lambda x: True)
        assert result.is_none()

    def test_get_raises(self):
        with pytest.raises(ValueError):
            Nothing().get()

    def test_get_or(self):
        assert Nothing().get_or(5) == 5

    def test_get_or_else(self):
        assert Nothing().get_or_else(lambda: 5) == 5

    def test_or_else(self):
        result = Nothing().or_else(lambda: Some(10))
        assert result == Some(10)

    def test_to_list(self):
        assert Nothing().to_list() == []

    def test_repr(self):
        assert repr(Nothing()) == "Nothing"

    def test_equality(self):
        assert Nothing() == Nothing()
        assert Nothing() != Some(5)


class TestSomeFunction:
    def test_creates_some(self):
        result = some(5)
        assert isinstance(result, Some)
        assert result.get() == 5


class TestNothingFunction:
    def test_creates_nothing(self):
        result = nothing()
        assert isinstance(result, Nothing)


class TestMaybeFunction:
    def test_some_from_value(self):
        result = maybe(5)
        assert result == Some(5)

    def test_nothing_from_none(self):
        result = maybe(None)
        assert result.is_none()


class TestFromOptional:
    def test_some_from_value(self):
        result = from_optional(5)
        assert result == Some(5)

    def test_nothing_from_none(self):
        result = from_optional(None)
        assert result.is_none()


class TestSafeDiv:
    def test_success(self):
        result = safe_div(10, 2)
        assert result == Some(5.0)

    def test_divide_by_zero(self):
        result = safe_div(10, 0)
        assert result.is_none()


class TestSafeInt:
    def test_success(self):
        result = safe_int("42")
        assert result == Some(42)

    def test_failure(self):
        result = safe_int("not a number")
        assert result.is_none()


class TestSafeFloat:
    def test_success(self):
        result = safe_float("3.14")
        assert result == Some(3.14)

    def test_failure(self):
        result = safe_float("not a float")
        assert result.is_none()


class TestSafeHead:
    def test_non_empty(self):
        result = safe_head([1, 2, 3])
        assert result == Some(1)

    def test_empty(self):
        result = safe_head([])
        assert result.is_none()


class TestSafeLast:
    def test_non_empty(self):
        result = safe_last([1, 2, 3])
        assert result == Some(3)

    def test_empty(self):
        result = safe_last([])
        assert result.is_none()


class TestSafeGet:
    def test_key_exists(self):
        result = safe_get({"a": 1}, "a")
        assert result == Some(1)

    def test_key_missing(self):
        result = safe_get({"a": 1}, "b")
        assert result.is_none()


class TestSafeIndex:
    def test_valid_index(self):
        result = safe_index([1, 2, 3], 1)
        assert result == Some(2)

    def test_negative_index(self):
        result = safe_index([1, 2, 3], -1)
        assert result.is_none()

    def test_out_of_bounds(self):
        result = safe_index([1, 2, 3], 10)
        assert result.is_none()


class TestLift:
    def test_lift_function(self):
        def double(x):
            return x * 2
        lifted = lift(double)
        assert lifted(Some(5)) == Some(10)
        assert lifted(Nothing()).is_none()


class TestLift2:
    def test_lift2_function(self):
        def add(a, b):
            return a + b
        lifted = lift2(add)
        assert lifted(Some(2), Some(3)) == Some(5)
        assert lifted(Some(2), Nothing()).is_none()
        assert lifted(Nothing(), Some(3)).is_none()


class TestSequence:
    def test_all_some(self):
        result = sequence([Some(1), Some(2), Some(3)])
        assert result == Some([1, 2, 3])

    def test_contains_nothing(self):
        result = sequence([Some(1), Nothing(), Some(3)])
        assert result.is_none()

    def test_empty(self):
        result = sequence([])
        assert result == Some([])


class TestTraverse:
    def test_all_success(self):
        result = traverse(safe_int, ["1", "2", "3"])
        assert result == Some([1, 2, 3])

    def test_contains_failure(self):
        result = traverse(safe_int, ["1", "not", "3"])
        assert result.is_none()


class TestCatMaybes:
    def test_filters_nothing(self):
        result = cat_maybes([Some(1), Nothing(), Some(3), Nothing()])
        assert result == [1, 3]

    def test_all_some(self):
        result = cat_maybes([Some(1), Some(2)])
        assert result == [1, 2]

    def test_all_nothing(self):
        result = cat_maybes([Nothing(), Nothing()])
        assert result == []


class TestSimulateMaybe:
    def test_some(self):
        result = simulate_maybe(["some:5"])
        assert result == ["Some(5)"]

    def test_nothing(self):
        result = simulate_maybe(["nothing:"])
        assert result == ["Nothing"]

    def test_safe_div_success(self):
        result = simulate_maybe(["safe_div:10,2"])
        assert result == ["Some(5.0)"]

    def test_safe_div_zero(self):
        result = simulate_maybe(["safe_div:10,0"])
        assert result == ["Nothing"]

    def test_safe_int_success(self):
        result = simulate_maybe(["safe_int:42"])
        assert result == ["Some(42)"]

    def test_map(self):
        result = simulate_maybe(["map:5,double"])
        assert result == ["Some(10)"]

    def test_filter_pass(self):
        result = simulate_maybe(["filter:6,even"])
        assert result == ["Some(6)"]

    def test_filter_fail(self):
        result = simulate_maybe(["filter:5,even"])
        assert result == ["Nothing"]

    def test_get_or(self):
        result = simulate_maybe(["get_or:nothing,10"])
        assert result == ["10"]

    def test_sequence_success(self):
        result = simulate_maybe(["sequence:1,2,3"])
        assert result == ["Some([1, 2, 3])"]


class TestChaining:
    def test_complex_chain(self):
        # Parse string, convert to int, double if even
        result = (
            safe_int("10")
            .filter(lambda x: x % 2 == 0)
            .map(lambda x: x * 2)
        )
        assert result == Some(20)

    def test_chain_short_circuits(self):
        result = (
            safe_int("not a number")
            .filter(lambda x: x % 2 == 0)
            .map(lambda x: x * 2)
        )
        assert result.is_none()
