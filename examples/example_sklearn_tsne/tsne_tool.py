#!/usr/bin/env python3
"""TSNE CLI tool.

A CLI for sklearn-style t-SNE dimensionality reduction.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: van der Maaten & Hinton (2008) t-SNE [10]

Usage:
    echo '{"X": [[1,2,3], [2,3,4], [10,11,12]], "n_components": 2}' | python tsne_tool.py fit-transform
"""

import argparse
import json
import math
import random
import sys


def euclidean_distance(a: list[float], b: list[float]) -> float:
    """Calculate Euclidean distance."""
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(len(a))))


def compute_pairwise_distances(X: list[list[float]]) -> list[list[float]]:
    """Compute pairwise distance matrix."""
    n = len(X)
    D = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = euclidean_distance(X[i], X[j])
            D[i][j] = d
            D[j][i] = d
    return D


def compute_p_ij(D: list[list[float]], perplexity: float) -> list[list[float]]:
    """Compute joint probabilities P_ij using Gaussian kernel."""
    n = len(D)
    P = [[0.0] * n for _ in range(n)]

    # For simplicity, use fixed sigma based on perplexity
    sigma = perplexity / 3.0

    for i in range(n):
        for j in range(n):
            if i != j:
                P[i][j] = math.exp(-(D[i][j] ** 2) / (2 * sigma**2))

    # Normalize
    for i in range(n):
        row_sum = sum(P[i])
        if row_sum > 0:
            for j in range(n):
                P[i][j] /= row_sum

    # Symmetrize
    for i in range(n):
        for j in range(i + 1, n):
            avg = (P[i][j] + P[j][i]) / 2
            P[i][j] = avg
            P[j][i] = avg

    return P


def compute_q_ij(Y: list[list[float]]) -> list[list[float]]:
    """Compute Q_ij using Student t-distribution."""
    n = len(Y)
    Q = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j:
                d_sq = sum((Y[i][k] - Y[j][k]) ** 2 for k in range(len(Y[0])))
                Q[i][j] = 1.0 / (1.0 + d_sq)

    # Normalize
    total = sum(sum(row) for row in Q)
    if total > 0:
        for i in range(n):
            for j in range(n):
                Q[i][j] /= total

    return Q


def fit_transform(
    X: list[list[float]],
    n_components: int = 2,
    perplexity: float = 30.0,
    n_iter: int = 250,
    learning_rate: float = 200.0,
    random_state: int = None,
) -> list[list[float]]:
    """Fit t-SNE and transform data."""
    if len(X) == 0:
        raise ValueError("Empty input data")

    n_samples = len(X)

    # Adjust perplexity if too high
    perplexity = min(perplexity, (n_samples - 1) / 3)
    if perplexity < 1:
        perplexity = 1

    if random_state is not None:
        random.seed(random_state)

    # Initialize Y randomly
    Y = [[random.gauss(0, 0.01) for _ in range(n_components)] for _ in range(n_samples)]

    # Compute pairwise distances and P
    D = compute_pairwise_distances(X)
    P = compute_p_ij(D, perplexity)

    # Gradient descent
    for iteration in range(n_iter):
        Q = compute_q_ij(Y)

        # Compute gradients
        grad = [[0.0] * n_components for _ in range(n_samples)]

        for i in range(n_samples):
            for j in range(n_samples):
                if i != j:
                    pq_diff = P[i][j] - Q[i][j]
                    d_sq = sum((Y[i][k] - Y[j][k]) ** 2 for k in range(n_components))
                    factor = 4.0 * pq_diff / (1.0 + d_sq)
                    for k in range(n_components):
                        grad[i][k] += factor * (Y[i][k] - Y[j][k])

        # Update Y
        lr = learning_rate * (1.0 - iteration / n_iter)  # Decay learning rate
        for i in range(n_samples):
            for k in range(n_components):
                Y[i][k] -= lr * grad[i][k] / n_samples

    return Y


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

    n_components = data.get("n_components", 2)
    perplexity = data.get("perplexity", 30.0)
    n_iter = data.get("n_iter", 250)
    learning_rate = data.get("learning_rate", 200.0)
    random_state = data.get("random_state", None)

    try:
        Y = fit_transform(data["X"], n_components, perplexity, n_iter, learning_rate, random_state)
        print(json.dumps({"X_embedded": Y}))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="TSNE CLI - t-distributed stochastic neighbor embedding (sklearn-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("fit-transform", help="Fit and transform data").set_defaults(
        func=cmd_fit_transform
    )

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
