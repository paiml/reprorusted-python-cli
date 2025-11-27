#!/usr/bin/env python3
"""
LRU Cache Example - Memoized computations

Demonstrates functools.lru_cache for memoization.
"""

import argparse
from functools import lru_cache


@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """Memoized fibonacci. Depyler: proven to terminate"""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@lru_cache(maxsize=128)
def factorial(n: int) -> int:
    """Memoized factorial. Depyler: proven to terminate"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def main():
    parser = argparse.ArgumentParser(description="Memoized math tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fib_p = subparsers.add_parser("fib", help="Fibonacci number")
    fib_p.add_argument("n", type=int)

    fact_p = subparsers.add_parser("fact", help="Factorial")
    fact_p.add_argument("n", type=int)

    args = parser.parse_args()
    if args.command == "fib":
        print(f"fib({args.n}) = {fibonacci(args.n)}")
    elif args.command == "fact":
        print(f"fact({args.n}) = {factorial(args.n)}")


if __name__ == "__main__":
    main()
