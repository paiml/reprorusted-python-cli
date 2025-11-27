#!/usr/bin/env python3
"""StandardScaler CLI - flat structure for depyler compatibility.

Standardize features by removing mean and scaling to unit variance.
"""

import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="StandardScaler CLI")
    parser.add_argument(
        "--mode", type=str, required=True, choices=["fit", "transform"], help="Mode"
    )
    # 4 data points
    parser.add_argument("--x0", type=float, default=1.0, help="Data point 0")
    parser.add_argument("--x1", type=float, default=2.0, help="Data point 1")
    parser.add_argument("--x2", type=float, default=3.0, help="Data point 2")
    parser.add_argument("--x3", type=float, default=4.0, help="Data point 3")
    # For transform mode
    parser.add_argument("--mean", type=float, default=0.0, help="Mean for transform")
    parser.add_argument("--std", type=float, default=1.0, help="Std for transform")
    parser.add_argument("--value", type=float, default=0.0, help="Value to transform")

    args = parser.parse_args()

    x0 = args.x0
    x1 = args.x1
    x2 = args.x2
    x3 = args.x3

    if args.mode == "fit":
        # Compute mean
        mean = (x0 + x1 + x2 + x3) / 4.0

        # Compute variance
        diff0 = x0 - mean
        diff1 = x1 - mean
        diff2 = x2 - mean
        diff3 = x3 - mean
        var = (diff0 * diff0 + diff1 * diff1 + diff2 * diff2 + diff3 * diff3) / 4.0

        # Compute std (sqrt via Newton-Raphson)
        std = var / 2.0
        if var > 0.0:
            i = 0.0
            while i < 10.0:
                std = (std + var / std) / 2.0
                i = i + 1.0
        else:
            std = 0.0

        print(f"mean={mean} std={std}")
    elif args.mode == "transform":
        mean = args.mean
        std = args.std
        value = args.value
        if std > 0.0:
            scaled = (value - mean) / std
        else:
            scaled = 0.0
        print(f"scaled={scaled}")


if __name__ == "__main__":
    main()
