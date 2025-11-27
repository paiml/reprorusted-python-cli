#!/usr/bin/env python3
"""Tensor ops CLI - flat structure for depyler compatibility.

Basic tensor operations (2x2 matrix).
"""

import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Tensor CLI")
    parser.add_argument(
        "--mode", type=str, required=True, choices=["add", "mul", "matmul"], help="Mode"
    )
    # 2x2 matrix A
    parser.add_argument("--a00", type=float, default=1.0, help="A[0,0]")
    parser.add_argument("--a01", type=float, default=0.0, help="A[0,1]")
    parser.add_argument("--a10", type=float, default=0.0, help="A[1,0]")
    parser.add_argument("--a11", type=float, default=1.0, help="A[1,1]")
    # 2x2 matrix B
    parser.add_argument("--b00", type=float, default=1.0, help="B[0,0]")
    parser.add_argument("--b01", type=float, default=0.0, help="B[0,1]")
    parser.add_argument("--b10", type=float, default=0.0, help="B[1,0]")
    parser.add_argument("--b11", type=float, default=1.0, help="B[1,1]")

    args = parser.parse_args()

    a00 = args.a00
    a01 = args.a01
    a10 = args.a10
    a11 = args.a11
    b00 = args.b00
    b01 = args.b01
    b10 = args.b10
    b11 = args.b11

    if args.mode == "add":
        # Element-wise add
        c00 = a00 + b00
        c01 = a01 + b01
        c10 = a10 + b10
        c11 = a11 + b11
        print(f"c00={c00} c01={c01} c10={c10} c11={c11}")
    elif args.mode == "mul":
        # Element-wise multiply
        c00 = a00 * b00
        c01 = a01 * b01
        c10 = a10 * b10
        c11 = a11 * b11
        print(f"c00={c00} c01={c01} c10={c10} c11={c11}")
    elif args.mode == "matmul":
        # Matrix multiplication
        c00 = a00 * b00 + a01 * b10
        c01 = a00 * b01 + a01 * b11
        c10 = a10 * b00 + a11 * b10
        c11 = a10 * b01 + a11 * b11
        print(f"c00={c00} c01={c01} c10={c10} c11={c11}")


if __name__ == "__main__":
    main()
