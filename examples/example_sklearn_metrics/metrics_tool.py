#!/usr/bin/env python3
"""Metrics CLI tool.

A CLI for sklearn-style classification and regression metrics.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: Pedregosa et al. (2011) sklearn metrics [1]

Usage:
    echo '{"y_true": [0, 1, 1], "y_pred": [0, 1, 0]}' | python metrics_tool.py accuracy
"""

import argparse
import json
import sys


def accuracy_score(y_true: list[int], y_pred: list[int]) -> float:
    """Calculate accuracy score."""
    if len(y_true) != len(y_pred):
        raise ValueError("Length mismatch")
    if len(y_true) == 0:
        raise ValueError("Empty input")
    correct = sum(1 for i in range(len(y_true)) if y_true[i] == y_pred[i])
    return correct / len(y_true)


def precision_score(y_true: list[int], y_pred: list[int]) -> float:
    """Calculate precision score (TP / (TP + FP))."""
    if len(y_true) != len(y_pred):
        raise ValueError("Length mismatch")
    tp = sum(1 for i in range(len(y_true)) if y_true[i] == 1 and y_pred[i] == 1)
    fp = sum(1 for i in range(len(y_true)) if y_true[i] == 0 and y_pred[i] == 1)
    if tp + fp == 0:
        return 0.0
    return tp / (tp + fp)


def recall_score(y_true: list[int], y_pred: list[int]) -> float:
    """Calculate recall score (TP / (TP + FN))."""
    if len(y_true) != len(y_pred):
        raise ValueError("Length mismatch")
    tp = sum(1 for i in range(len(y_true)) if y_true[i] == 1 and y_pred[i] == 1)
    fn = sum(1 for i in range(len(y_true)) if y_true[i] == 1 and y_pred[i] == 0)
    if tp + fn == 0:
        return 0.0
    return tp / (tp + fn)


def f1_score(y_true: list[int], y_pred: list[int]) -> float:
    """Calculate F1 score (harmonic mean of precision and recall)."""
    p = precision_score(y_true, y_pred)
    r = recall_score(y_true, y_pred)
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)


def confusion_matrix(y_true: list[int], y_pred: list[int]) -> list[list[int]]:
    """Calculate confusion matrix [[TN, FP], [FN, TP]]."""
    if len(y_true) != len(y_pred):
        raise ValueError("Length mismatch")
    tn = sum(1 for i in range(len(y_true)) if y_true[i] == 0 and y_pred[i] == 0)
    fp = sum(1 for i in range(len(y_true)) if y_true[i] == 0 and y_pred[i] == 1)
    fn = sum(1 for i in range(len(y_true)) if y_true[i] == 1 and y_pred[i] == 0)
    tp = sum(1 for i in range(len(y_true)) if y_true[i] == 1 and y_pred[i] == 1)
    return [[tn, fp], [fn, tp]]


def mean_squared_error(y_true: list[float], y_pred: list[float]) -> float:
    """Calculate mean squared error."""
    if len(y_true) != len(y_pred):
        raise ValueError("Length mismatch")
    if len(y_true) == 0:
        raise ValueError("Empty input")
    return sum((y_true[i] - y_pred[i]) ** 2 for i in range(len(y_true))) / len(y_true)


def r2_score(y_true: list[float], y_pred: list[float]) -> float:
    """Calculate R-squared score."""
    if len(y_true) != len(y_pred):
        raise ValueError("Length mismatch")
    if len(y_true) == 0:
        raise ValueError("Empty input")

    y_mean = sum(y_true) / len(y_true)
    ss_res = sum((y_true[i] - y_pred[i]) ** 2 for i in range(len(y_true)))
    ss_tot = sum((y_true[i] - y_mean) ** 2 for i in range(len(y_true)))

    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0
    return 1.0 - ss_res / ss_tot


def cmd_accuracy(args: argparse.Namespace) -> None:
    """Handle accuracy subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        acc = accuracy_score(data["y_true"], data["y_pred"])
        print(json.dumps({"accuracy": acc}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_precision(args: argparse.Namespace) -> None:
    """Handle precision subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        prec = precision_score(data["y_true"], data["y_pred"])
        print(json.dumps({"precision": prec}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_recall(args: argparse.Namespace) -> None:
    """Handle recall subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        rec = recall_score(data["y_true"], data["y_pred"])
        print(json.dumps({"recall": rec}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_f1(args: argparse.Namespace) -> None:
    """Handle f1 subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        f1 = f1_score(data["y_true"], data["y_pred"])
        print(json.dumps({"f1": f1}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_confusion_matrix(args: argparse.Namespace) -> None:
    """Handle confusion-matrix subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        matrix = confusion_matrix(data["y_true"], data["y_pred"])
        print(json.dumps({"matrix": matrix}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_mse(args: argparse.Namespace) -> None:
    """Handle mse subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        mse = mean_squared_error(data["y_true"], data["y_pred"])
        print(json.dumps({"mse": mse}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_r2(args: argparse.Namespace) -> None:
    """Handle r2 subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        r2 = r2_score(data["y_true"], data["y_pred"])
        print(json.dumps({"r2": r2}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Metrics CLI - classification and regression metrics (sklearn-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("accuracy", help="Accuracy score").set_defaults(func=cmd_accuracy)
    subparsers.add_parser("precision", help="Precision score").set_defaults(func=cmd_precision)
    subparsers.add_parser("recall", help="Recall score").set_defaults(func=cmd_recall)
    subparsers.add_parser("f1", help="F1 score").set_defaults(func=cmd_f1)
    subparsers.add_parser("confusion-matrix", help="Confusion matrix").set_defaults(
        func=cmd_confusion_matrix
    )
    subparsers.add_parser("mse", help="Mean squared error").set_defaults(func=cmd_mse)
    subparsers.add_parser("r2", help="R-squared score").set_defaults(func=cmd_r2)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
