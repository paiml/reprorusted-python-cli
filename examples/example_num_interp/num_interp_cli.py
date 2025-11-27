"""Interpolation CLI.

Demonstrates interpolation methods: linear, cubic, spline.
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass


def linear_interp(x: float, x0: float, y0: float, x1: float, y1: float) -> float:
    """Linear interpolation between two points."""
    if x1 == x0:
        return y0
    t = (x - x0) / (x1 - x0)
    return y0 + t * (y1 - y0)


def piecewise_linear(xs: list[float], ys: list[float], x: float) -> float:
    """Piecewise linear interpolation."""
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("Need at least 2 points")

    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]

    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            return linear_interp(x, xs[i], ys[i], xs[i + 1], ys[i + 1])

    return ys[-1]


def lagrange(xs: list[float], ys: list[float], x: float) -> float:
    """Lagrange polynomial interpolation."""
    n = len(xs)
    result = 0.0

    for i in range(n):
        term = ys[i]
        for j in range(n):
            if i != j:
                term *= (x - xs[j]) / (xs[i] - xs[j])
        result += term

    return result


def newton_divided_diff(xs: list[float], ys: list[float]) -> list[float]:
    """Calculate Newton divided differences."""
    n = len(xs)
    coefs = ys[:]

    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coefs[i] = (coefs[i] - coefs[i - 1]) / (xs[i] - xs[i - j])

    return coefs


def newton_interp(xs: list[float], coefs: list[float], x: float) -> float:
    """Newton polynomial interpolation."""
    n = len(coefs)
    result = coefs[-1]

    for i in range(n - 2, -1, -1):
        result = result * (x - xs[i]) + coefs[i]

    return result


@dataclass
class CubicSpline:
    """Cubic spline interpolation."""

    xs: list[float]
    ys: list[float]
    a: list[float]  # Coefficients
    b: list[float]
    c: list[float]
    d: list[float]

    @classmethod
    def natural(cls, xs: list[float], ys: list[float]) -> "CubicSpline":
        """Create natural cubic spline (second derivatives = 0 at endpoints)."""
        n = len(xs)
        if n < 2:
            raise ValueError("Need at least 2 points")

        # Calculate h (intervals)
        h = [xs[i + 1] - xs[i] for i in range(n - 1)]

        # Set up tridiagonal system for second derivatives
        alpha = [0.0] * n
        for i in range(1, n - 1):
            alpha[i] = (3 / h[i]) * (ys[i + 1] - ys[i]) - (3 / h[i - 1]) * (ys[i] - ys[i - 1])

        # Solve tridiagonal system
        diag = [1.0] + [0.0] * (n - 1)
        mu = [0.0] * n
        z = [0.0] * n

        for i in range(1, n - 1):
            diag[i] = 2 * (xs[i + 1] - xs[i - 1]) - h[i - 1] * mu[i - 1]
            mu[i] = h[i] / diag[i]
            z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / diag[i]

        diag[n - 1] = 1.0

        # Back substitution
        c = [0.0] * n
        b = [0.0] * (n - 1)
        d = [0.0] * (n - 1)
        a = ys[:-1]

        for j in range(n - 2, -1, -1):
            c[j] = z[j] - mu[j] * c[j + 1]
            b[j] = (ys[j + 1] - ys[j]) / h[j] - h[j] * (c[j + 1] + 2 * c[j]) / 3
            d[j] = (c[j + 1] - c[j]) / (3 * h[j])

        return cls(xs, ys, a, b, c[:-1], d)

    def __call__(self, x: float) -> float:
        """Evaluate spline at x."""
        if x <= self.xs[0]:
            return self.ys[0]
        if x >= self.xs[-1]:
            return self.ys[-1]

        # Find interval
        i = 0
        for j in range(len(self.xs) - 1):
            if self.xs[j] <= x <= self.xs[j + 1]:
                i = j
                break

        dx = x - self.xs[i]
        return self.a[i] + self.b[i] * dx + self.c[i] * dx**2 + self.d[i] * dx**3


def hermite_interp(
    x0: float, y0: float, dy0: float, x1: float, y1: float, dy1: float, x: float
) -> float:
    """Hermite interpolation with derivatives."""
    t = (x - x0) / (x1 - x0)
    h = x1 - x0

    h00 = 2 * t**3 - 3 * t**2 + 1
    h10 = t**3 - 2 * t**2 + t
    h01 = -2 * t**3 + 3 * t**2
    h11 = t**3 - t**2

    return h00 * y0 + h10 * h * dy0 + h01 * y1 + h11 * h * dy1


class Interpolator:
    """Factory for creating interpolators."""

    @staticmethod
    def linear(xs: list[float], ys: list[float]) -> Callable[[float], float]:
        return lambda x: piecewise_linear(xs, ys, x)

    @staticmethod
    def polynomial(xs: list[float], ys: list[float]) -> Callable[[float], float]:
        return lambda x: lagrange(xs, ys, x)

    @staticmethod
    def cubic_spline(xs: list[float], ys: list[float]) -> Callable[[float], float]:
        spline = CubicSpline.natural(xs, ys)
        return spline


def simulate_interp(operations: list[str]) -> list[str]:
    """Simulate interpolation operations."""
    results: list[str] = []

    xs = [0.0, 1.0, 2.0, 3.0]
    ys = [0.0, 1.0, 4.0, 9.0]  # y = x^2

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "linear":
            x = float(parts[1])
            result = piecewise_linear(xs, ys, x)
            results.append(f"{result:.2f}")
        elif cmd == "lagrange":
            x = float(parts[1])
            result = lagrange(xs, ys, x)
            results.append(f"{result:.2f}")
        elif cmd == "spline":
            x = float(parts[1])
            spline = CubicSpline.natural(xs, ys)
            result = spline(x)
            results.append(f"{result:.2f}")
        elif cmd == "newton":
            x = float(parts[1])
            coefs = newton_divided_diff(xs, ys)
            result = newton_interp(xs, coefs, x)
            results.append(f"{result:.2f}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: num_interp_cli.py <command>")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":
        xs = [0.0, 1.0, 2.0, 3.0, 4.0]
        ys = [0.0, 1.0, 4.0, 9.0, 16.0]  # y = x^2

        spline = CubicSpline.natural(xs, ys)

        print("Interpolating y = x^2:")
        for x in [0.5, 1.5, 2.5, 3.5]:
            lin = piecewise_linear(xs, ys, x)
            lag = lagrange(xs, ys, x)
            spl = spline(x)
            exact = x**2
            print(
                f"x={x}: linear={lin:.3f}, lagrange={lag:.3f}, spline={spl:.3f}, exact={exact:.3f}"
            )
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
