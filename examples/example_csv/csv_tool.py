#!/usr/bin/env python3
"""CSV Example - CSV-like parsing CLI."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="CSV operations tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    c = subs.add_parser("count")
    c.add_argument("row")
    f = subs.add_parser("field")
    f.add_argument("row")
    f.add_argument("index", type=int)

    args = parser.parse_args()
    if args.cmd == "count":
        fields = args.row.split(",")
        print(len(fields))
    elif args.cmd == "field":
        fields = args.row.split(",")
        print(fields[args.index])


if __name__ == "__main__":
    main()
