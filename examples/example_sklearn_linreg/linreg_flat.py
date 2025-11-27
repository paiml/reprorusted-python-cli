#!/usr/bin/env python3
"""LinearRegression CLI - flat structure (no subcommands).

Uses the same pattern as example_simple/trivial_cli.py for depyler compatibility.
"""

import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LinearRegression CLI")
    parser.add_argument("--mode", type=str, required=True, choices=["fit", "predict"], help="Mode")
    parser.add_argument("--x1", type=float, default=0.0, help="First x value")
    parser.add_argument("--y1", type=float, default=0.0, help="First y value")
    parser.add_argument("--x2", type=float, default=0.0, help="Second x value")
    parser.add_argument("--y2", type=float, default=0.0, help="Second y value")
    parser.add_argument("--x", type=float, default=0.0, help="X value to predict")
    parser.add_argument("--coef", type=float, default=0.0, help="Coefficient")
    parser.add_argument("--intercept", type=float, default=0.0, help="Intercept")

    args = parser.parse_args()

    if args.mode == "fit":
        x1 = args.x1
        y1 = args.y1
        x2 = args.x2
        y2 = args.y2
        if x1 == x2:
            coef = 0.0
            intercept = y1
        else:
            coef = (y2 - y1) / (x2 - x1)
            intercept = y1 - coef * x1
        print(f"coef={coef} intercept={intercept}")
    elif args.mode == "predict":
        x = args.x
        coef = args.coef
        intercept = args.intercept
        y = coef * x + intercept
        print(f"prediction={y}")


if __name__ == "__main__":
    main()
