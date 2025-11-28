#!/usr/bin/env python3
"""Math Special Functions CLI.

Special mathematical functions from math module.
"""

import argparse
import math
import sys


def hypot(*args: float) -> float:
    """Euclidean norm (distance from origin)."""
    return math.hypot(*args)


def dist(p: list[float], q: list[float]) -> float:
    """Euclidean distance between two points."""
    return math.dist(p, q)


def degrees(x: float) -> float:
    """Convert radians to degrees."""
    return math.degrees(x)


def radians(x: float) -> float:
    """Convert degrees to radians."""
    return math.radians(x)


def prod(iterable: list[float], start: float = 1.0) -> float:
    """Product of all elements."""
    return math.prod(iterable, start=start)


def fsum(iterable: list[float]) -> float:
    """Accurate floating point sum."""
    return math.fsum(iterable)


def sumprod(p: list[float], q: list[float]) -> float:
    """Sum of products of two sequences."""
    # Python 3.12+ has math.sumprod, fallback for earlier versions
    return sum(a * b for a, b in zip(p, q, strict=False))


def nextafter(x: float, y: float) -> float:
    """Next float after x toward y."""
    return math.nextafter(x, y)


def ulp(x: float) -> float:
    """Unit in the last place."""
    return math.ulp(x)


def comb(n: int, k: int) -> int:
    """Number of combinations (n choose k)."""
    return math.comb(n, k)


def perm(n: int, k: int | None = None) -> int:
    """Number of permutations."""
    if k is None:
        return math.perm(n)
    return math.perm(n, k)


def erf(x: float) -> float:
    """Error function."""
    return math.erf(x)


def erfc(x: float) -> float:
    """Complementary error function."""
    return math.erfc(x)


def gamma_fn(x: float) -> float:
    """Gamma function."""
    return math.gamma(x)


def lgamma(x: float) -> float:
    """Natural log of gamma function."""
    return math.lgamma(x)


def expm1(x: float) -> float:
    """exp(x) - 1, accurate for small x."""
    return math.expm1(x)


def log1p(x: float) -> float:
    """log(1 + x), accurate for small x."""
    return math.log1p(x)


def asinh(x: float) -> float:
    """Inverse hyperbolic sine."""
    return math.asinh(x)


def acosh(x: float) -> float:
    """Inverse hyperbolic cosine."""
    return math.acosh(x)


def atanh(x: float) -> float:
    """Inverse hyperbolic tangent."""
    return math.atanh(x)


def cbrt(x: float) -> float:
    """Cube root."""
    # Python 3.12+ has math.cbrt, fallback for earlier versions
    if x >= 0:
        return x ** (1 / 3)
    return -((-x) ** (1 / 3))


def exp2(x: float) -> float:
    """2 raised to power x."""
    # Python 3.12+ has math.exp2, fallback for earlier versions
    return 2.0**x


def binomial_coefficient(n: int, k: int) -> int:
    """Calculate binomial coefficient using comb."""
    return comb(n, k)


def triangle_area(a: float, b: float, c: float) -> float:
    """Calculate triangle area using Heron's formula."""
    s = (a + b + c) / 2
    return math.sqrt(s * (s - a) * (s - b) * (s - c))


def distance_3d(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    """3D Euclidean distance."""
    return dist([x1, y1, z1], [x2, y2, z2])


def vector_length(*components: float) -> float:
    """Length of n-dimensional vector."""
    return hypot(*components)


def normal_cdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    """Cumulative distribution function of normal distribution."""
    return 0.5 * (1 + erf((x - mu) / (sigma * math.sqrt(2))))


def normal_pdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    """Probability density function of normal distribution."""
    return (1 / (sigma * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x - mu) / sigma) ** 2)


def sigmoid(x: float) -> float:
    """Sigmoid function."""
    return 1 / (1 + math.exp(-x))


def softplus(x: float) -> float:
    """Softplus function (smooth ReLU)."""
    return math.log1p(math.exp(x))


def main() -> int:
    parser = argparse.ArgumentParser(description="Special math functions CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # hypot
    hypot_p = subparsers.add_parser("hypot", help="Euclidean norm")
    hypot_p.add_argument("values", type=float, nargs="+")

    # dist
    dist_p = subparsers.add_parser("dist", help="Distance between points")
    dist_p.add_argument("--p1", type=float, nargs="+", required=True)
    dist_p.add_argument("--p2", type=float, nargs="+", required=True)

    # degrees
    deg_p = subparsers.add_parser("degrees", help="Radians to degrees")
    deg_p.add_argument("radians", type=float)

    # radians
    rad_p = subparsers.add_parser("radians", help="Degrees to radians")
    rad_p.add_argument("degrees", type=float)

    # prod
    prod_p = subparsers.add_parser("prod", help="Product of values")
    prod_p.add_argument("values", type=float, nargs="+")

    # comb
    comb_p = subparsers.add_parser("comb", help="Combinations")
    comb_p.add_argument("n", type=int)
    comb_p.add_argument("k", type=int)

    # perm
    perm_p = subparsers.add_parser("perm", help="Permutations")
    perm_p.add_argument("n", type=int)
    perm_p.add_argument("k", type=int, nargs="?")

    # triangle
    tri_p = subparsers.add_parser("triangle", help="Triangle area")
    tri_p.add_argument("a", type=float)
    tri_p.add_argument("b", type=float)
    tri_p.add_argument("c", type=float)

    # sigmoid
    sig_p = subparsers.add_parser("sigmoid", help="Sigmoid function")
    sig_p.add_argument("x", type=float)

    # normal
    norm_p = subparsers.add_parser("normal", help="Normal distribution")
    norm_p.add_argument("x", type=float)
    norm_p.add_argument("--mu", type=float, default=0.0)
    norm_p.add_argument("--sigma", type=float, default=1.0)
    norm_p.add_argument("--cdf", action="store_true")

    args = parser.parse_args()

    if args.command == "hypot":
        print(hypot(*args.values))
    elif args.command == "dist":
        print(dist(args.p1, args.p2))
    elif args.command == "degrees":
        print(degrees(args.radians))
    elif args.command == "radians":
        print(radians(args.degrees))
    elif args.command == "prod":
        print(prod(args.values))
    elif args.command == "comb":
        print(comb(args.n, args.k))
    elif args.command == "perm":
        print(perm(args.n, args.k))
    elif args.command == "triangle":
        print(triangle_area(args.a, args.b, args.c))
    elif args.command == "sigmoid":
        print(sigmoid(args.x))
    elif args.command == "normal":
        if args.cdf:
            print(normal_cdf(args.x, args.mu, args.sigma))
        else:
            print(normal_pdf(args.x, args.mu, args.sigma))
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
