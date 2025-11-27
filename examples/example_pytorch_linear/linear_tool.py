#!/usr/bin/env python3
"""Linear layer CLI tool.

A CLI for PyTorch-style nn.Linear layer.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: He et al. (2015) Weight initialization [5]

Usage:
    echo '{"x": [1,2], "weight": [[1,0],[0,1]], "bias": [0,0]}' | python linear_tool.py forward
"""

import argparse
import json
import math
import random
import sys


def forward(
    x: list[float] | list[list[float]], weight: list[list[float]], bias: list[float]
) -> list[float] | list[list[float]]:
    """Forward pass: y = Wx + b."""
    # Handle batch input
    if x and isinstance(x[0], list):
        return [forward_single(xi, weight, bias) for xi in x]
    return forward_single(x, weight, bias)


def forward_single(x: list[float], weight: list[list[float]], bias: list[float]) -> list[float]:
    """Forward pass for single sample."""
    out_features = len(weight)
    in_features = len(weight[0])

    if len(x) != in_features:
        raise ValueError(f"Shape mismatch: x has {len(x)}, weight expects {in_features}")

    output = []
    for i in range(out_features):
        val = bias[i]
        for j in range(in_features):
            val += weight[i][j] * x[j]
        output.append(val)
    return output


def init_weights(in_features: int, out_features: int, random_state: int = None) -> dict:
    """Initialize weights using Kaiming uniform."""
    if random_state is not None:
        random.seed(random_state)

    # Kaiming initialization: std = sqrt(2/in_features)
    std = math.sqrt(2.0 / in_features)
    bound = math.sqrt(3.0) * std

    weight = [
        [random.uniform(-bound, bound) for _ in range(in_features)] for _ in range(out_features)
    ]
    # Bias uniform in [-1/sqrt(in), 1/sqrt(in)]
    bias_bound = 1.0 / math.sqrt(in_features)
    bias = [random.uniform(-bias_bound, bias_bound) for _ in range(out_features)]

    return {"weight": weight, "bias": bias}


def cmd_forward(args: argparse.Namespace) -> None:
    """Handle forward subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    required = ["x", "weight", "bias"]
    for field in required:
        if field not in data:
            print(f"Error: Missing '{field}'", file=sys.stderr)
            sys.exit(1)

    try:
        output = forward(data["x"], data["weight"], data["bias"])
        print(json.dumps({"output": output}))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_init(args: argparse.Namespace) -> None:
    """Handle init subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    in_features = data.get("in_features", 1)
    out_features = data.get("out_features", 1)
    random_state = data.get("random_state", None)

    result = init_weights(in_features, out_features, random_state)
    print(json.dumps(result))


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Linear CLI - nn.Linear layer (PyTorch-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("forward", help="Forward pass").set_defaults(func=cmd_forward)
    subparsers.add_parser("init", help="Initialize weights").set_defaults(func=cmd_init)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
