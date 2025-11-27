#!/usr/bin/env python3
"""Tensor operations CLI tool.

A CLI for PyTorch-style tensor operations.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: Paszke et al. (2019) PyTorch [2]

Usage:
    echo '{"data": [1, 2, 3]}' | python tensor_tool.py create
    echo '{"a": [1, 2], "b": [3, 4]}' | python tensor_tool.py add
"""

import argparse
import json
import sys

Tensor = list[float] | list[list[float]]


def get_shape(tensor: Tensor) -> list[int]:
    """Get shape of tensor."""
    if not tensor:
        return [0]
    if isinstance(tensor[0], list):
        return [len(tensor), len(tensor[0])]
    return [len(tensor)]


def flatten(tensor: Tensor) -> list[float]:
    """Flatten tensor to 1D."""
    if not tensor:
        return []
    if isinstance(tensor[0], list):
        return [x for row in tensor for x in row]
    return tensor


def zeros(shape: list[int]) -> Tensor:
    """Create zeros tensor."""
    if len(shape) == 1:
        return [0.0] * shape[0]
    return [[0.0] * shape[1] for _ in range(shape[0])]


def ones(shape: list[int]) -> Tensor:
    """Create ones tensor."""
    if len(shape) == 1:
        return [1.0] * shape[0]
    return [[1.0] * shape[1] for _ in range(shape[0])]


def add(a: Tensor, b: Tensor) -> Tensor:
    """Element-wise addition."""
    if isinstance(a[0], list):
        if len(a) != len(b) or len(a[0]) != len(b[0]):
            raise ValueError("Shape mismatch")
        return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]
    if len(a) != len(b):
        raise ValueError("Shape mismatch")
    return [a[i] + b[i] for i in range(len(a))]


def mul(a: Tensor, b: Tensor) -> Tensor:
    """Element-wise multiplication."""
    if isinstance(a[0], list):
        if len(a) != len(b) or len(a[0]) != len(b[0]):
            raise ValueError("Shape mismatch")
        return [[a[i][j] * b[i][j] for j in range(len(a[0]))] for i in range(len(a))]
    if len(a) != len(b):
        raise ValueError("Shape mismatch")
    return [a[i] * b[i] for i in range(len(a))]


def matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """Matrix multiplication."""
    if len(a[0]) != len(b):
        raise ValueError(f"Shape mismatch: {len(a[0])} != {len(b)}")
    m, k = len(a), len(a[0])
    n = len(b[0])
    result = [[0.0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            for p in range(k):
                result[i][j] += a[i][p] * b[p][j]
    return result


def tensor_sum(tensor: Tensor) -> float:
    """Sum all elements."""
    flat = flatten(tensor)
    return sum(flat)


def tensor_mean(tensor: Tensor) -> float:
    """Mean of all elements."""
    flat = flatten(tensor)
    return sum(flat) / len(flat) if flat else 0.0


def cmd_create(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "data" not in data:
        print("Error: Missing 'data'", file=sys.stderr)
        sys.exit(1)

    tensor = data["data"]
    shape = get_shape(tensor)
    print(json.dumps({"tensor": tensor, "shape": shape}))


def cmd_zeros(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    shape = data.get("shape", [1])
    tensor = zeros(shape)
    print(json.dumps({"tensor": tensor, "shape": shape}))


def cmd_ones(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    shape = data.get("shape", [1])
    tensor = ones(shape)
    print(json.dumps({"tensor": tensor, "shape": shape}))


def cmd_add(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = add(data["a"], data["b"])
        print(json.dumps({"tensor": result}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_mul(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = mul(data["a"], data["b"])
        print(json.dumps({"tensor": result}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_matmul(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = matmul(data["a"], data["b"])
        print(json.dumps({"tensor": result}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_sum(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    result = tensor_sum(data["tensor"])
    print(json.dumps({"value": result}))


def cmd_mean(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    result = tensor_mean(data["tensor"])
    print(json.dumps({"value": result}))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tensor CLI - PyTorch-style tensor operations (aprender-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("create", help="Create tensor from data").set_defaults(func=cmd_create)
    subparsers.add_parser("zeros", help="Create zeros tensor").set_defaults(func=cmd_zeros)
    subparsers.add_parser("ones", help="Create ones tensor").set_defaults(func=cmd_ones)
    subparsers.add_parser("add", help="Element-wise addition").set_defaults(func=cmd_add)
    subparsers.add_parser("mul", help="Element-wise multiplication").set_defaults(func=cmd_mul)
    subparsers.add_parser("matmul", help="Matrix multiplication").set_defaults(func=cmd_matmul)
    subparsers.add_parser("sum", help="Sum reduction").set_defaults(func=cmd_sum)
    subparsers.add_parser("mean", help="Mean reduction").set_defaults(func=cmd_mean)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
