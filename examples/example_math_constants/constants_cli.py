#!/usr/bin/env python3
"""Math Constants CLI.

Mathematical constants and special value handling.
"""

import argparse
import math
import sys

# Constants
PI: float = math.pi
E: float = math.e
TAU: float = math.tau
INF: float = math.inf
NEG_INF: float = -math.inf
NAN: float = math.nan


def get_pi() -> float:
    """Get pi constant."""
    return PI


def get_e() -> float:
    """Get Euler's number."""
    return E


def get_tau() -> float:
    """Get tau (2*pi)."""
    return TAU


def get_inf() -> float:
    """Get positive infinity."""
    return INF


def get_neg_inf() -> float:
    """Get negative infinity."""
    return NEG_INF


def get_nan() -> float:
    """Get NaN."""
    return NAN


def circle_circumference(radius: float) -> float:
    """Calculate circle circumference."""
    return 2 * PI * radius


def circle_area(radius: float) -> float:
    """Calculate circle area."""
    return PI * radius * radius


def sphere_volume(radius: float) -> float:
    """Calculate sphere volume."""
    return (4 / 3) * PI * radius**3


def sphere_surface_area(radius: float) -> float:
    """Calculate sphere surface area."""
    return 4 * PI * radius**2


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * PI / 180


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180 / PI


def is_finite_value(x: float) -> bool:
    """Check if value is finite (not inf or nan)."""
    return math.isfinite(x)


def is_infinite(x: float) -> bool:
    """Check if value is infinite."""
    return math.isinf(x)


def is_nan_value(x: float) -> bool:
    """Check if value is NaN."""
    return math.isnan(x)


def is_positive_inf(x: float) -> bool:
    """Check if positive infinity."""
    return math.isinf(x) and x > 0


def is_negative_inf(x: float) -> bool:
    """Check if negative infinity."""
    return math.isinf(x) and x < 0


def safe_divide(a: float, b: float) -> float:
    """Safe division handling division by zero."""
    if b == 0:
        if a > 0:
            return INF
        if a < 0:
            return NEG_INF
        return NAN
    return a / b


def safe_log(x: float) -> float:
    """Safe logarithm handling non-positive values."""
    if x <= 0:
        return NEG_INF
    return math.log(x)


def safe_sqrt(x: float) -> float:
    """Safe square root handling negative values."""
    if x < 0:
        return NAN
    return math.sqrt(x)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to range [min_val, max_val]."""
    if math.isnan(value):
        return NAN
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * t


def inverse_lerp(a: float, b: float, value: float) -> float:
    """Inverse linear interpolation."""
    if a == b:
        return 0.0
    return (value - a) / (b - a)


def normalize_angle(angle: float) -> float:
    """Normalize angle to [0, 2*pi)."""
    while angle < 0:
        angle += TAU
    while angle >= TAU:
        angle -= TAU
    return angle


def golden_ratio() -> float:
    """Return golden ratio phi."""
    return (1 + math.sqrt(5)) / 2


def euler_mascheroni() -> float:
    """Approximate Euler-Mascheroni constant."""
    # Approximation using harmonic series
    n = 1000000
    h = sum(1 / i for i in range(1, n + 1))
    return h - math.log(n)


def main() -> int:
    parser = argparse.ArgumentParser(description="Math constants CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # constants
    subparsers.add_parser("pi", help="Show pi")
    subparsers.add_parser("e", help="Show e")
    subparsers.add_parser("tau", help="Show tau")
    subparsers.add_parser("inf", help="Show infinity")
    subparsers.add_parser("golden", help="Show golden ratio")

    # circle
    circle_p = subparsers.add_parser("circle", help="Circle calculations")
    circle_p.add_argument("radius", type=float)
    circle_p.add_argument("--area", action="store_true")
    circle_p.add_argument("--circumference", action="store_true")

    # sphere
    sphere_p = subparsers.add_parser("sphere", help="Sphere calculations")
    sphere_p.add_argument("radius", type=float)
    sphere_p.add_argument("--volume", action="store_true")
    sphere_p.add_argument("--surface", action="store_true")

    # convert
    conv_p = subparsers.add_parser("convert", help="Angle conversion")
    conv_p.add_argument("value", type=float)
    conv_p.add_argument("--to-radians", action="store_true")
    conv_p.add_argument("--to-degrees", action="store_true")

    # check
    check_p = subparsers.add_parser("check", help="Check special values")
    check_p.add_argument("value", type=float)

    args = parser.parse_args()

    if args.command == "pi":
        print(f"π = {PI}")
    elif args.command == "e":
        print(f"e = {E}")
    elif args.command == "tau":
        print(f"τ = {TAU}")
    elif args.command == "inf":
        print(f"∞ = {INF}")
    elif args.command == "golden":
        print(f"φ = {golden_ratio()}")
    elif args.command == "circle":
        if args.area:
            print(f"Area: {circle_area(args.radius)}")
        if args.circumference:
            print(f"Circumference: {circle_circumference(args.radius)}")
        if not args.area and not args.circumference:
            print(f"Area: {circle_area(args.radius)}")
            print(f"Circumference: {circle_circumference(args.radius)}")
    elif args.command == "sphere":
        if args.volume:
            print(f"Volume: {sphere_volume(args.radius)}")
        if args.surface:
            print(f"Surface area: {sphere_surface_area(args.radius)}")
        if not args.volume and not args.surface:
            print(f"Volume: {sphere_volume(args.radius)}")
            print(f"Surface area: {sphere_surface_area(args.radius)}")
    elif args.command == "convert":
        if args.to_radians:
            print(f"{args.value}° = {degrees_to_radians(args.value)} rad")
        elif args.to_degrees:
            print(f"{args.value} rad = {radians_to_degrees(args.value)}°")
        else:
            print(f"{args.value}° = {degrees_to_radians(args.value)} rad")
    elif args.command == "check":
        print(f"Value: {args.value}")
        print(f"  is_finite: {is_finite_value(args.value)}")
        print(f"  is_infinite: {is_infinite(args.value)}")
        print(f"  is_nan: {is_nan_value(args.value)}")
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
