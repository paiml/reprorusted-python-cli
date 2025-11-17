#!/usr/bin/env python3
"""
Simple test for with open() support
"""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Test with open()")
    parser.add_argument("--write", action="store_true", help="Write to file")
    parser.add_argument("--read", action="store_true", help="Read from file")
    args = parser.parse_args()

    if args.write:
        with open("test.txt", "w") as f:
            f.write("Hello from Rust!\n")
        print("Written to test.txt")

    if args.read:
        with open("test.txt") as f:
            content = f.read()
        print(f"Read: {content}")


if __name__ == "__main__":
    main()
