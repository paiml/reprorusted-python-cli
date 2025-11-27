#!/usr/bin/env python3
"""Colorsys Example - Color conversion CLI."""

import argparse
import colorsys


def cmd_rgb2hsv(args):
    """RGB to HSV. Depyler: proven to terminate"""
    r, g, b = args.r / 255, args.g / 255, args.b / 255
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    print(f"HSV: {h:.3f}, {s:.3f}, {v:.3f}")


def cmd_hsv2rgb(args):
    """HSV to RGB. Depyler: proven to terminate"""
    r, g, b = colorsys.hsv_to_rgb(args.h, args.s, args.v)
    print(f"RGB: {int(r * 255)}, {int(g * 255)}, {int(b * 255)}")


def cmd_rgb2hls(args):
    """RGB to HLS. Depyler: proven to terminate"""
    r, g, b = args.r / 255, args.g / 255, args.b / 255
    h, light, s = colorsys.rgb_to_hls(r, g, b)
    print(f"HLS: {h:.3f}, {light:.3f}, {s:.3f}")


def cmd_hex(args):
    """RGB to Hex. Depyler: proven to terminate"""
    print(f"#{args.r:02x}{args.g:02x}{args.b:02x}")


def main():
    parser = argparse.ArgumentParser(description="Color conversion tool")
    subs = parser.add_subparsers(dest="command", required=True)
    r2h = subs.add_parser("rgb2hsv")
    r2h.add_argument("r", type=int)
    r2h.add_argument("g", type=int)
    r2h.add_argument("b", type=int)
    h2r = subs.add_parser("hsv2rgb")
    h2r.add_argument("h", type=float)
    h2r.add_argument("s", type=float)
    h2r.add_argument("v", type=float)
    r2l = subs.add_parser("rgb2hls")
    r2l.add_argument("r", type=int)
    r2l.add_argument("g", type=int)
    r2l.add_argument("b", type=int)
    hx = subs.add_parser("hex")
    hx.add_argument("r", type=int)
    hx.add_argument("g", type=int)
    hx.add_argument("b", type=int)
    args = parser.parse_args()
    {"rgb2hsv": cmd_rgb2hsv, "hsv2rgb": cmd_hsv2rgb, "rgb2hls": cmd_rgb2hls, "hex": cmd_hex}[
        args.command
    ](args)


if __name__ == "__main__":
    main()
