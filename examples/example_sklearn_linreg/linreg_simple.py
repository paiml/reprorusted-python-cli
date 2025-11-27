#!/usr/bin/env python3
"""LinearRegression CLI - simplified for depyler compatibility."""

import argparse
import json
import sys


def fit_simple(x_vals: list, y_vals: list) -> dict:
    """Simple linear regression y = mx + b using least squares."""
    n = len(x_vals)
    if n == 0:
        return {"coef": 0.0, "intercept": 0.0}

    sum_x = 0.0
    sum_y = 0.0
    sum_xy = 0.0
    sum_xx = 0.0

    i = 0
    while i < n:
        sum_x = sum_x + x_vals[i]
        sum_y = sum_y + y_vals[i]
        sum_xy = sum_xy + x_vals[i] * y_vals[i]
        sum_xx = sum_xx + x_vals[i] * x_vals[i]
        i = i + 1

    denom = n * sum_xx - sum_x * sum_x
    if denom == 0:
        return {"coef": 0.0, "intercept": sum_y / n}

    coef = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - coef * sum_x) / n

    return {"coef": coef, "intercept": intercept}


def predict_simple(x_vals: list, coef: float, intercept: float) -> list:
    """Predict y = coef * x + intercept."""
    result = []
    i = 0
    while i < len(x_vals):
        pred = coef * x_vals[i] + intercept
        result.append(pred)
        i = i + 1
    return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LinearRegression CLI")
    parser.add_argument("command", choices=["fit", "predict"], help="Command")
    args = parser.parse_args()

    data = json.load(sys.stdin)

    if args.command == "fit":
        result = fit_simple(data["x"], data["y"])
        print(json.dumps(result))
    elif args.command == "predict":
        preds = predict_simple(data["x"], data["coef"], data["intercept"])
        print(json.dumps({"predictions": preds}))


if __name__ == "__main__":
    main()
