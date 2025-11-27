#!/usr/bin/env python3
"""Autograd CLI tool.

A CLI for PyTorch-style automatic differentiation.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: Baydin et al. (2018) Automatic Differentiation [3]

Usage:
    echo '{"expression": "x**2", "x": 3.0}' | python autograd_tool.py backward
"""

import argparse
import json
import sys


def numerical_gradient(f, x: float, h: float = 1e-5) -> float:
    """Compute gradient numerically using central difference."""
    return (f(x + h) - f(x - h)) / (2 * h)


def backward_power(x: float, n: int) -> float:
    """Gradient of x^n is n * x^(n-1)."""
    return n * (x ** (n - 1))


def backward_sum(x: list[float]) -> list[float]:
    """Gradient of sum is all ones."""
    return [1.0] * len(x)


def backward_linear(a: float, b: float, x: float) -> float:
    """Gradient of ax + b is a."""
    return a


def backward_product(x: float, w: float) -> tuple:
    """Gradient of x*w: d/dx = w, d/dw = x."""
    return w, x


def parse_and_differentiate(expression: str, variables: dict) -> dict:
    """Parse expression and compute gradients."""
    expression = expression.strip()

    # Handle x**n pattern
    if "**" in expression:
        parts = expression.split("**")
        if parts[0].strip() == "x":
            n = int(parts[1].strip())
            x = variables["x"]
            grad = backward_power(x, n)
            return {"grad": grad, "value": x**n}

    # Handle sum pattern
    if expression == "sum":
        x = variables["x"]
        grad = backward_sum(x)
        value = sum(x)
        return {"grad": grad, "value": value}

    # Handle x * w pattern (product of two variables)
    if "x * w" in expression or "x*w" in expression:
        x = variables["x"]
        w = variables["w"]
        grad_x, grad_w = backward_product(x, w)
        return {"grad_x": grad_x, "grad_w": grad_w, "value": x * w}

    # Handle a*x + b pattern
    if "*x" in expression:
        # Parse "a*x + b"
        if "+ " in expression:
            parts = expression.split("+")
            ax_part = parts[0].strip()
            b = float(parts[1].strip())
            a = float(ax_part.split("*")[0].strip())
            x = variables["x"]
            grad = backward_linear(a, b, x)
            return {"grad": grad, "value": a * x + b}

    raise ValueError(f"Unsupported expression: {expression}")


def cmd_backward(args: argparse.Namespace) -> None:
    """Handle backward subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "expression" not in data:
        print("Error: Missing 'expression'", file=sys.stderr)
        sys.exit(1)

    try:
        result = parse_and_differentiate(data["expression"], data)
        print(json.dumps(result))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Autograd CLI - automatic differentiation (PyTorch-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("backward", help="Compute gradients via backward pass").set_defaults(
        func=cmd_backward
    )

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
