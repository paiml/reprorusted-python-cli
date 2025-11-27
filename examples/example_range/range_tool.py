#!/usr/bin/env python3
"""Range Example - Range operations CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Range tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    u = subs.add_parser("upto")
    u.add_argument("n", type=int)
    b = subs.add_parser("between")
    b.add_argument("start", type=int)
    b.add_argument("end", type=int)
    st = subs.add_parser("step")
    st.add_argument("start", type=int)
    st.add_argument("end", type=int)
    st.add_argument("step", type=int)

    args = parser.parse_args()
    if args.cmd == "upto":
        result = ""
        i = 0
        while i < args.n:
            if i > 0:
                result = result + " "
            result = result + str(i)
            i = i + 1
        print(result)
    elif args.cmd == "between":
        result = ""
        i = args.start
        while i < args.end:
            if i > args.start:
                result = result + " "
            result = result + str(i)
            i = i + 1
        print(result)
    elif args.cmd == "step":
        result = ""
        i = args.start
        first = True
        while i < args.end:
            if not first:
                result = result + " "
            first = False
            result = result + str(i)
            i = i + args.step
        print(result)


if __name__ == "__main__":
    main()
