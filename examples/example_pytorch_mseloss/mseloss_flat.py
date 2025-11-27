#!/usr/bin/env python3
"""MSE Loss CLI - flat structure for depyler compatibility.

Mean Squared Error: L = (1/n) * sum((y_pred - y_true)^2)
"""

import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MSE Loss CLI")
    parser.add_argument("--mode", type=str, required=True, choices=["loss", "grad"], help="Mode")
    # Predictions (4 values)
    parser.add_argument("--p0", type=float, default=0.0, help="Prediction 0")
    parser.add_argument("--p1", type=float, default=0.0, help="Prediction 1")
    parser.add_argument("--p2", type=float, default=0.0, help="Prediction 2")
    parser.add_argument("--p3", type=float, default=0.0, help="Prediction 3")
    # Targets (4 values)
    parser.add_argument("--t0", type=float, default=1.0, help="Target 0")
    parser.add_argument("--t1", type=float, default=1.0, help="Target 1")
    parser.add_argument("--t2", type=float, default=1.0, help="Target 2")
    parser.add_argument("--t3", type=float, default=1.0, help="Target 3")

    args = parser.parse_args()

    p0 = args.p0
    p1 = args.p1
    p2 = args.p2
    p3 = args.p3
    t0 = args.t0
    t1 = args.t1
    t2 = args.t2
    t3 = args.t3

    # Differences
    d0 = p0 - t0
    d1 = p1 - t1
    d2 = p2 - t2
    d3 = p3 - t3

    if args.mode == "loss":
        # MSE = mean of squared differences
        mse = (d0 * d0 + d1 * d1 + d2 * d2 + d3 * d3) / 4.0
        print(f"mse={mse}")
    elif args.mode == "grad":
        # d(MSE)/d(p_i) = 2 * (p_i - t_i) / n = 2 * d_i / 4 = d_i / 2
        g0 = d0 / 2.0
        g1 = d1 / 2.0
        g2 = d2 / 2.0
        g3 = d3 / 2.0
        print(f"g0={g0} g1={g1} g2={g2} g3={g3}")


if __name__ == "__main__":
    main()
