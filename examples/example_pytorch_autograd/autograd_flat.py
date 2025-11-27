#!/usr/bin/env python3
"""Autograd CLI - flat structure for depyler compatibility.

Demonstrates gradient computation for simple functions.
"""

import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Autograd CLI")
    parser.add_argument(
        "--mode", type=str, required=True, choices=["power", "linear", "product"], help="Mode"
    )
    parser.add_argument("--x", type=float, default=3.0, help="Input x")
    parser.add_argument("--n", type=float, default=2.0, help="Power n (for power mode)")
    parser.add_argument("--a", type=float, default=2.0, help="Coefficient a (for linear mode)")
    parser.add_argument("--b", type=float, default=1.0, help="Bias b (for linear mode)")
    parser.add_argument("--w", type=float, default=4.0, help="Weight w (for product mode)")

    args = parser.parse_args()

    x = args.x
    n = args.n
    a = args.a
    b = args.b
    w = args.w

    if args.mode == "power":
        # f(x) = x^n, df/dx = n * x^(n-1)
        # Compute x^(n-1) manually
        result = 1.0
        power = n - 1.0
        i = 0.0
        while i < power:
            result = result * x
            i = i + 1.0
        grad = n * result
        # Compute value x^n
        value = result * x
        print(f"value={value} grad={grad}")
    elif args.mode == "linear":
        # f(x) = a*x + b, df/dx = a
        value = a * x + b
        grad = a
        print(f"value={value} grad={grad}")
    elif args.mode == "product":
        # f(x,w) = x * w, df/dx = w, df/dw = x
        value = x * w
        grad_x = w
        grad_w = x
        print(f"value={value} grad_x={grad_x} grad_w={grad_w}")


if __name__ == "__main__":
    main()
