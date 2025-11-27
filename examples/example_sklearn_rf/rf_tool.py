#!/usr/bin/env python3
"""RandomForestClassifier CLI tool.

A CLI for sklearn-style Random Forest classification.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: Breiman (2001) Random Forests [8]

Usage:
    echo '{"X": [[0], [1], [2], [3]], "y": [0, 0, 1, 1], "n_estimators": 10}' | python rf_tool.py fit
"""

import argparse
import json
import random
import sys
from typing import Any


def gini_impurity(y: list[int]) -> float:
    """Calculate GINI impurity."""
    if len(y) == 0:
        return 0.0
    classes = set(y)
    impurity = 1.0
    for c in classes:
        p = sum(1 for yi in y if yi == c) / len(y)
        impurity -= p**2
    return impurity


def bootstrap_sample(X: list[list[float]], y: list[int]) -> tuple:
    """Create bootstrap sample."""
    n = len(X)
    indices = [random.randint(0, n - 1) for _ in range(n)]
    X_boot = [X[i] for i in indices]
    y_boot = [y[i] for i in indices]
    return X_boot, y_boot


def best_split(X: list[list[float]], y: list[int], max_features: int) -> tuple:
    """Find best split using GINI criterion with feature subsampling."""
    n_samples = len(X)
    n_features = len(X[0]) if n_samples > 0 else 0

    if n_samples == 0:
        return None, None, None, None

    best_gini = float("inf")
    best_feature = None
    best_threshold = None
    best_left_idx = None
    best_right_idx = None

    # Random feature subset
    all_features = list(range(n_features))
    features_to_check = random.sample(all_features, min(max_features, n_features))

    for feature in features_to_check:
        values = sorted({X[i][feature] for i in range(n_samples)})
        if len(values) < 2:
            continue
        thresholds = [(values[i] + values[i + 1]) / 2 for i in range(len(values) - 1)]

        for threshold in thresholds:
            left_idx = [i for i in range(n_samples) if X[i][feature] <= threshold]
            right_idx = [i for i in range(n_samples) if X[i][feature] > threshold]

            if len(left_idx) == 0 or len(right_idx) == 0:
                continue

            left_y = [y[i] for i in left_idx]
            right_y = [y[i] for i in right_idx]

            gini = (
                len(left_y) * gini_impurity(left_y) + len(right_y) * gini_impurity(right_y)
            ) / n_samples

            if gini < best_gini:
                best_gini = gini
                best_feature = feature
                best_threshold = threshold
                best_left_idx = left_idx
                best_right_idx = right_idx

    return best_feature, best_threshold, best_left_idx, best_right_idx


def build_tree(
    X: list[list[float]], y: list[int], depth: int, max_depth: int, max_features: int
) -> dict[str, Any]:
    """Recursively build decision tree."""
    classes = set(y)

    if len(classes) == 1 or depth >= max_depth or len(y) < 2:
        class_counts = {}
        for yi in y:
            class_counts[yi] = class_counts.get(yi, 0) + 1
        majority_class = (
            max(class_counts.keys(), key=lambda k: class_counts[k]) if class_counts else 0
        )
        return {"class": majority_class}

    feature, threshold, left_idx, right_idx = best_split(X, y, max_features)

    if feature is None:
        class_counts = {}
        for yi in y:
            class_counts[yi] = class_counts.get(yi, 0) + 1
        majority_class = (
            max(class_counts.keys(), key=lambda k: class_counts[k]) if class_counts else 0
        )
        return {"class": majority_class}

    left_X = [X[i] for i in left_idx]
    left_y = [y[i] for i in left_idx]
    right_X = [X[i] for i in right_idx]
    right_y = [y[i] for i in right_idx]

    return {
        "feature": feature,
        "threshold": threshold,
        "left": build_tree(left_X, left_y, depth + 1, max_depth, max_features),
        "right": build_tree(right_X, right_y, depth + 1, max_depth, max_features),
    }


def predict_single_tree(tree: dict[str, Any], x: list[float]) -> int:
    """Predict class using single tree."""
    if "class" in tree:
        return tree["class"]
    if x[tree["feature"]] <= tree["threshold"]:
        return predict_single_tree(tree["left"], x)
    return predict_single_tree(tree["right"], x)


def fit(
    X: list[list[float]],
    y: list[int],
    n_estimators: int = 10,
    max_depth: int = 10,
    random_state: int = None,
) -> dict[str, Any]:
    """Fit random forest classifier."""
    if len(X) == 0 or len(y) == 0:
        raise ValueError("Empty input data")

    if random_state is not None:
        random.seed(random_state)

    n_features = len(X[0])
    max_features = max(1, int(n_features**0.5))  # sqrt(n_features)

    trees = []
    for _ in range(n_estimators):
        X_boot, y_boot = bootstrap_sample(X, y)
        tree = build_tree(X_boot, y_boot, 0, max_depth, max_features)
        trees.append(tree)

    return {"trees": trees}


def predict(X: list[list[float]], trees: list[dict[str, Any]]) -> list[int]:
    """Predict class labels using majority voting."""
    predictions = []
    for x in X:
        votes = {}
        for tree in trees:
            pred = predict_single_tree(tree, x)
            votes[pred] = votes.get(pred, 0) + 1
        majority = max(votes.keys(), key=lambda k: votes[k])
        predictions.append(majority)
    return predictions


def score(X: list[list[float]], y: list[int], trees: list[dict[str, Any]]) -> float:
    """Calculate accuracy score."""
    predictions = predict(X, trees)
    correct = sum(1 for i in range(len(y)) if predictions[i] == y[i])
    return correct / len(y)


def cmd_fit(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "X" not in data or "y" not in data:
        print("Error: Missing 'X' or 'y'", file=sys.stderr)
        sys.exit(1)

    n_estimators = data.get("n_estimators", 10)
    max_depth = data.get("max_depth", 10)
    random_state = data.get("random_state", None)

    try:
        result = fit(data["X"], data["y"], n_estimators, max_depth, random_state)
        print(json.dumps(result))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_predict(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "X" not in data or "trees" not in data:
        print("Error: Missing 'X' or 'trees'", file=sys.stderr)
        sys.exit(1)

    predictions = predict(data["X"], data["trees"])
    print(json.dumps({"predictions": predictions}))


def cmd_fit_predict(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    required = ["X_train", "y_train", "X_test"]
    for field in required:
        if field not in data:
            print(f"Error: Missing '{field}'", file=sys.stderr)
            sys.exit(1)

    n_estimators = data.get("n_estimators", 10)
    max_depth = data.get("max_depth", 10)
    random_state = data.get("random_state", 42)

    try:
        result = fit(data["X_train"], data["y_train"], n_estimators, max_depth, random_state)
        predictions = predict(data["X_test"], result["trees"])
        print(json.dumps({"trees": result["trees"], "predictions": predictions}))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_score(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "X" not in data or "y" not in data or "trees" not in data:
        print("Error: Missing 'X', 'y', or 'trees'", file=sys.stderr)
        sys.exit(1)

    accuracy = score(data["X"], data["y"], data["trees"])
    print(json.dumps({"accuracy": accuracy}))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RandomForestClassifier CLI - ensemble classification (sklearn-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("fit", help="Fit random forest").set_defaults(func=cmd_fit)
    subparsers.add_parser("predict", help="Predict class labels").set_defaults(func=cmd_predict)
    subparsers.add_parser("fit-predict", help="Fit and predict").set_defaults(func=cmd_fit_predict)
    subparsers.add_parser("score", help="Calculate accuracy").set_defaults(func=cmd_score)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
