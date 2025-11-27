#!/usr/bin/env python3
"""Linear layer CLI - flat structure for depyler compatibility.

Implements y = Wx + b for 2D input/output.
"""

import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Linear layer CLI")
    parser.add_argument(
        "--mode", type=str, required=True, choices=["forward", "backward"], help="Mode"
    )
    # Input vector (2D)
    parser.add_argument("--x0", type=float, default=1.0, help="Input x[0]")
    parser.add_argument("--x1", type=float, default=2.0, help="Input x[1]")
    # Weight matrix (2x2)
    parser.add_argument("--w00", type=float, default=1.0, help="W[0,0]")
    parser.add_argument("--w01", type=float, default=0.0, help="W[0,1]")
    parser.add_argument("--w10", type=float, default=0.0, help="W[1,0]")
    parser.add_argument("--w11", type=float, default=1.0, help="W[1,1]")
    # Bias (2D)
    parser.add_argument("--b0", type=float, default=0.0, help="Bias b[0]")
    parser.add_argument("--b1", type=float, default=0.0, help="Bias b[1]")
    # Upstream gradient for backward (2D)
    parser.add_argument("--dy0", type=float, default=1.0, help="Grad dy[0]")
    parser.add_argument("--dy1", type=float, default=1.0, help="Grad dy[1]")

    args = parser.parse_args()

    x0 = args.x0
    x1 = args.x1
    w00 = args.w00
    w01 = args.w01
    w10 = args.w10
    w11 = args.w11
    b0 = args.b0
    b1 = args.b1
    dy0 = args.dy0
    dy1 = args.dy1

    if args.mode == "forward":
        # y = Wx + b
        y0 = w00 * x0 + w01 * x1 + b0
        y1 = w10 * x0 + w11 * x1 + b1
        print(f"y0={y0} y1={y1}")
    elif args.mode == "backward":
        # dx = W^T @ dy
        dx0 = w00 * dy0 + w10 * dy1
        dx1 = w01 * dy0 + w11 * dy1
        # dW = dy @ x^T
        dw00 = dy0 * x0
        dw01 = dy0 * x1
        dw10 = dy1 * x0
        dw11 = dy1 * x1
        # db = dy
        db0 = dy0
        db1 = dy1
        print(
            f"dx0={dx0} dx1={dx1} dw00={dw00} dw01={dw01} dw10={dw10} dw11={dw11} db0={db0} db1={db1}"
        )


if __name__ == "__main__":
    main()
