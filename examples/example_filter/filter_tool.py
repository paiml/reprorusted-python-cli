#!/usr/bin/env python3
"""Filter Example - Filter operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Filter operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    p = subs.add_parser("positive")
    p.add_argument("a", type=int)
    p.add_argument("b", type=int)
    p.add_argument("c", type=int)
    p.add_argument("d", type=int)
    p.add_argument("e", type=int)
    ev = subs.add_parser("even")
    ev.add_argument("a", type=int)
    ev.add_argument("b", type=int)
    ev.add_argument("c", type=int)
    ev.add_argument("d", type=int)
    ev.add_argument("e", type=int)
    od = subs.add_parser("odd")
    od.add_argument("a", type=int)
    od.add_argument("b", type=int)
    od.add_argument("c", type=int)
    od.add_argument("d", type=int)
    od.add_argument("e", type=int)

    args = parser.parse_args()
    if args.cmd == "positive":
        result = ""
        nums = [args.a, args.b, args.c, args.d, args.e]
        i = 0
        while i < 5:
            if nums[i] > 0:
                if len(result) > 0:
                    result = result + " "
                result = result + str(nums[i])
            i = i + 1
        print(result)
    elif args.cmd == "even":
        result = ""
        nums = [args.a, args.b, args.c, args.d, args.e]
        i = 0
        while i < 5:
            if nums[i] % 2 == 0:
                if len(result) > 0:
                    result = result + " "
                result = result + str(nums[i])
            i = i + 1
        print(result)
    elif args.cmd == "odd":
        result = ""
        nums = [args.a, args.b, args.c, args.d, args.e]
        i = 0
        while i < 5:
            if nums[i] % 2 != 0:
                if len(result) > 0:
                    result = result + " "
                result = result + str(nums[i])
            i = i + 1
        print(result)


if __name__ == "__main__":
    main()
