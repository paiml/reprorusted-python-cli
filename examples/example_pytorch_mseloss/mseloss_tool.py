#!/usr/bin/env python3
"""Loss functions CLI tool.

A CLI for PyTorch-style loss functions.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: Paszke et al. (2019) PyTorch [2]

Usage:
    echo '{"pred": [1, 2], "target": [2, 3]}' | python mseloss_tool.py forward
"""

import argparse
import json
import math
import sys


def mse_loss(pred: list[float], target: list[float], reduction: str = "mean") -> float:
    """Mean squared error loss."""
    if len(pred) != len(target):
        raise ValueError("Shape mismatch")

    squared_errors = [(pred[i] - target[i]) ** 2 for i in range(len(pred))]

    if reduction == "sum":
        return sum(squared_errors)
    elif reduction == "mean":
        return sum(squared_errors) / len(squared_errors)
    else:
        raise ValueError(f"Unknown reduction: {reduction}")


def mse_backward(pred: list[float], target: list[float]) -> list[float]:
    """Gradient of MSE loss with respect to pred."""
    n = len(pred)
    return [2 * (pred[i] - target[i]) / n for i in range(n)]


def l1_loss(pred: list[float], target: list[float], reduction: str = "mean") -> float:
    """L1 loss (mean absolute error)."""
    if len(pred) != len(target):
        raise ValueError("Shape mismatch")

    abs_errors = [abs(pred[i] - target[i]) for i in range(len(pred))]

    if reduction == "sum":
        return sum(abs_errors)
    elif reduction == "mean":
        return sum(abs_errors) / len(abs_errors)
    else:
        raise ValueError(f"Unknown reduction: {reduction}")


def cross_entropy_loss(logits: list[float], target: int) -> float:
    """Cross-entropy loss with softmax."""
    # Softmax
    max_logit = max(logits)
    exp_logits = [math.exp(logit - max_logit) for logit in logits]
    sum_exp = sum(exp_logits)
    softmax = [e / sum_exp for e in exp_logits]

    # Negative log likelihood
    return -math.log(softmax[target] + 1e-10)


def cmd_forward(args: argparse.Namespace) -> None:
    """Handle forward subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "pred" not in data or "target" not in data:
        print("Error: Missing 'pred' or 'target'", file=sys.stderr)
        sys.exit(1)

    reduction = data.get("reduction", "mean")

    try:
        loss = mse_loss(data["pred"], data["target"], reduction)
        print(json.dumps({"loss": loss}))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_backward(args: argparse.Namespace) -> None:
    """Handle backward subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "pred" not in data or "target" not in data:
        print("Error: Missing 'pred' or 'target'", file=sys.stderr)
        sys.exit(1)

    grad = mse_backward(data["pred"], data["target"])
    print(json.dumps({"grad": grad}))


def cmd_l1_forward(args: argparse.Namespace) -> None:
    """Handle l1-forward subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "pred" not in data or "target" not in data:
        print("Error: Missing 'pred' or 'target'", file=sys.stderr)
        sys.exit(1)

    reduction = data.get("reduction", "mean")

    try:
        loss = l1_loss(data["pred"], data["target"], reduction)
        print(json.dumps({"loss": loss}))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_cross_entropy(args: argparse.Namespace) -> None:
    """Handle cross-entropy subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "logits" not in data or "target" not in data:
        print("Error: Missing 'logits' or 'target'", file=sys.stderr)
        sys.exit(1)

    loss = cross_entropy_loss(data["logits"], data["target"])
    print(json.dumps({"loss": loss}))


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Loss CLI - MSE, L1, CrossEntropy (PyTorch-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("forward", help="MSE loss forward").set_defaults(func=cmd_forward)
    subparsers.add_parser("backward", help="MSE loss backward").set_defaults(func=cmd_backward)
    subparsers.add_parser("l1-forward", help="L1 loss forward").set_defaults(func=cmd_l1_forward)
    subparsers.add_parser("cross-entropy", help="Cross-entropy loss").set_defaults(
        func=cmd_cross_entropy
    )

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
