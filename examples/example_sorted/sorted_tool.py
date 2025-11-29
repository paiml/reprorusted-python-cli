#!/usr/bin/env python3
"""Sorted Example - Sorting operations CLI.

Examples:
    >>> sort_asc([5, 2, 8, 1, 9])
    [1, 2, 5, 8, 9]
    >>> sort_desc([5, 2, 8, 1, 9])
    [9, 8, 5, 2, 1]
"""

import argparse


def sort_asc(nums: list) -> list:
    """Sort list ascending (bubble sort).

    >>> sort_asc([3, 1, 2])
    [1, 2, 3]
    >>> sort_asc([5, 4, 3, 2, 1])
    [1, 2, 3, 4, 5]
    >>> sort_asc([1, 1, 1])
    [1, 1, 1]
    """
    result = nums.copy()
    n = len(result)
    i = 0
    while i < n:
        j = i + 1
        while j < n:
            if result[j] < result[i]:
                tmp = result[i]
                result[i] = result[j]
                result[j] = tmp
            j = j + 1
        i = i + 1
    return result


def sort_desc(nums: list) -> list:
    """Sort list descending (bubble sort).

    >>> sort_desc([3, 1, 2])
    [3, 2, 1]
    >>> sort_desc([1, 2, 3, 4, 5])
    [5, 4, 3, 2, 1]
    """
    result = nums.copy()
    n = len(result)
    i = 0
    while i < n:
        j = i + 1
        while j < n:
            if result[j] > result[i]:
                tmp = result[i]
                result[i] = result[j]
                result[j] = tmp
            j = j + 1
        i = i + 1
    return result


def sort_alpha(words: list) -> list:
    """Sort strings alphabetically.

    >>> sort_alpha(["c", "a", "b"])
    ['a', 'b', 'c']
    >>> sort_alpha(["zebra", "apple", "mango"])
    ['apple', 'mango', 'zebra']
    """
    result = words.copy()
    n = len(result)
    i = 0
    while i < n:
        j = i + 1
        while j < n:
            if result[j] < result[i]:
                tmp = result[i]
                result[i] = result[j]
                result[j] = tmp
            j = j + 1
        i = i + 1
    return result


def main():
    parser = argparse.ArgumentParser(description="Sorting tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    a = subs.add_parser("asc")
    a.add_argument("a", type=int)
    a.add_argument("b", type=int)
    a.add_argument("c", type=int)
    a.add_argument("d", type=int)
    a.add_argument("e", type=int)
    de = subs.add_parser("desc")
    de.add_argument("a", type=int)
    de.add_argument("b", type=int)
    de.add_argument("c", type=int)
    de.add_argument("d", type=int)
    de.add_argument("e", type=int)
    al = subs.add_parser("alpha")
    al.add_argument("a")
    al.add_argument("b")
    al.add_argument("c")

    args = parser.parse_args()
    if args.cmd == "asc":
        nums = sort_asc([args.a, args.b, args.c, args.d, args.e])
        print(f"{nums[0]} {nums[1]} {nums[2]} {nums[3]} {nums[4]}")
    elif args.cmd == "desc":
        nums = sort_desc([args.a, args.b, args.c, args.d, args.e])
        print(f"{nums[0]} {nums[1]} {nums[2]} {nums[3]} {nums[4]}")
    elif args.cmd == "alpha":
        words = sort_alpha([args.a, args.b, args.c])
        print(f"{words[0]} {words[1]} {words[2]}")


if __name__ == "__main__":
    main()
