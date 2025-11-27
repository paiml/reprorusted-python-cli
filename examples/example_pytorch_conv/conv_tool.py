#!/usr/bin/env python3
"""Conv2d CLI tool - 2D convolution (PyTorch-compatible)."""

import argparse
import json
import sys


def conv2d(x: list, kernel: list, bias: list, stride: int = 1, padding: int = 0) -> list:
    """2D convolution forward pass."""
    in_ch, h, w = len(x), len(x[0]), len(x[0][0])
    out_ch, _, kh, kw = len(kernel), len(kernel[0]), len(kernel[0][0]), len(kernel[0][0][0])

    out_h = (h + 2 * padding - kh) // stride + 1
    out_w = (w + 2 * padding - kw) // stride + 1

    output = [[[0.0 for _ in range(out_w)] for _ in range(out_h)] for _ in range(out_ch)]

    for oc in range(out_ch):
        for oh in range(out_h):
            for ow in range(out_w):
                val = bias[oc] if bias else 0
                for ic in range(in_ch):
                    for kh_i in range(kh):
                        for kw_i in range(kw):
                            ih = oh * stride + kh_i - padding
                            iw = ow * stride + kw_i - padding
                            if 0 <= ih < h and 0 <= iw < w:
                                val += x[ic][ih][iw] * kernel[oc][ic][kh_i][kw_i]
                output[oc][oh][ow] = val

    return output


def cmd_forward(args: argparse.Namespace) -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        output = conv2d(data["x"], data["kernel"], data.get("bias", [0]))
        print(json.dumps({"output": output}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Conv2d CLI - 2D convolution (PyTorch-compatible)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("forward", help="Forward pass").set_defaults(func=cmd_forward)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
