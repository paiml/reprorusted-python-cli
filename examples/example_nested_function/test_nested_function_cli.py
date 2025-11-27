"""Tests for nested_function_cli.py"""

from nested_function_cli import (
    binary_search_nested,
    calculate_with_helpers,
    expression_parser,
    fibonacci_with_cache,
    merge_sort_nested,
    process_string,
    recursive_with_helper,
    tree_operations,
    validate_with_rules,
)


class TestCalculateWithHelpers:
    def test_basic(self):
        result = calculate_with_helpers([1, 2, 3, 4, 5])
        assert result["sum"] == 15
        assert result["avg"] == 3
        assert result["min"] == 1
        assert result["max"] == 5

    def test_single(self):
        result = calculate_with_helpers([42])
        assert result["sum"] == 42
        assert result["min"] == 42
        assert result["max"] == 42

    def test_empty(self):
        result = calculate_with_helpers([])
        assert result["sum"] == 0
        assert result["avg"] == 0


class TestProcessString:
    def test_basic(self):
        result = process_string("hello world")
        assert result["chars"] == 11
        assert result["words"] == 2
        assert result["first"] == "hello"
        assert result["last"] == "world"

    def test_empty(self):
        result = process_string("")
        assert result["chars"] == 0
        assert result["words"] == 0
        assert result["first"] == ""


class TestRecursiveWithHelper:
    def test_factorial_5(self):
        assert recursive_with_helper(5) == 120

    def test_factorial_0(self):
        assert recursive_with_helper(0) == 1

    def test_factorial_1(self):
        assert recursive_with_helper(1) == 1


class TestFibonacciWithCache:
    def test_fib_10(self):
        assert fibonacci_with_cache(10) == 55

    def test_fib_0(self):
        assert fibonacci_with_cache(0) == 0

    def test_fib_1(self):
        assert fibonacci_with_cache(1) == 1

    def test_fib_large(self):
        assert fibonacci_with_cache(20) == 6765


class TestBinarySearchNested:
    def test_found(self):
        items = [1, 3, 5, 7, 9]
        assert binary_search_nested(items, 5) == 2

    def test_not_found(self):
        items = [1, 3, 5, 7, 9]
        assert binary_search_nested(items, 4) == -1

    def test_first(self):
        items = [1, 3, 5, 7, 9]
        assert binary_search_nested(items, 1) == 0

    def test_last(self):
        items = [1, 3, 5, 7, 9]
        assert binary_search_nested(items, 9) == 4


class TestMergeSortNested:
    def test_unsorted(self):
        assert merge_sort_nested([3, 1, 4, 1, 5, 9, 2, 6]) == [1, 1, 2, 3, 4, 5, 6, 9]

    def test_sorted(self):
        assert merge_sort_nested([1, 2, 3]) == [1, 2, 3]

    def test_reverse(self):
        assert merge_sort_nested([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_empty(self):
        assert merge_sort_nested([]) == []

    def test_single(self):
        assert merge_sort_nested([42]) == [42]


class TestValidateWithRules:
    def test_valid(self):
        valid, errors = validate_with_rules("abc123")
        assert valid is True
        assert errors == []

    def test_too_short(self):
        valid, errors = validate_with_rules("ab")
        assert valid is False
        assert "too short" in errors

    def test_not_alphanumeric(self):
        valid, errors = validate_with_rules("abc!")
        assert valid is False
        assert "not alphanumeric" in errors

    def test_starts_with_number(self):
        valid, errors = validate_with_rules("123abc")
        assert valid is False
        assert "must start with letter" in errors


class TestTreeOperations:
    def test_single_node(self):
        tree = {"value": 10}
        result = tree_operations(tree)
        assert result["nodes"] == 1
        assert result["depth"] == 1
        assert result["sum"] == 10

    def test_with_children(self):
        tree = {
            "value": 1,
            "children": [
                {"value": 2},
                {"value": 3},
            ]
        }
        result = tree_operations(tree)
        assert result["nodes"] == 3
        assert result["depth"] == 2
        assert result["sum"] == 6

    def test_deep_tree(self):
        tree = {
            "value": 1,
            "children": [
                {
                    "value": 2,
                    "children": [
                        {"value": 3}
                    ]
                }
            ]
        }
        result = tree_operations(tree)
        assert result["depth"] == 3


class TestExpressionParser:
    def test_simple_add(self):
        assert expression_parser("2 + 3") == 5

    def test_simple_sub(self):
        assert expression_parser("10 - 3") == 7

    def test_chain(self):
        assert expression_parser("1 + 2 + 3") == 6

    def test_mixed(self):
        assert expression_parser("10 - 3 + 5") == 12

    def test_single_number(self):
        assert expression_parser("42") == 42


class TestEdgeCases:
    def test_factorial_large(self):
        assert recursive_with_helper(10) == 3628800

    def test_empty_sort(self):
        assert merge_sort_nested([]) == []

    def test_single_element_search(self):
        assert binary_search_nested([5], 5) == 0
        assert binary_search_nested([5], 3) == -1
