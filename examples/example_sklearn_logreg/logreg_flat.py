#!/usr/bin/env python3
"""LogisticRegression CLI - flat structure for depyler compatibility.

Implements binary classification with sigmoid activation.
"""

import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LogisticRegression CLI")
    parser.add_argument(
        "--mode", type=str, required=True, choices=["sigmoid", "predict"], help="Mode"
    )
    parser.add_argument("--x", type=float, default=0.0, help="Input value")
    parser.add_argument("--weight", type=float, default=1.0, help="Weight")
    parser.add_argument("--bias", type=float, default=0.0, help="Bias")
    parser.add_argument("--threshold", type=float, default=0.5, help="Classification threshold")

    args = parser.parse_args()

    if args.mode == "sigmoid":
        # Compute sigmoid(x)
        x = args.x
        neg_bound = 0.0 - 20.0
        # Avoid overflow: clamp to reasonable range
        if x > 20.0:
            result = 1.0
        elif x < neg_bound:
            result = 0.0
        else:
            # e^(-x) approximation for small values
            exp_neg_x = 1.0
            term = 1.0
            i = 1.0
            while i <= 10.0:
                term = term * (-x) / i
                exp_neg_x = exp_neg_x + term
                i = i + 1.0
            result = 1.0 / (1.0 + exp_neg_x)
        print(f"sigmoid={result}")
    elif args.mode == "predict":
        x = args.x
        w = args.weight
        b = args.bias
        threshold = args.threshold
        # Linear combination
        z = w * x + b
        neg_bound = 0.0 - 20.0
        # Sigmoid
        if z > 20.0:
            prob = 1.0
        elif z < neg_bound:
            prob = 0.0
        else:
            exp_neg_z = 1.0
            term = 1.0
            i = 1.0
            while i <= 10.0:
                term = term * (-z) / i
                exp_neg_z = exp_neg_z + term
                i = i + 1.0
            prob = 1.0 / (1.0 + exp_neg_z)
        # Classification
        if prob >= threshold:
            label = 1
        else:
            label = 0
        print(f"prob={prob} label={label}")


if __name__ == "__main__":
    main()
