#!/usr/bin/env python3
"""Statistics Example - Statistical calculations CLI."""

import argparse
import statistics


def cmd_mean(args):
    """Calculate mean. Depyler: proven to terminate"""
    nums = [float(n) for n in args.numbers]
    print(f"Mean: {statistics.mean(nums)}")


def cmd_median(args):
    """Calculate median. Depyler: proven to terminate"""
    nums = [float(n) for n in args.numbers]
    print(f"Median: {statistics.median(nums)}")


def cmd_stdev(args):
    """Calculate standard deviation. Depyler: proven to terminate"""
    nums = [float(n) for n in args.numbers]
    print(f"Stdev: {statistics.stdev(nums):.4f}")


def cmd_mode(args):
    """Calculate mode. Depyler: proven to terminate"""
    nums = [float(n) for n in args.numbers]
    print(f"Mode: {statistics.mode(nums)}")


def main():
    parser = argparse.ArgumentParser(description="Statistics tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for cmd in ["mean", "median", "stdev", "mode"]:
        p = subparsers.add_parser(cmd)
        p.add_argument("numbers", nargs="+")

    args = parser.parse_args()
    {"mean": cmd_mean, "median": cmd_median, "stdev": cmd_stdev, "mode": cmd_mode}[args.command](
        args
    )


if __name__ == "__main__":
    main()
