#!/usr/bin/env python3
"""Sorted Example - Sorting operations CLI."""

import argparse


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
        nums = [args.a, args.b, args.c, args.d, args.e]
        i = 0
        while i < 5:
            j = i + 1
            while j < 5:
                if nums[j] < nums[i]:
                    tmp = nums[i]
                    nums[i] = nums[j]
                    nums[j] = tmp
                j = j + 1
            i = i + 1
        print(f"{nums[0]} {nums[1]} {nums[2]} {nums[3]} {nums[4]}")
    elif args.cmd == "desc":
        nums = [args.a, args.b, args.c, args.d, args.e]
        i = 0
        while i < 5:
            j = i + 1
            while j < 5:
                if nums[j] > nums[i]:
                    tmp = nums[i]
                    nums[i] = nums[j]
                    nums[j] = tmp
                j = j + 1
            i = i + 1
        print(f"{nums[0]} {nums[1]} {nums[2]} {nums[3]} {nums[4]}")
    elif args.cmd == "alpha":
        words = [args.a, args.b, args.c]
        i = 0
        while i < 3:
            j = i + 1
            while j < 3:
                if words[j] < words[i]:
                    tmp = words[i]
                    words[i] = words[j]
                    words[j] = tmp
                j = j + 1
            i = i + 1
        print(f"{words[0]} {words[1]} {words[2]}")


if __name__ == "__main__":
    main()
