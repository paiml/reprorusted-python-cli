#!/usr/bin/env python3
"""NumPy Cosine Example - Cosine similarity CLI."""

import argparse

import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Cosine similarity tool")
    subs = parser.add_subparsers(dest="cmd", required=True)

    c3 = subs.add_parser("cosine3")
    c3.add_argument("a1", type=float)
    c3.add_argument("a2", type=float)
    c3.add_argument("a3", type=float)
    c3.add_argument("b1", type=float)
    c3.add_argument("b2", type=float)
    c3.add_argument("b3", type=float)

    c2 = subs.add_parser("cosine2")
    c2.add_argument("a1", type=float)
    c2.add_argument("a2", type=float)
    c2.add_argument("b1", type=float)
    c2.add_argument("b2", type=float)

    c4 = subs.add_parser("cosine4")
    c4.add_argument("a1", type=float)
    c4.add_argument("a2", type=float)
    c4.add_argument("a3", type=float)
    c4.add_argument("a4", type=float)
    c4.add_argument("b1", type=float)
    c4.add_argument("b2", type=float)
    c4.add_argument("b3", type=float)
    c4.add_argument("b4", type=float)

    args = parser.parse_args()
    if args.cmd == "cosine3":
        a = np.array([args.a1, args.a2, args.a3])
        b = np.array([args.b1, args.b2, args.b3])
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        result = dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0
        print(round(result, 3))
    elif args.cmd == "cosine2":
        a = np.array([args.a1, args.a2])
        b = np.array([args.b1, args.b2])
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        result = dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0
        print(round(result, 3))
    elif args.cmd == "cosine4":
        a = np.array([args.a1, args.a2, args.a3, args.a4])
        b = np.array([args.b1, args.b2, args.b3, args.b4])
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        result = dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0
        print(round(result, 3))


if __name__ == "__main__":
    main()
