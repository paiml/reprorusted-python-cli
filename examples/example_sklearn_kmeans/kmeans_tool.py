#!/usr/bin/env python3
"""KMeans CLI tool.

A CLI for sklearn-style KMeans clustering with fit/predict/labels pattern.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: Lloyd (1982) Least Squares Quantization in PCM [9]

Usage:
    echo '{"X": [[1,1], [2,2], [8,8], [9,9]], "n_clusters": 2}' | python kmeans_tool.py fit
"""

import argparse
import json
import math
import random
import sys


def euclidean_distance(a: list[float], b: list[float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(len(a))))


def assign_labels(X: list[list[float]], centroids: list[list[float]]) -> list[int]:
    """Assign each point to nearest centroid."""
    labels = []
    for point in X:
        min_dist = float("inf")
        min_idx = 0
        for i, centroid in enumerate(centroids):
            dist = euclidean_distance(point, centroid)
            if dist < min_dist:
                min_dist = dist
                min_idx = i
        labels.append(min_idx)
    return labels


def update_centroids(
    X: list[list[float]], labels: list[int], n_clusters: int, n_features: int
) -> list[list[float]]:
    """Update centroids as mean of assigned points."""
    centroids = [[0.0] * n_features for _ in range(n_clusters)]
    counts = [0] * n_clusters

    for i, point in enumerate(X):
        cluster = labels[i]
        counts[cluster] += 1
        for j in range(n_features):
            centroids[cluster][j] += point[j]

    for i in range(n_clusters):
        if counts[i] > 0:
            for j in range(n_features):
                centroids[i][j] /= counts[i]

    return centroids


def compute_inertia(X: list[list[float]], labels: list[int], centroids: list[list[float]]) -> float:
    """Compute within-cluster sum of squares (inertia)."""
    inertia = 0.0
    for i, point in enumerate(X):
        centroid = centroids[labels[i]]
        inertia += euclidean_distance(point, centroid) ** 2
    return inertia


def fit(
    X: list[list[float]],
    n_clusters: int = 2,
    max_iter: int = 300,
    random_state: int = None,
) -> dict:
    """Fit KMeans using Lloyd's algorithm.

    Args:
        X: Data points (n_samples, n_features)
        n_clusters: Number of clusters
        max_iter: Maximum iterations
        random_state: Random seed for reproducibility
    """
    if len(X) == 0:
        raise ValueError("Empty input data")

    n_samples = len(X)
    n_features = len(X[0])

    if n_clusters > n_samples:
        raise ValueError(
            f"n_clusters ({n_clusters}) cannot be greater than n_samples ({n_samples})"
        )

    # Set random seed
    if random_state is not None:
        random.seed(random_state)

    # Initialize centroids using random points from X
    indices = random.sample(range(n_samples), n_clusters)
    centroids = [X[i][:] for i in indices]

    labels = []
    for _ in range(max_iter):
        # Assign labels
        new_labels = assign_labels(X, centroids)

        # Check for convergence
        if labels == new_labels:
            break
        labels = new_labels

        # Update centroids
        centroids = update_centroids(X, labels, n_clusters, n_features)

    inertia = compute_inertia(X, labels, centroids)

    return {"labels": labels, "centroids": centroids, "inertia": inertia}


def predict(X: list[list[float]], centroids: list[list[float]]) -> list[int]:
    """Predict cluster labels for new data."""
    return assign_labels(X, centroids)


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

    n_clusters = data.get("n_clusters", 2)
    max_iter = data.get("max_iter", 300)
    random_state = data.get("random_state", None)

    try:
        result = fit(data["X"], n_clusters, max_iter, random_state)
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

    required = ["X", "centroids"]
    for field in required:
        if field not in data:
            print(f"Error: Missing required field '{field}'", file=sys.stderr)
            sys.exit(1)

    labels = predict(data["X"], data["centroids"])
    print(json.dumps({"labels": labels}))


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KMeans CLI - clustering with Lloyd's algorithm (sklearn-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # fit subcommand
    fit_parser = subparsers.add_parser("fit", help="Fit KMeans model")
    fit_parser.set_defaults(func=cmd_fit)

    # predict subcommand
    predict_parser = subparsers.add_parser("predict", help="Predict cluster labels")
    predict_parser.set_defaults(func=cmd_predict)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
