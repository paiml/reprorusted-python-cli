#!/usr/bin/env python3
"""LinearRegression CLI tool.

A CLI for sklearn LinearRegression with fit/predict/score pattern.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: Pedregosa et al. (2011) sklearn API design [1]

Usage:
    echo '{"X": [[1], [2], [3]], "y": [2, 4, 6]}' | python linreg_tool.py fit
    echo '{"X": [[4]], "coef": [2.0], "intercept": 0.0}' | python linreg_tool.py predict
"""

import argparse
import json
import sys


def fit(X: list[list[float]], y: list[float]) -> dict:
    """Fit linear regression using ordinary least squares.

    Uses the normal equation: beta = (X^T X)^-1 X^T y
    For numerical stability with single feature, uses direct formula.
    """
    if len(X) == 0 or len(y) == 0:
        raise ValueError("Empty input data")

    if len(X) != len(y):
        raise ValueError(f"Dimension mismatch: X has {len(X)} samples, y has {len(y)}")

    n_samples = len(X)
    n_features = len(X[0])

    # Add bias column (column of 1s) to X
    X_with_bias = [[1.0] + row for row in X]

    # Compute X^T X
    XtX = [[0.0] * (n_features + 1) for _ in range(n_features + 1)]
    for i in range(n_features + 1):
        for j in range(n_features + 1):
            for k in range(n_samples):
                XtX[i][j] += X_with_bias[k][i] * X_with_bias[k][j]

    # Compute X^T y
    Xty = [0.0] * (n_features + 1)
    for i in range(n_features + 1):
        for k in range(n_samples):
            Xty[i] += X_with_bias[k][i] * y[k]

    # Solve using Gaussian elimination with partial pivoting
    coeffs = solve_linear_system(XtX, Xty)

    intercept = coeffs[0]
    coef = coeffs[1:]

    return {"coef": coef, "intercept": intercept}


def solve_linear_system(A: list[list[float]], b: list[float]) -> list[float]:
    """Solve Ax = b using Gaussian elimination with partial pivoting."""
    n = len(A)

    # Create augmented matrix
    aug = [row[:] + [b[i]] for i, row in enumerate(A)]

    # Forward elimination with partial pivoting
    for col in range(n):
        # Find pivot
        max_row = col
        for row in range(col + 1, n):
            if abs(aug[row][col]) > abs(aug[max_row][col]):
                max_row = row

        # Swap rows
        aug[col], aug[max_row] = aug[max_row], aug[col]

        # Check for zero pivot
        if abs(aug[col][col]) < 1e-12:
            raise ValueError("Matrix is singular or nearly singular")

        # Eliminate below
        for row in range(col + 1, n):
            factor = aug[row][col] / aug[col][col]
            for j in range(col, n + 1):
                aug[row][j] -= factor * aug[col][j]

    # Back substitution
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = aug[i][n]
        for j in range(i + 1, n):
            x[i] -= aug[i][j] * x[j]
        x[i] /= aug[i][i]

    return x


def predict(X: list[list[float]], coef: list[float], intercept: float) -> list[float]:
    """Predict using linear model: y = X @ coef + intercept."""
    predictions = []
    for row in X:
        pred = intercept
        for i, val in enumerate(row):
            pred += val * coef[i]
        predictions.append(pred)
    return predictions


def score(X: list[list[float]], y: list[float], coef: list[float], intercept: float) -> float:
    """Calculate R-squared score.

    R² = 1 - SS_res / SS_tot
    where SS_res = sum((y_true - y_pred)²)
          SS_tot = sum((y_true - y_mean)²)
    """
    predictions = predict(X, coef, intercept)

    # Calculate mean of y
    y_mean = sum(y) / len(y)

    # Calculate SS_res and SS_tot
    ss_res = sum((y[i] - predictions[i]) ** 2 for i in range(len(y)))
    ss_tot = sum((y[i] - y_mean) ** 2 for i in range(len(y)))

    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0

    return 1.0 - ss_res / ss_tot


def cmd_fit(args: argparse.Namespace) -> None:
    """Handle fit subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    if "X" not in data:
        print("Error: Missing required field 'X'", file=sys.stderr)
        sys.exit(1)
    if "y" not in data:
        print("Error: Missing required field 'y'", file=sys.stderr)
        sys.exit(1)

    try:
        result = fit(data["X"], data["y"])
        print(json.dumps(result))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_predict(args: argparse.Namespace) -> None:
    """Handle predict subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    required = ["X", "coef", "intercept"]
    for field in required:
        if field not in data:
            print(f"Error: Missing required field '{field}'", file=sys.stderr)
            sys.exit(1)

    predictions = predict(data["X"], data["coef"], data["intercept"])
    print(json.dumps({"predictions": predictions}))


def cmd_score(args: argparse.Namespace) -> None:
    """Handle score subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    required = ["X", "y", "coef", "intercept"]
    for field in required:
        if field not in data:
            print(f"Error: Missing required field '{field}'", file=sys.stderr)
            sys.exit(1)

    r2 = score(data["X"], data["y"], data["coef"], data["intercept"])
    print(json.dumps({"r2": r2}))


def cmd_fit_predict(args: argparse.Namespace) -> None:
    """Handle fit-predict subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    required = ["X_train", "y_train", "X_test"]
    for field in required:
        if field not in data:
            print(f"Error: Missing required field '{field}'", file=sys.stderr)
            sys.exit(1)

    try:
        fit_result = fit(data["X_train"], data["y_train"])
        predictions = predict(data["X_test"], fit_result["coef"], fit_result["intercept"])
        result = {
            "coef": fit_result["coef"],
            "intercept": fit_result["intercept"],
            "predictions": predictions,
        }
        print(json.dumps(result))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_fit_score(args: argparse.Namespace) -> None:
    """Handle fit-score subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    required = ["X", "y"]
    for field in required:
        if field not in data:
            print(f"Error: Missing required field '{field}'", file=sys.stderr)
            sys.exit(1)

    try:
        fit_result = fit(data["X"], data["y"])
        r2 = score(data["X"], data["y"], fit_result["coef"], fit_result["intercept"])
        result = {"coef": fit_result["coef"], "intercept": fit_result["intercept"], "r2": r2}
        print(json.dumps(result))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LinearRegression CLI - fit/predict/score pattern (sklearn-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # fit subcommand
    fit_parser = subparsers.add_parser("fit", help="Fit linear regression model")
    fit_parser.set_defaults(func=cmd_fit)

    # predict subcommand
    predict_parser = subparsers.add_parser("predict", help="Predict using fitted model")
    predict_parser.set_defaults(func=cmd_predict)

    # score subcommand
    score_parser = subparsers.add_parser("score", help="Calculate R-squared score")
    score_parser.set_defaults(func=cmd_score)

    # fit-predict subcommand
    fit_predict_parser = subparsers.add_parser(
        "fit-predict", help="Fit model and predict on test data"
    )
    fit_predict_parser.set_defaults(func=cmd_fit_predict)

    # fit-score subcommand
    fit_score_parser = subparsers.add_parser("fit-score", help="Fit model and calculate R-squared")
    fit_score_parser.set_defaults(func=cmd_fit_score)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
