#!/usr/bin/env python3
"""Dropout CLI tool - dropout regularization (PyTorch-compatible)."""

import argparse
import json
import random
import sys


def dropout(x: list[float], p: float, training: bool, random_state: int = None) -> list[float]:
    """Dropout forward pass."""
    if not training:
        return x

    if random_state is not None:
        random.seed(random_state)

    # Scale by 1/(1-p) to maintain expected value
    scale = 1.0 / (1.0 - p) if p < 1 else 0

    output = []
    for xi in x:
        if random.random() < p:
            output.append(0.0)
        else:
            output.append(xi * scale)
    return output


def cmd_forward(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        output = dropout(
            data["x"],
            data.get("p", 0.5),
            data.get("training", True),
            data.get("random_state", None),
        )
        print(json.dumps({"output": output}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dropout CLI (PyTorch-compatible)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("forward", help="Forward pass").set_defaults(func=cmd_forward)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
