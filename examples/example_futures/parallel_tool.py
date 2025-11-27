#!/usr/bin/env python3
"""Concurrent.futures Example - Parallel processing CLI."""

import argparse
from concurrent.futures import ThreadPoolExecutor


def square(n):
    """Square a number. Depyler: proven to terminate"""
    return n * n


def cmd_sum(args):
    """Sum numbers in parallel. Depyler: proven to terminate"""
    numbers = [int(n) for n in args.numbers]
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda x: x, numbers))
    print(f"Sum: {sum(results)}")


def cmd_square(args):
    """Square numbers in parallel. Depyler: proven to terminate"""
    numbers = [int(n) for n in args.numbers]
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(square, numbers))
    for n, r in zip(numbers, results, strict=True):
        print(f"{n}^2 = {r}")


def main():
    parser = argparse.ArgumentParser(description="Parallel processing tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    s = subparsers.add_parser("sum")
    s.add_argument("numbers", nargs="+")

    sq = subparsers.add_parser("square")
    sq.add_argument("numbers", nargs="+")

    args = parser.parse_args()
    if args.command == "sum":
        cmd_sum(args)
    elif args.command == "square":
        cmd_square(args)


if __name__ == "__main__":
    main()
