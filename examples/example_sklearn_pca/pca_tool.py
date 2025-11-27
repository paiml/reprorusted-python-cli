#!/usr/bin/env python3
"""PCA CLI tool.

A CLI for sklearn-style PCA dimensionality reduction.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: van der Maaten & Hinton (2008) [10]

Usage:
    echo '{"X": [[1,2,3], [2,4,6]], "n_components": 2}' | python pca_tool.py fit-transform
"""

import argparse
import json
import math
import sys


def mean_center(X: list[list[float]]) -> tuple[list[list[float]], list[float]]:
    """Center data by subtracting mean."""
    n_samples = len(X)
    n_features = len(X[0])

    mean = [0.0] * n_features
    for row in X:
        for j in range(n_features):
            mean[j] += row[j]
    mean = [m / n_samples for m in mean]

    X_centered = []
    for row in X:
        X_centered.append([row[j] - mean[j] for j in range(n_features)])

    return X_centered, mean


def covariance_matrix(X: list[list[float]]) -> list[list[float]]:
    """Compute covariance matrix of centered data."""
    n_samples = len(X)
    n_features = len(X[0])

    cov = [[0.0] * n_features for _ in range(n_features)]
    for i in range(n_features):
        for j in range(n_features):
            for k in range(n_samples):
                cov[i][j] += X[k][i] * X[k][j]
            cov[i][j] /= n_samples - 1 if n_samples > 1 else 1

    return cov


def power_iteration(matrix: list[list[float]], num_iter: int = 100) -> tuple[list[float], float]:
    """Find dominant eigenvector using power iteration."""
    n = len(matrix)
    # Initialize random vector
    vec = [1.0 / math.sqrt(n)] * n

    for _ in range(num_iter):
        # Multiply matrix by vector
        new_vec = [0.0] * n
        for i in range(n):
            for j in range(n):
                new_vec[i] += matrix[i][j] * vec[j]

        # Compute norm
        norm = math.sqrt(sum(v * v for v in new_vec))
        if norm < 1e-10:
            break

        # Normalize
        vec = [v / norm for v in new_vec]

    # Compute eigenvalue (Rayleigh quotient)
    mv = [sum(matrix[i][j] * vec[j] for j in range(n)) for i in range(n)]
    eigenvalue = sum(vec[i] * mv[i] for i in range(n))

    return vec, eigenvalue


def deflate_matrix(
    matrix: list[list[float]], eigenvec: list[float], eigenval: float
) -> list[list[float]]:
    """Deflate matrix by removing contribution of eigenvector."""
    n = len(matrix)
    result = [[matrix[i][j] for j in range(n)] for i in range(n)]

    for i in range(n):
        for j in range(n):
            result[i][j] -= eigenval * eigenvec[i] * eigenvec[j]

    return result


def fit(X: list[list[float]], n_components: int = None) -> dict:
    """Fit PCA to compute principal components."""
    if len(X) == 0:
        raise ValueError("Empty input data")

    n_samples = len(X)
    n_features = len(X[0])

    if n_components is None:
        n_components = min(n_samples, n_features)

    if n_components > n_features:
        raise ValueError(f"n_components ({n_components}) > n_features ({n_features})")

    # Center data
    X_centered, mean = mean_center(X)

    # Compute covariance matrix
    cov = covariance_matrix(X_centered)

    # Extract principal components using power iteration
    components = []
    eigenvalues = []
    matrix = [row[:] for row in cov]

    for _ in range(n_components):
        eigenvec, eigenval = power_iteration(matrix)
        components.append(eigenvec)
        eigenvalues.append(max(eigenval, 0))  # Ensure non-negative
        matrix = deflate_matrix(matrix, eigenvec, eigenval)

    # Compute explained variance ratio
    total_var = sum(eigenvalues) if sum(eigenvalues) > 0 else 1
    explained_variance_ratio = [e / total_var for e in eigenvalues]

    return {
        "components": components,
        "mean": mean,
        "explained_variance_ratio": explained_variance_ratio,
    }


def transform(
    X: list[list[float]], components: list[list[float]], mean: list[float]
) -> list[list[float]]:
    """Transform data using fitted PCA."""
    n_samples = len(X)
    n_features = len(X[0])

    # Center data
    X_centered = [[X[i][j] - mean[j] for j in range(n_features)] for i in range(n_samples)]

    # Project onto components
    X_transformed = []
    for row in X_centered:
        transformed = []
        for comp in components:
            proj = sum(row[j] * comp[j] for j in range(n_features))
            transformed.append(proj)
        X_transformed.append(transformed)

    return X_transformed


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

    n_components = data.get("n_components", None)

    try:
        result = fit(data["X"], n_components)
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

    required = ["X", "components", "mean"]
    for field in required:
        if field not in data:
            print(f"Error: Missing '{field}'", file=sys.stderr)
            sys.exit(1)

    X_transformed = transform(data["X"], data["components"], data["mean"])
    print(json.dumps({"X_transformed": X_transformed}))


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

    n_components = data.get("n_components", None)

    try:
        fit_result = fit(data["X"], n_components)
        X_transformed = transform(data["X"], fit_result["components"], fit_result["mean"])
        result = {
            "X_transformed": X_transformed,
            "components": fit_result["components"],
            "mean": fit_result["mean"],
            "explained_variance_ratio": fit_result["explained_variance_ratio"],
        }
        print(json.dumps(result))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PCA CLI - dimensionality reduction (sklearn-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    fit_parser = subparsers.add_parser("fit", help="Fit PCA model")
    fit_parser.set_defaults(func=cmd_fit)

    transform_parser = subparsers.add_parser("transform", help="Transform data")
    transform_parser.set_defaults(func=cmd_transform)

    fit_transform_parser = subparsers.add_parser("fit-transform", help="Fit and transform")
    fit_transform_parser.set_defaults(func=cmd_fit_transform)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
