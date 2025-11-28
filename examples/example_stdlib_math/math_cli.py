#!/usr/bin/env python3
"""Standard Library Math CLI.

Mathematical functions using Python's math module.
"""

import argparse
import math
import sys


def sqrt(x: float) -> float:
    """Square root."""
    return math.sqrt(x)


def power(base: float, exp: float) -> float:
    """Power function."""
    return math.pow(base, exp)


def log_natural(x: float) -> float:
    """Natural logarithm."""
    return math.log(x)


def log_base(x: float, base: float) -> float:
    """Logarithm with custom base."""
    return math.log(x, base)


def log10(x: float) -> float:
    """Base 10 logarithm."""
    return math.log10(x)


def log2(x: float) -> float:
    """Base 2 logarithm."""
    return math.log2(x)


def exp(x: float) -> float:
    """Exponential function e^x."""
    return math.exp(x)


def sin(x: float) -> float:
    """Sine function."""
    return math.sin(x)


def cos(x: float) -> float:
    """Cosine function."""
    return math.cos(x)


def tan(x: float) -> float:
    """Tangent function."""
    return math.tan(x)


def asin(x: float) -> float:
    """Arc sine."""
    return math.asin(x)


def acos(x: float) -> float:
    """Arc cosine."""
    return math.acos(x)


def atan(x: float) -> float:
    """Arc tangent."""
    return math.atan(x)


def atan2(y: float, x: float) -> float:
    """Arc tangent of y/x."""
    return math.atan2(y, x)


def sinh(x: float) -> float:
    """Hyperbolic sine."""
    return math.sinh(x)


def cosh(x: float) -> float:
    """Hyperbolic cosine."""
    return math.cosh(x)


def tanh(x: float) -> float:
    """Hyperbolic tangent."""
    return math.tanh(x)


def floor(x: float) -> int:
    """Floor function."""
    return math.floor(x)


def ceil(x: float) -> int:
    """Ceiling function."""
    return math.ceil(x)


def trunc(x: float) -> int:
    """Truncate to integer."""
    return math.trunc(x)


def fabs(x: float) -> float:
    """Absolute value (float)."""
    return math.fabs(x)


def factorial(n: int) -> int:
    """Factorial."""
    return math.factorial(n)


def gcd(a: int, b: int) -> int:
    """Greatest common divisor."""
    return math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    """Least common multiple."""
    return math.lcm(a, b)


def isqrt(n: int) -> int:
    """Integer square root."""
    return math.isqrt(n)


def is_close(a: float, b: float, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> bool:
    """Check if two floats are close."""
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def is_finite(x: float) -> bool:
    """Check if finite."""
    return math.isfinite(x)


def is_inf(x: float) -> bool:
    """Check if infinite."""
    return math.isinf(x)


def is_nan(x: float) -> bool:
    """Check if NaN."""
    return math.isnan(x)


def fmod(x: float, y: float) -> float:
    """Floating point modulo."""
    return math.fmod(x, y)


def remainder(x: float, y: float) -> float:
    """IEEE 754 remainder."""
    return math.remainder(x, y)


def modf(x: float) -> tuple[float, float]:
    """Return fractional and integer parts."""
    return math.modf(x)


def frexp(x: float) -> tuple[float, int]:
    """Return mantissa and exponent."""
    return math.frexp(x)


def ldexp(x: float, i: int) -> float:
    """Return x * 2^i."""
    return math.ldexp(x, i)


def copysign(x: float, y: float) -> float:
    """Copy sign of y to x."""
    return math.copysign(x, y)


def solve_quadratic(a: float, b: float, c: float) -> list[float]:
    """Solve quadratic equation ax^2 + bx + c = 0."""
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return []
    if discriminant == 0:
        return [-b / (2 * a)]
    sqrt_d = math.sqrt(discriminant)
    return [(-b + sqrt_d) / (2 * a), (-b - sqrt_d) / (2 * a)]


def distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """Euclidean distance in 2D."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distance_3d(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    """Euclidean distance in 3D."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Math functions CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # sqrt
    sqrt_p = subparsers.add_parser("sqrt", help="Square root")
    sqrt_p.add_argument("x", type=float)

    # pow
    pow_p = subparsers.add_parser("pow", help="Power")
    pow_p.add_argument("base", type=float)
    pow_p.add_argument("exp", type=float)

    # trig
    sin_p = subparsers.add_parser("sin", help="Sine")
    sin_p.add_argument("x", type=float)

    cos_p = subparsers.add_parser("cos", help="Cosine")
    cos_p.add_argument("x", type=float)

    tan_p = subparsers.add_parser("tan", help="Tangent")
    tan_p.add_argument("x", type=float)

    # log
    log_p = subparsers.add_parser("log", help="Natural log")
    log_p.add_argument("x", type=float)

    # exp
    exp_p = subparsers.add_parser("exp", help="Exponential")
    exp_p.add_argument("x", type=float)

    # factorial
    fact_p = subparsers.add_parser("factorial", help="Factorial")
    fact_p.add_argument("n", type=int)

    # gcd
    gcd_p = subparsers.add_parser("gcd", help="GCD")
    gcd_p.add_argument("a", type=int)
    gcd_p.add_argument("b", type=int)

    # quadratic
    quad_p = subparsers.add_parser("quadratic", help="Solve quadratic")
    quad_p.add_argument("a", type=float)
    quad_p.add_argument("b", type=float)
    quad_p.add_argument("c", type=float)

    # distance
    dist_p = subparsers.add_parser("distance", help="2D distance")
    dist_p.add_argument("x1", type=float)
    dist_p.add_argument("y1", type=float)
    dist_p.add_argument("x2", type=float)
    dist_p.add_argument("y2", type=float)

    args = parser.parse_args()

    if args.command == "sqrt":
        print(sqrt(args.x))
    elif args.command == "pow":
        print(power(args.base, args.exp))
    elif args.command == "sin":
        print(sin(args.x))
    elif args.command == "cos":
        print(cos(args.x))
    elif args.command == "tan":
        print(tan(args.x))
    elif args.command == "log":
        print(log_natural(args.x))
    elif args.command == "exp":
        print(exp(args.x))
    elif args.command == "factorial":
        print(factorial(args.n))
    elif args.command == "gcd":
        print(gcd(args.a, args.b))
    elif args.command == "quadratic":
        roots = solve_quadratic(args.a, args.b, args.c)
        if roots:
            print(f"Roots: {roots}")
        else:
            print("No real roots")
    elif args.command == "distance":
        print(distance_2d(args.x1, args.y1, args.x2, args.y2))
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
