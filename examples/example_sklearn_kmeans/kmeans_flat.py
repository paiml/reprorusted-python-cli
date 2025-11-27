#!/usr/bin/env python3
"""KMeans CLI - flat structure for depyler compatibility.

Simple 1D k-means with 4 fixed data points for demonstration.
"""

import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="KMeans CLI")
    parser.add_argument(
        "--mode", type=str, required=True, choices=["cluster", "centroid"], help="Mode"
    )
    # 4 data points
    parser.add_argument("--x0", type=float, default=0.0, help="Data point 0")
    parser.add_argument("--x1", type=float, default=1.0, help="Data point 1")
    parser.add_argument("--x2", type=float, default=5.0, help="Data point 2")
    parser.add_argument("--x3", type=float, default=6.0, help="Data point 3")
    # 2 initial centroids
    parser.add_argument("--c0", type=float, default=0.5, help="Centroid 0")
    parser.add_argument("--c1", type=float, default=5.5, help="Centroid 1")
    # Iterations
    parser.add_argument("--iters", type=float, default=3.0, help="Number of iterations")

    args = parser.parse_args()

    x0 = args.x0
    x1 = args.x1
    x2 = args.x2
    x3 = args.x3
    c0 = args.c0
    c1 = args.c1
    iters = args.iters

    # Initialize labels
    l0 = 0.0
    l1 = 0.0
    l2 = 0.0
    l3 = 0.0

    # K-means iterations
    iter_count = 0.0
    while iter_count < iters:
        # Assign labels (0 or 1) based on closest centroid
        # abs() via conditional
        d0_c0 = x0 - c0
        if d0_c0 < 0.0:
            d0_c0 = 0.0 - d0_c0
        d0_c1 = x0 - c1
        if d0_c1 < 0.0:
            d0_c1 = 0.0 - d0_c1
        if d0_c0 < d0_c1:
            l0 = 0.0
        else:
            l0 = 1.0

        d1_c0 = x1 - c0
        if d1_c0 < 0.0:
            d1_c0 = 0.0 - d1_c0
        d1_c1 = x1 - c1
        if d1_c1 < 0.0:
            d1_c1 = 0.0 - d1_c1
        if d1_c0 < d1_c1:
            l1 = 0.0
        else:
            l1 = 1.0

        d2_c0 = x2 - c0
        if d2_c0 < 0.0:
            d2_c0 = 0.0 - d2_c0
        d2_c1 = x2 - c1
        if d2_c1 < 0.0:
            d2_c1 = 0.0 - d2_c1
        if d2_c0 < d2_c1:
            l2 = 0.0
        else:
            l2 = 1.0

        d3_c0 = x3 - c0
        if d3_c0 < 0.0:
            d3_c0 = 0.0 - d3_c0
        d3_c1 = x3 - c1
        if d3_c1 < 0.0:
            d3_c1 = 0.0 - d3_c1
        if d3_c0 < d3_c1:
            l3 = 0.0
        else:
            l3 = 1.0

        # Update centroids
        sum0 = 0.0
        count0 = 0.0
        sum1 = 0.0
        count1 = 0.0

        if l0 < 0.5:
            sum0 = sum0 + x0
            count0 = count0 + 1.0
        else:
            sum1 = sum1 + x0
            count1 = count1 + 1.0

        if l1 < 0.5:
            sum0 = sum0 + x1
            count0 = count0 + 1.0
        else:
            sum1 = sum1 + x1
            count1 = count1 + 1.0

        if l2 < 0.5:
            sum0 = sum0 + x2
            count0 = count0 + 1.0
        else:
            sum1 = sum1 + x2
            count1 = count1 + 1.0

        if l3 < 0.5:
            sum0 = sum0 + x3
            count0 = count0 + 1.0
        else:
            sum1 = sum1 + x3
            count1 = count1 + 1.0

        if count0 > 0.0:
            c0 = sum0 / count0
        if count1 > 0.0:
            c1 = sum1 / count1

        iter_count = iter_count + 1.0

    if args.mode == "cluster":
        # Output final labels
        print(f"l0={l0} l1={l1} l2={l2} l3={l3}")
    elif args.mode == "centroid":
        # Output final centroids
        print(f"c0={c0} c1={c1}")


if __name__ == "__main__":
    main()
