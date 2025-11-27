#!/usr/bin/env python3
"""LinearRegression CLI - CLI args only (no stdin JSON).

Uses pure CLI arguments to avoid serde_json::Value type coercion issues.
"""

import argparse


def compute_linreg(x1: float, y1: float, x2: float, y2: float) -> str:
    """Compute linear regression from two points."""
    if x1 == x2:
        return f"coef=0.0 intercept={y1}"

    coef = (y2 - y1) / (x2 - x1)
    intercept = y1 - coef * x1
    return f"coef={coef} intercept={intercept}"


def predict_value(x: float, coef: float, intercept: float) -> str:
    """Predict y = coef * x + intercept."""
    y = coef * x + intercept
    return f"prediction={y}"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LinearRegression CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # fit subcommand
    fit_parser = subparsers.add_parser("fit", help="Fit linear regression from two points")
    fit_parser.add_argument("--x1", type=float, required=True, help="First x value")
    fit_parser.add_argument("--y1", type=float, required=True, help="First y value")
    fit_parser.add_argument("--x2", type=float, required=True, help="Second x value")
    fit_parser.add_argument("--y2", type=float, required=True, help="Second y value")

    # predict subcommand
    pred_parser = subparsers.add_parser("predict", help="Predict using coefficients")
    pred_parser.add_argument("--x", type=float, required=True, help="X value to predict")
    pred_parser.add_argument("--coef", type=float, required=True, help="Coefficient")
    pred_parser.add_argument("--intercept", type=float, required=True, help="Intercept")

    args = parser.parse_args()

    if args.command == "fit":
        result = compute_linreg(args.x1, args.y1, args.x2, args.y2)
        print(result)
    elif args.command == "predict":
        result = predict_value(args.x, args.coef, args.intercept)
        print(result)


if __name__ == "__main__":
    main()
