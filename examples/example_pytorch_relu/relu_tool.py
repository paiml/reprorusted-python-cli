#!/usr/bin/env python3
"""Activation functions CLI tool.

A CLI for PyTorch-style activation functions.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: He et al. (2015) Deep Rectifiers [5]

Usage:
    echo '{"x": [-1, 0, 1]}' | python relu_tool.py relu
"""

import argparse
import json
import math
import sys


def relu(x: list[float]) -> list[float]:
    """ReLU activation: max(0, x)."""
    return [max(0.0, xi) for xi in x]


def sigmoid(x: list[float]) -> list[float]:
    """Sigmoid activation: 1 / (1 + exp(-x))."""
    result = []
    for xi in x:
        if xi >= 0:
            result.append(1.0 / (1.0 + math.exp(-xi)))
        else:
            exp_x = math.exp(xi)
            result.append(exp_x / (1.0 + exp_x))
    return result


def tanh(x: list[float]) -> list[float]:
    """Tanh activation."""
    return [math.tanh(xi) for xi in x]


def softmax(x: list[float]) -> list[float]:
    """Softmax activation."""
    # Subtract max for numerical stability
    max_x = max(x)
    exp_x = [math.exp(xi - max_x) for xi in x]
    sum_exp = sum(exp_x)
    return [e / sum_exp for e in exp_x]


def cmd_relu(args: argparse.Namespace) -> None:
    """Handle relu subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "x" not in data:
        print("Error: Missing 'x'", file=sys.stderr)
        sys.exit(1)

    output = relu(data["x"])
    print(json.dumps({"output": output}))


def cmd_sigmoid(args: argparse.Namespace) -> None:
    """Handle sigmoid subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "x" not in data:
        print("Error: Missing 'x'", file=sys.stderr)
        sys.exit(1)

    output = sigmoid(data["x"])
    print(json.dumps({"output": output}))


def cmd_tanh(args: argparse.Namespace) -> None:
    """Handle tanh subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "x" not in data:
        print("Error: Missing 'x'", file=sys.stderr)
        sys.exit(1)

    output = tanh(data["x"])
    print(json.dumps({"output": output}))


def cmd_softmax(args: argparse.Namespace) -> None:
    """Handle softmax subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "x" not in data:
        print("Error: Missing 'x'", file=sys.stderr)
        sys.exit(1)

    output = softmax(data["x"])
    print(json.dumps({"output": output}))


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Activation CLI - ReLU, Sigmoid, Tanh, Softmax (PyTorch-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("relu", help="ReLU activation").set_defaults(func=cmd_relu)
    subparsers.add_parser("sigmoid", help="Sigmoid activation").set_defaults(func=cmd_sigmoid)
    subparsers.add_parser("tanh", help="Tanh activation").set_defaults(func=cmd_tanh)
    subparsers.add_parser("softmax", help="Softmax activation").set_defaults(func=cmd_softmax)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
