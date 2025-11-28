#!/usr/bin/env python3
"""Polynomial Operations CLI.

Pure Python polynomial operations without external dependencies.
"""

import argparse
import sys
from dataclasses import dataclass


@dataclass
class Polynomial:
    """Polynomial representation using coefficients."""

    coeffs: list[float]  # coeffs[i] is coefficient of x^i

    def __post_init__(self):
        # Remove trailing zeros
        while len(self.coeffs) > 1 and self.coeffs[-1] == 0:
            self.coeffs.pop()

    @property
    def degree(self) -> int:
        """Get polynomial degree."""
        return len(self.coeffs) - 1

    def __str__(self) -> str:
        """Format polynomial as string."""
        if not self.coeffs or all(c == 0 for c in self.coeffs):
            return "0"

        terms = []
        for i, c in enumerate(self.coeffs):
            if c == 0:
                continue

            if i == 0:
                terms.append(f"{c}")
            elif i == 1:
                if c == 1:
                    terms.append("x")
                elif c == -1:
                    terms.append("-x")
                else:
                    terms.append(f"{c}x")
            else:
                if c == 1:
                    terms.append(f"x^{i}")
                elif c == -1:
                    terms.append(f"-x^{i}")
                else:
                    terms.append(f"{c}x^{i}")

        if not terms:
            return "0"

        result = terms[-1]
        for term in reversed(terms[:-1]):
            if term.startswith("-"):
                result += f" - {term[1:]}"
            else:
                result += f" + {term}"

        return result


def add(p1: Polynomial, p2: Polynomial) -> Polynomial:
    """Add two polynomials."""
    max_len = max(len(p1.coeffs), len(p2.coeffs))
    result = [0.0] * max_len

    for i, c in enumerate(p1.coeffs):
        result[i] += c
    for i, c in enumerate(p2.coeffs):
        result[i] += c

    return Polynomial(result)


def subtract(p1: Polynomial, p2: Polynomial) -> Polynomial:
    """Subtract p2 from p1."""
    max_len = max(len(p1.coeffs), len(p2.coeffs))
    result = [0.0] * max_len

    for i, c in enumerate(p1.coeffs):
        result[i] += c
    for i, c in enumerate(p2.coeffs):
        result[i] -= c

    return Polynomial(result)


def multiply(p1: Polynomial, p2: Polynomial) -> Polynomial:
    """Multiply two polynomials."""
    if not p1.coeffs or not p2.coeffs:
        return Polynomial([0])

    result = [0.0] * (len(p1.coeffs) + len(p2.coeffs) - 1)

    for i, c1 in enumerate(p1.coeffs):
        for j, c2 in enumerate(p2.coeffs):
            result[i + j] += c1 * c2

    return Polynomial(result)


def scalar_multiply(p: Polynomial, scalar: float) -> Polynomial:
    """Multiply polynomial by scalar."""
    return Polynomial([c * scalar for c in p.coeffs])


def evaluate(p: Polynomial, x: float) -> float:
    """Evaluate polynomial at x using Horner's method."""
    if not p.coeffs:
        return 0.0

    result = p.coeffs[-1]
    for i in range(len(p.coeffs) - 2, -1, -1):
        result = result * x + p.coeffs[i]

    return result


def derivative(p: Polynomial) -> Polynomial:
    """Calculate derivative of polynomial."""
    if len(p.coeffs) <= 1:
        return Polynomial([0])

    result = [i * p.coeffs[i] for i in range(1, len(p.coeffs))]
    return Polynomial(result)


def integrate(p: Polynomial, constant: float = 0) -> Polynomial:
    """Calculate indefinite integral of polynomial."""
    result = [constant]
    for i, c in enumerate(p.coeffs):
        result.append(c / (i + 1))
    return Polynomial(result)


def definite_integral(p: Polynomial, a: float, b: float) -> float:
    """Calculate definite integral from a to b."""
    integral = integrate(p)
    return evaluate(integral, b) - evaluate(integral, a)


def power(p: Polynomial, n: int) -> Polynomial:
    """Raise polynomial to power n."""
    if n < 0:
        raise ValueError("Negative powers not supported")
    if n == 0:
        return Polynomial([1])

    result = Polynomial(p.coeffs[:])
    for _ in range(n - 1):
        result = multiply(result, p)

    return result


def divide(dividend: Polynomial, divisor: Polynomial) -> tuple[Polynomial, Polynomial]:
    """Polynomial long division. Returns (quotient, remainder)."""
    if all(c == 0 for c in divisor.coeffs):
        raise ValueError("Division by zero polynomial")

    if dividend.degree < divisor.degree:
        return Polynomial([0]), dividend

    quotient = [0.0] * (dividend.degree - divisor.degree + 1)
    remainder = dividend.coeffs[:]

    divisor_lead = divisor.coeffs[-1]

    for i in range(len(quotient) - 1, -1, -1):
        if len(remainder) > divisor.degree + i:
            coeff = remainder[divisor.degree + i] / divisor_lead
            quotient[i] = coeff

            for j, c in enumerate(divisor.coeffs):
                remainder[i + j] -= coeff * c

    return Polynomial(quotient), Polynomial(remainder)


def gcd(p1: Polynomial, p2: Polynomial) -> Polynomial:
    """Calculate GCD of two polynomials using Euclidean algorithm."""
    while any(c != 0 for c in p2.coeffs):
        _, remainder = divide(p1, p2)
        p1 = p2
        p2 = remainder

    # Normalize leading coefficient to 1
    if p1.coeffs and p1.coeffs[-1] != 0:
        lead = p1.coeffs[-1]
        return Polynomial([c / lead for c in p1.coeffs])

    return p1


