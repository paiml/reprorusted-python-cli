#!/usr/bin/env python3
"""Activation functions CLI - flat structure for depyler compatibility.

ReLU, Sigmoid, Tanh implementations.
"""

import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Activation functions CLI")
    parser.add_argument(
        "--mode", type=str, required=True, choices=["relu", "sigmoid", "tanh"], help="Mode"
    )
    parser.add_argument("--x", type=float, default=0.0, help="Input value")

    args = parser.parse_args()

    x = args.x

    if args.mode == "relu":
        # ReLU: max(0, x)
        if x > 0.0:
            y = x
        else:
            y = 0.0
        print(f"y={y}")
    elif args.mode == "sigmoid":
        # Sigmoid: 1 / (1 + e^(-x))
        neg_bound = 0.0 - 20.0
        if x > 20.0:
            y = 1.0
        elif x < neg_bound:
            y = 0.0
        else:
            # Taylor series for e^(-x)
            neg_x = 0.0 - x
            exp_neg_x = 1.0
            term = 1.0
            i = 1.0
            while i <= 10.0:
                term = term * neg_x / i
                exp_neg_x = exp_neg_x + term
                i = i + 1.0
            y = 1.0 / (1.0 + exp_neg_x)
        print(f"y={y}")
    elif args.mode == "tanh":
        # Tanh: (e^x - e^(-x)) / (e^x + e^(-x))
        neg_bound = 0.0 - 10.0
        if x > 10.0:
            y = 1.0
        elif x < neg_bound:
            y = 0.0 - 1.0
        else:
            # Taylor series for e^x and e^(-x)
            neg_x = 0.0 - x
            exp_x = 1.0
            term_p = 1.0
            exp_neg_x = 1.0
            term_n = 1.0
            i = 1.0
            while i <= 10.0:
                term_p = term_p * x / i
                exp_x = exp_x + term_p
                term_n = term_n * neg_x / i
                exp_neg_x = exp_neg_x + term_n
                i = i + 1.0
            denom = exp_x + exp_neg_x
            if denom > 0.0:
                y = (exp_x - exp_neg_x) / denom
            else:
                y = 0.0
        print(f"y={y}")


if __name__ == "__main__":
    main()
