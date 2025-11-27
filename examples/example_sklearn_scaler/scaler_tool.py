#!/usr/bin/env python3
"""StandardScaler CLI tool.

A CLI for sklearn-style StandardScaler normalization.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: Pedregosa et al. (2011) sklearn preprocessing [1]

Usage:
    echo '{"X": [[1, 10], [2, 20], [3, 30]]}' | python scaler_tool.py fit-transform
"""

import argparse
import json
import math
import sys


def compute_mean_std(X: list[list[float]]) -> tuple[list[float], list[float]]:
    """Compute mean and standard deviation for each feature."""
    n_samples = len(X)
    n_features = len(X[0])

    # Compute mean
    mean = [0.0] * n_features
    for row in X:
        for j in range(n_features):
            mean[j] += row[j]
    mean = [m / n_samples for m in mean]

    # Compute std
    std = [0.0] * n_features
    for row in X:
        for j in range(n_features):
            std[j] += (row[j] - mean[j]) ** 2
    std = [math.sqrt(s / n_samples) if n_samples > 0 else 0.0 for s in std]

    return mean, std


def fit(X: list[list[float]]) -> dict:
    """Fit scaler to compute mean and std."""
    if len(X) == 0:
        raise ValueError("Empty input data")

    mean, std = compute_mean_std(X)
    return {"mean": mean, "std": std}


def transform(X: list[list[float]], mean: list[float], std: list[float]) -> list[list[float]]:
    """Transform data using fitted parameters."""
    X_scaled = []
    for row in X:
        scaled_row = []
        for j in range(len(row)):
            if std[j] > 1e-10:
                scaled_row.append((row[j] - mean[j]) / std[j])
            else:
                scaled_row.append(0.0)  # Constant feature
        X_scaled.append(scaled_row)
    return X_scaled


def inverse_transform(
    X_scaled: list[list[float]], mean: list[float], std: list[float]
) -> list[list[float]]:
    """Inverse transform to recover original data."""
    X = []
    for row in X_scaled:
        original_row = []
        for j in range(len(row)):
            original_row.append(row[j] * std[j] + mean[j])
        X.append(original_row)
    return X


def cmd_fit(args: argparse.Namespace) -> None:
    """Handle fit subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "X" not in data:
        print("Error: Missing 'X'", file=sys.stderr)
        sys.exit(1)

    try:
        result = fit(data["X"])
        print(json.dumps(result))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_transform(args: argparse.Namespace) -> None:
    """Handle transform subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    required = ["X", "mean", "std"]
    for field in required:
        if field not in data:
            print(f"Error: Missing '{field}'", file=sys.stderr)
            sys.exit(1)

    X_scaled = transform(data["X"], data["mean"], data["std"])
    print(json.dumps({"X_scaled": X_scaled}))


def cmd_fit_transform(args: argparse.Namespace) -> None:
    """Handle fit-transform subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "X" not in data:
        print("Error: Missing 'X'", file=sys.stderr)
        sys.exit(1)

    try:
        fit_result = fit(data["X"])
        X_scaled = transform(data["X"], fit_result["mean"], fit_result["std"])
        result = {
            "X_scaled": X_scaled,
            "mean": fit_result["mean"],
            "std": fit_result["std"],
        }
        print(json.dumps(result))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_inverse_transform(args: argparse.Namespace) -> None:
    """Handle inverse-transform subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    required = ["X_scaled", "mean", "std"]
    for field in required:
        if field not in data:
            print(f"Error: Missing '{field}'", file=sys.stderr)
            sys.exit(1)

    X = inverse_transform(data["X_scaled"], data["mean"], data["std"])
    print(json.dumps({"X": X}))


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="StandardScaler CLI - zero mean, unit variance (sklearn-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    fit_parser = subparsers.add_parser("fit", help="Fit scaler")
    fit_parser.set_defaults(func=cmd_fit)

    transform_parser = subparsers.add_parser("transform", help="Transform data")
    transform_parser.set_defaults(func=cmd_transform)

    fit_transform_parser = subparsers.add_parser("fit-transform", help="Fit and transform")
    fit_transform_parser.set_defaults(func=cmd_fit_transform)

    inverse_parser = subparsers.add_parser("inverse-transform", help="Inverse transform")
    inverse_parser.set_defaults(func=cmd_inverse_transform)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
