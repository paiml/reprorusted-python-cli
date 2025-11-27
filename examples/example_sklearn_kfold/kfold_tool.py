#!/usr/bin/env python3
"""KFold CLI tool.

A CLI for sklearn-style K-fold cross-validation.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: Pedregosa et al. (2011) sklearn model selection [1]

Usage:
    echo '{"n_samples": 10, "n_splits": 5}' | python kfold_tool.py split
"""

import argparse
import json
import math
import sys


def kfold_split(n_samples: int, n_splits: int = 5) -> list[dict[str, list[int]]]:
    """Generate K-fold train/test splits."""
    if n_splits > n_samples:
        raise ValueError(f"n_splits ({n_splits}) > n_samples ({n_samples})")

    fold_sizes = [n_samples // n_splits] * n_splits
    for i in range(n_samples % n_splits):
        fold_sizes[i] += 1

    indices = list(range(n_samples))
    folds = []
    current = 0

    for fold_size in fold_sizes:
        test_idx = indices[current : current + fold_size]
        train_idx = indices[:current] + indices[current + fold_size :]
        folds.append({"train": train_idx, "test": test_idx})
        current += fold_size

    return folds


def linear_regression_fit(X: list[list[float]], y: list[float]) -> tuple:
    """Simple linear regression fit."""
    n = len(X)
    if n == 0:
        return [0.0], 0.0

    n_features = len(X[0])

    # Add bias column

    # Normal equation: (X^T X)^-1 X^T y
    # For simplicity, use single feature case
    if n_features == 1:
        sum_x = sum(X[i][0] for i in range(n))
        sum_y = sum(y)
        sum_xy = sum(X[i][0] * y[i] for i in range(n))
        sum_xx = sum(X[i][0] ** 2 for i in range(n))

        denom = n * sum_xx - sum_x**2
        if abs(denom) < 1e-10:
            return [0.0], sum_y / n if n > 0 else 0.0

        coef = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - coef * sum_x) / n
        return [coef], intercept

    return [0.0] * n_features, 0.0


def linear_regression_predict(
    X: list[list[float]], coef: list[float], intercept: float
) -> list[float]:
    """Linear regression predict."""
    return [intercept + sum(X[i][j] * coef[j] for j in range(len(coef))) for i in range(len(X))]


def r2_score(y_true: list[float], y_pred: list[float]) -> float:
    """Calculate R² score."""
    if len(y_true) == 0:
        return 0.0
    y_mean = sum(y_true) / len(y_true)
    ss_res = sum((y_true[i] - y_pred[i]) ** 2 for i in range(len(y_true)))
    ss_tot = sum((y_true[i] - y_mean) ** 2 for i in range(len(y_true)))
    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0
    return 1.0 - ss_res / ss_tot


def cross_val_score(
    X: list[list[float]], y: list[float], model: str, n_splits: int = 5
) -> list[float]:
    """Perform cross-validation and return scores."""
    folds = kfold_split(len(X), n_splits)
    scores = []

    for fold in folds:
        X_train = [X[i] for i in fold["train"]]
        y_train = [y[i] for i in fold["train"]]
        X_test = [X[i] for i in fold["test"]]
        y_test = [y[i] for i in fold["test"]]

        if model == "linear_regression":
            coef, intercept = linear_regression_fit(X_train, y_train)
            y_pred = linear_regression_predict(X_test, coef, intercept)
            score = r2_score(y_test, y_pred)
        else:
            score = 0.0

        scores.append(score)

    return scores


def cmd_split(args: argparse.Namespace) -> None:
    """Handle split subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "n_samples" not in data:
        print("Error: Missing 'n_samples'", file=sys.stderr)
        sys.exit(1)

    n_splits = data.get("n_splits", 5)

    try:
        folds = kfold_split(data["n_samples"], n_splits)
        print(json.dumps({"folds": folds}))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_cross_val_score(args: argparse.Namespace) -> None:
    """Handle cross-val-score subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    required = ["X", "y", "model"]
    for field in required:
        if field not in data:
            print(f"Error: Missing '{field}'", file=sys.stderr)
            sys.exit(1)

    n_splits = data.get("n_splits", 5)

    try:
        scores = cross_val_score(data["X"], data["y"], data["model"], n_splits)
        mean_score = sum(scores) / len(scores)
        std_score = math.sqrt(sum((s - mean_score) ** 2 for s in scores) / len(scores))
        print(json.dumps({"scores": scores, "mean_score": mean_score, "std_score": std_score}))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KFold CLI - cross-validation splitting (sklearn-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("split", help="Generate K-fold splits").set_defaults(func=cmd_split)
    subparsers.add_parser("cross-val-score", help="Cross-validation scoring").set_defaults(
        func=cmd_cross_val_score
    )

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
