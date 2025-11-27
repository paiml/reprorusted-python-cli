#!/usr/bin/env python3
"""LogisticRegression CLI tool.

A CLI for sklearn-style LogisticRegression with fit/predict/score pattern.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: Pedregosa et al. (2011) sklearn API design [1]

Usage:
    echo '{"X": [[1], [2], [8], [9]], "y": [0, 0, 1, 1]}' | python logreg_tool.py fit
    echo '{"X": [[5]], "coef": [1.0], "intercept": -5.0}' | python logreg_tool.py predict
"""

import argparse
import json
import math
import sys


def sigmoid(x: float) -> float:
    """Sigmoid activation function."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    else:
        exp_x = math.exp(x)
        return exp_x / (1.0 + exp_x)


def fit(
    X: list[list[float]],
    y: list[int],
    learning_rate: float = 0.1,
    max_iter: int = 1000,
) -> dict:
    """Fit logistic regression using gradient descent.

    Uses batch gradient descent to minimize cross-entropy loss.
    """
    if len(X) == 0 or len(y) == 0:
        raise ValueError("Empty input data")

    if len(X) != len(y):
        raise ValueError(f"Dimension mismatch: X has {len(X)} samples, y has {len(y)}")

    n_samples = len(X)
    n_features = len(X[0])

    # Initialize weights
    coef = [0.0] * n_features
    intercept = 0.0

    # Gradient descent
    for _ in range(max_iter):
        # Compute gradients
        grad_coef = [0.0] * n_features
        grad_intercept = 0.0

        for i in range(n_samples):
            # Compute prediction
            z = intercept
            for j in range(n_features):
                z += coef[j] * X[i][j]
            pred = sigmoid(z)

            # Compute error
            error = pred - y[i]

            # Accumulate gradients
            grad_intercept += error
            for j in range(n_features):
                grad_coef[j] += error * X[i][j]

        # Update weights
        intercept -= learning_rate * grad_intercept / n_samples
        for j in range(n_features):
            coef[j] -= learning_rate * grad_coef[j] / n_samples

    return {"coef": coef, "intercept": intercept}


def predict_proba(X: list[list[float]], coef: list[float], intercept: float) -> list[float]:
    """Predict probabilities for class 1."""
    probabilities = []
    for row in X:
        z = intercept
        for i, val in enumerate(row):
            z += val * coef[i]
        probabilities.append(sigmoid(z))
    return probabilities


def predict(X: list[list[float]], coef: list[float], intercept: float) -> list[int]:
    """Predict class labels (0 or 1)."""
    probs = predict_proba(X, coef, intercept)
    return [1 if p >= 0.5 else 0 for p in probs]


def score(X: list[list[float]], y: list[int], coef: list[float], intercept: float) -> float:
    """Calculate accuracy score."""
    predictions = predict(X, coef, intercept)
    correct = sum(1 for i in range(len(y)) if predictions[i] == y[i])
    return correct / len(y)


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

    learning_rate = data.get("learning_rate", 0.1)
    max_iter = data.get("max_iter", 1000)

    try:
        result = fit(data["X"], data["y"], learning_rate, max_iter)
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


def cmd_predict_proba(args: argparse.Namespace) -> None:
    """Handle predict-proba subcommand."""
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

    probabilities = predict_proba(data["X"], data["coef"], data["intercept"])
    print(json.dumps({"probabilities": probabilities}))


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

    accuracy = score(data["X"], data["y"], data["coef"], data["intercept"])
    print(json.dumps({"accuracy": accuracy}))


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

    learning_rate = data.get("learning_rate", 0.1)
    max_iter = data.get("max_iter", 1000)

    try:
        fit_result = fit(data["X_train"], data["y_train"], learning_rate, max_iter)
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

    learning_rate = data.get("learning_rate", 0.1)
    max_iter = data.get("max_iter", 1000)

    try:
        fit_result = fit(data["X"], data["y"], learning_rate, max_iter)
        accuracy = score(data["X"], data["y"], fit_result["coef"], fit_result["intercept"])
        result = {
            "coef": fit_result["coef"],
            "intercept": fit_result["intercept"],
            "accuracy": accuracy,
        }
        print(json.dumps(result))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LogisticRegression CLI - fit/predict/score pattern (sklearn-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # fit subcommand
    fit_parser = subparsers.add_parser("fit", help="Fit logistic regression model")
    fit_parser.set_defaults(func=cmd_fit)

    # predict subcommand
    predict_parser = subparsers.add_parser("predict", help="Predict class labels")
    predict_parser.set_defaults(func=cmd_predict)

    # predict-proba subcommand
    predict_proba_parser = subparsers.add_parser("predict-proba", help="Predict probabilities")
    predict_proba_parser.set_defaults(func=cmd_predict_proba)

    # score subcommand
    score_parser = subparsers.add_parser("score", help="Calculate accuracy score")
    score_parser.set_defaults(func=cmd_score)

    # fit-predict subcommand
    fit_predict_parser = subparsers.add_parser(
        "fit-predict", help="Fit model and predict on test data"
    )
    fit_predict_parser.set_defaults(func=cmd_fit_predict)

    # fit-score subcommand
    fit_score_parser = subparsers.add_parser("fit-score", help="Fit model and calculate accuracy")
    fit_score_parser.set_defaults(func=cmd_fit_score)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
