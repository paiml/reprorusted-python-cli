#!/usr/bin/env python3
"""Nested Comprehension CLI.

Nested list comprehension patterns.
"""

import argparse
import sys


def flatten_2d(matrix: list[list[int]]) -> list[int]:
    """Flatten 2D list to 1D."""
    return [x for row in matrix for x in row]


def flatten_3d(cube: list[list[list[int]]]) -> list[int]:
    """Flatten 3D list to 1D."""
    return [x for plane in cube for row in plane for x in row]


def flatten_with_filter(matrix: list[list[int]], threshold: int) -> list[int]:
    """Flatten and filter values above threshold."""
    return [x for row in matrix for x in row if x > threshold]


def matrix_to_pairs(matrix: list[list[int]]) -> list[tuple[int, int, int]]:
    """Convert matrix to list of (row_idx, col_idx, value) tuples."""
    return [(i, j, matrix[i][j]) for i in range(len(matrix)) for j in range(len(matrix[i]))]


def multiply_matrices_element(m1: list[list[int]], m2: list[list[int]]) -> list[list[int]]:
    """Element-wise matrix multiplication."""
    return [[m1[i][j] * m2[i][j] for j in range(len(m1[i]))] for i in range(len(m1))]


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    """Transpose matrix using nested comprehension."""
    if not matrix:
        return []
    return [[row[i] for row in matrix] for i in range(len(matrix[0]))]


def nested_squares(n: int) -> list[list[int]]:
    """Generate n x n matrix of squares."""
    return [[i * j for j in range(n)] for i in range(n)]


def nested_with_condition(n: int) -> list[list[int]]:
    """Generate matrix with conditional values."""
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def filter_rows_by_sum(matrix: list[list[int]], min_sum: int) -> list[list[int]]:
    """Keep only rows with sum >= min_sum."""
    return [row for row in matrix if sum(row) >= min_sum]


def filter_and_transform(matrix: list[list[int]]) -> list[list[int]]:
    """Filter rows and double values."""
    return [[x * 2 for x in row] for row in matrix if sum(row) > 0]


def cross_product(list1: list[int], list2: list[int]) -> list[tuple[int, int]]:
    """Cartesian product of two lists."""
    return [(x, y) for x in list1 for y in list2]


def cross_product_filtered(list1: list[int], list2: list[int]) -> list[tuple[int, int]]:
    """Cartesian product with filter."""
    return [(x, y) for x in list1 for y in list2 if x != y]


def cross_product_sum(list1: list[int], list2: list[int], target: int) -> list[tuple[int, int]]:
    """Pairs that sum to target."""
    return [(x, y) for x in list1 for y in list2 if x + y == target]


def nested_strings(words: list[str]) -> list[str]:
    """Extract all characters from all words."""
    return [char for word in words for char in word]


def nested_strings_filtered(words: list[str]) -> list[str]:
    """Extract vowels from all words."""
    vowels = "aeiouAEIOU"
    return [char for word in words for char in word if char in vowels]


def group_by_length(words: list[str]) -> dict[int, list[str]]:
    """Group words by length using comprehension."""
    lengths = {len(w) for w in words}
    return {length: [w for w in words if len(w) == length] for length in lengths}


def nested_enumerate(matrix: list[list[int]]) -> list[tuple[int, int, int]]:
    """Enumerate 2D matrix."""
    return [(i, j, val) for i, row in enumerate(matrix) for j, val in enumerate(row)]


def diagonal_elements(matrix: list[list[int]]) -> list[int]:
    """Get diagonal elements."""
    return [matrix[i][i] for i in range(min(len(matrix), len(matrix[0]) if matrix else 0))]


def anti_diagonal_elements(matrix: list[list[int]]) -> list[int]:
    """Get anti-diagonal elements."""
    n = len(matrix)
    return [matrix[i][n - 1 - i] for i in range(n) if n - 1 - i < len(matrix[i])]


def upper_triangular(matrix: list[list[int]]) -> list[int]:
    """Get upper triangular elements."""
    return [matrix[i][j] for i in range(len(matrix)) for j in range(len(matrix[i])) if j >= i]


def lower_triangular(matrix: list[list[int]]) -> list[int]:
    """Get lower triangular elements."""
    return [matrix[i][j] for i in range(len(matrix)) for j in range(len(matrix[i])) if j <= i]


def sliding_window_2d(matrix: list[list[int]], size: int) -> list[list[list[int]]]:
    """Extract sliding windows from matrix."""
    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    return [
        [[matrix[i + di][j + dj] for dj in range(size)] for di in range(size)]
        for i in range(rows - size + 1)
        for j in range(cols - size + 1)
    ]


def flatten_dict_values(d: dict[str, list[int]]) -> list[int]:
    """Flatten dictionary values."""
    return [x for values in d.values() for x in values]


def flatten_nested_dict(d: dict[str, dict[str, int]]) -> list[tuple[str, str, int]]:
    """Flatten nested dict to tuples."""
    return [(k1, k2, v) for k1, inner in d.items() for k2, v in inner.items()]


def combinations_with_replacement(items: list[int], r: int) -> list[tuple[int, ...]]:
    """Simple combinations with replacement for r=2."""
    if r != 2:
        return []
    return [(x, y) for i, x in enumerate(items) for y in items[i:]]


def permutations_2(items: list[int]) -> list[tuple[int, int]]:
    """All 2-permutations."""
    return [(x, y) for i, x in enumerate(items) for j, y in enumerate(items) if i != j]


def main() -> int:
    parser = argparse.ArgumentParser(description="Nested comprehension CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # flatten
    flat_p = subparsers.add_parser("flatten", help="Flatten matrix")
    flat_p.add_argument("--matrix", required=True, help="Matrix as [[1,2],[3,4]]")

    # transpose
    trans_p = subparsers.add_parser("transpose", help="Transpose matrix")
    trans_p.add_argument("--matrix", required=True)

    # cross
    cross_p = subparsers.add_parser("cross", help="Cross product")
    cross_p.add_argument("--list1", required=True)
    cross_p.add_argument("--list2", required=True)

    # squares
    sq_p = subparsers.add_parser("squares", help="Generate square matrix")
    sq_p.add_argument("n", type=int)

    args = parser.parse_args()

    if args.command == "flatten":
        import ast

        matrix = ast.literal_eval(args.matrix)
        result = flatten_2d(matrix)
        print(result)

    elif args.command == "transpose":
        import ast

        matrix = ast.literal_eval(args.matrix)
        result = transpose(matrix)
        print(result)

    elif args.command == "cross":
        import ast

        list1 = ast.literal_eval(args.list1)
        list2 = ast.literal_eval(args.list2)
        result = cross_product(list1, list2)
        print(result)

    elif args.command == "squares":
        result = nested_squares(args.n)
        for row in result:
            print(row)

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
