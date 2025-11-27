#!/usr/bin/env python3
"""BatchNorm1d CLI tool - batch normalization (PyTorch-compatible)."""

import argparse
import json
import math
import sys


def batchnorm(
    x: list[list[float]], gamma: list[float], beta: list[float], eps: float = 1e-5
) -> list[list[float]]:
    """Batch normalization forward pass."""
    n_samples = len(x)
    n_features = len(x[0])

    # Compute mean and variance per feature
    mean = [sum(x[i][j] for i in range(n_samples)) / n_samples for j in range(n_features)]
    var = [
        sum((x[i][j] - mean[j]) ** 2 for i in range(n_samples)) / n_samples
        for j in range(n_features)
    ]

    # Normalize and scale
    output = []
    for i in range(n_samples):
        row = []
        for j in range(n_features):
            x_norm = (x[i][j] - mean[j]) / math.sqrt(var[j] + eps)
            row.append(gamma[j] * x_norm + beta[j])
        output.append(row)

    return output


def cmd_forward(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        output = batchnorm(data["x"], data["gamma"], data["beta"])
        print(json.dumps({"output": output}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="BatchNorm1d CLI (PyTorch-compatible)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("forward", help="Forward pass").set_defaults(func=cmd_forward)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