def compose(outer: Polynomial, inner: Polynomial) -> Polynomial:
    """Compose polynomials: outer(inner(x))."""
    result = Polynomial([0])

    for i, c in enumerate(outer.coeffs):
        term = scalar_multiply(power(inner, i), c)
        result = add(result, term)

    return result


def find_roots_quadratic(p: Polynomial) -> list[complex]:
    """Find roots of quadratic polynomial."""
    if p.degree != 2:
        raise ValueError("Polynomial must be quadratic")

    c, b, a = p.coeffs[0], p.coeffs[1], p.coeffs[2]

    discriminant = b * b - 4 * a * c

    if discriminant >= 0:
        sqrt_d = discriminant**0.5
        return [(-b + sqrt_d) / (2 * a), (-b - sqrt_d) / (2 * a)]
    else:
        sqrt_d = (-discriminant) ** 0.5
        return [
            complex(-b / (2 * a), sqrt_d / (2 * a)),
            complex(-b / (2 * a), -sqrt_d / (2 * a)),
        ]


def find_root_newton(p: Polynomial, x0: float, tol: float = 1e-10, max_iter: int = 100) -> float:
    """Find a root using Newton's method."""
    dp = derivative(p)
    x = x0

    for _ in range(max_iter):
        fx = evaluate(p, x)
        if abs(fx) < tol:
            return x

        dfx = evaluate(dp, x)
        if abs(dfx) < 1e-15:
            raise ValueError("Derivative too small")

        x = x - fx / dfx

    raise ValueError("Did not converge")


def interpolate_lagrange(points: list[tuple[float, float]]) -> Polynomial:
    """Lagrange polynomial interpolation."""
    n = len(points)
    result = Polynomial([0])

    for i in range(n):
        xi, yi = points[i]

        # Build basis polynomial L_i
        basis = Polynomial([1])
        for j in range(n):
            if i != j:
                xj = points[j][0]
                factor = Polynomial([-xj / (xi - xj), 1 / (xi - xj)])
                basis = multiply(basis, factor)

        result = add(result, scalar_multiply(basis, yi))

    return result


def from_roots(roots: list[float]) -> Polynomial:
    """Create polynomial from its roots."""
    result = Polynomial([1])

    for r in roots:
        factor = Polynomial([-r, 1])  # (x - r)
        result = multiply(result, factor)

    return result


def parse_polynomial(s: str) -> Polynomial:
    """Parse polynomial from string like '1,2,3' -> 1 + 2x + 3x^2."""
    coeffs = [float(c) for c in s.split(",")]
    return Polynomial(coeffs)


def main() -> int:
    parser = argparse.ArgumentParser(description="Polynomial operations")
    parser.add_argument(
        "--mode",
        choices=[
            "eval",
            "add",
            "mult",
            "deriv",
            "integ",
            "roots",
            "divide",
            "interpolate",
            "demo",
        ],
        default="demo",
        help="Operation mode",
    )
    parser.add_argument("--p", help="Polynomial coefficients (comma-separated)")
    parser.add_argument("--q", help="Second polynomial")
    parser.add_argument("--x", type=float, help="Value to evaluate at")
    parser.add_argument("--points", help="Points for interpolation (x1:y1,x2:y2,...)")

    args = parser.parse_args()

    if args.mode == "demo":
        print("Polynomial Operations Demo\n")

        p = Polynomial([1, 2, 3])  # 1 + 2x + 3x^2
        q = Polynomial([2, 1])  # 2 + x

        print(f"P(x) = {p}")
        print(f"Q(x) = {q}")
        print(f"\nP(2) = {evaluate(p, 2)}")
        print(f"P + Q = {add(p, q)}")
        print(f"P * Q = {multiply(p, q)}")
        print(f"P' = {derivative(p)}")
        print(f"∫P dx = {integrate(p)}")

        quadratic = Polynomial([6, -5, 1])  # x^2 - 5x + 6 = (x-2)(x-3)
        print(f"\nRoots of {quadratic}: {find_roots_quadratic(quadratic)}")

    elif args.p:
        p = parse_polynomial(args.p)

        if args.mode == "eval" and args.x is not None:
            result = evaluate(p, args.x)
            print(f"P({args.x}) = {result}")

        elif args.mode == "add" and args.q:
            q = parse_polynomial(args.q)
            result = add(p, q)
            print(f"P + Q = {result}")

        elif args.mode == "mult" and args.q:
            q = parse_polynomial(args.q)
            result = multiply(p, q)
            print(f"P * Q = {result}")

        elif args.mode == "deriv":
            result = derivative(p)
            print(f"P' = {result}")

        elif args.mode == "integ":
            result = integrate(p)
            print(f"∫P dx = {result}")

        elif args.mode == "roots" and p.degree == 2:
            roots = find_roots_quadratic(p)
            print(f"Roots: {roots}")

        elif args.mode == "divide" and args.q:
            q = parse_polynomial(args.q)
            quot, rem = divide(p, q)
            print(f"P / Q = {quot}")
            print(f"Remainder = {rem}")

    elif args.mode == "interpolate" and args.points:
        points = []
        for pt in args.points.split(","):
            x, y = pt.split(":")
            points.append((float(x), float(y)))

        result = interpolate_lagrange(points)
        print(f"Interpolating polynomial: {result}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
