"""Root Finding CLI.

Demonstrates root finding methods: Newton, bisection, secant.
"""

import math
import sys
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class RootResult:
    """Result of root finding."""

    root: float
    iterations: int
    converged: bool
    error: float


def bisection(
    f: Callable[[float], float], a: float, b: float, tol: float = 1e-10, max_iter: int = 100
) -> RootResult:
    """Find root using bisection method."""
    if f(a) * f(b) > 0:
        raise ValueError("f(a) and f(b) must have opposite signs")

    for i in range(max_iter):
        c = (a + b) / 2
        fc = f(c)

        if abs(fc) < tol or (b - a) / 2 < tol:
            return RootResult(c, i + 1, True, abs(fc))

        if fc * f(a) < 0:
            b = c
        else:
            a = c

    return RootResult((a + b) / 2, max_iter, False, abs(f((a + b) / 2)))


def newton(
    f: Callable[[float], float],
    df: Callable[[float], float],
    x0: float,
    tol: float = 1e-10,
    max_iter: int = 100,
) -> RootResult:
    """Find root using Newton-Raphson method."""
    x = x0
    for i in range(max_iter):
        fx = f(x)
        dfx = df(x)

        if abs(dfx) < 1e-14:
            return RootResult(x, i + 1, False, abs(fx))

        x_new = x - fx / dfx
        if abs(x_new - x) < tol:
            return RootResult(x_new, i + 1, True, abs(f(x_new)))
        x = x_new

    return RootResult(x, max_iter, False, abs(f(x)))


def secant(
    f: Callable[[float], float], x0: float, x1: float, tol: float = 1e-10, max_iter: int = 100
) -> RootResult:
    """Find root using secant method."""
    for i in range(max_iter):
        f0, f1 = f(x0), f(x1)

        if abs(f1 - f0) < 1e-14:
            return RootResult(x1, i + 1, False, abs(f1))

        x_new = x1 - f1 * (x1 - x0) / (f1 - f0)

        if abs(x_new - x1) < tol:
            return RootResult(x_new, i + 1, True, abs(f(x_new)))

        x0, x1 = x1, x_new

    return RootResult(x1, max_iter, False, abs(f(x1)))


def regula_falsi(
    f: Callable[[float], float], a: float, b: float, tol: float = 1e-10, max_iter: int = 100
) -> RootResult:
    """Find root using regula falsi (false position) method."""
    if f(a) * f(b) > 0:
        raise ValueError("f(a) and f(b) must have opposite signs")

    for i in range(max_iter):
        fa, fb = f(a), f(b)
        c = (a * fb - b * fa) / (fb - fa)
        fc = f(c)

        if abs(fc) < tol:
            return RootResult(c, i + 1, True, abs(fc))

        if fc * fa < 0:
            b = c
        else:
            a = c

    c = (a * f(b) - b * f(a)) / (f(b) - f(a))
    return RootResult(c, max_iter, False, abs(f(c)))


def brent(
    f: Callable[[float], float], a: float, b: float, tol: float = 1e-10, max_iter: int = 100
) -> RootResult:
    """Find root using Brent's method."""
    if f(a) * f(b) > 0:
        raise ValueError("f(a) and f(b) must have opposite signs")

    if abs(f(a)) < abs(f(b)):
        a, b = b, a

    c = a
    d = a  # Initialize d for Brent's method
    mflag = True

    for i in range(max_iter):
        fa, fb, fc = f(a), f(b), f(c)

        if abs(fb) < tol:
            return RootResult(b, i + 1, True, abs(fb))

        # Try inverse quadratic interpolation
        if fa != fc and fb != fc:
            s = (
                a * fb * fc / ((fa - fb) * (fa - fc))
                + b * fa * fc / ((fb - fa) * (fb - fc))
                + c * fa * fb / ((fc - fa) * (fc - fb))
            )
        else:
            s = b - fb * (b - a) / (fb - fa)

        # Check if s is acceptable
        cond1 = (s < (3 * a + b) / 4 or s > b) if a < b else (s > (3 * a + b) / 4 or s < b)
        cond2 = mflag and abs(s - b) >= abs(b - c) / 2
        cond3 = not mflag and abs(s - b) >= abs(c - d) / 2 if i > 0 else False
        cond4 = mflag and abs(b - c) < tol
        cond5 = not mflag and abs(c - d) < tol if i > 0 else False

        if cond1 or cond2 or cond3 or cond4 or cond5:
            s = (a + b) / 2
            mflag = True
        else:
            mflag = False

        d = c
        c = b

        if f(a) * f(s) < 0:
            b = s
        else:
            a = s

        if abs(f(a)) < abs(f(b)):
            a, b = b, a

    return RootResult(b, max_iter, False, abs(f(b)))


def fixed_point(
    g: Callable[[float], float], x0: float, tol: float = 1e-10, max_iter: int = 100
) -> RootResult:
    """Find fixed point x = g(x)."""
    x = x0
    for i in range(max_iter):
        x_new = g(x)
        if abs(x_new - x) < tol:
            return RootResult(x_new, i + 1, True, abs(x_new - g(x_new)))
        x = x_new

    return RootResult(x, max_iter, False, abs(x - g(x)))


def find_all_roots(
    f: Callable[[float], float], a: float, b: float, n_intervals: int = 100, tol: float = 1e-10
) -> list[float]:
    """Find all roots in interval by searching subintervals."""
    roots = []
    dx = (b - a) / n_intervals

    for i in range(n_intervals):
        x0 = a + i * dx
        x1 = a + (i + 1) * dx

        if f(x0) * f(x1) <= 0:
            try:
                result = bisection(f, x0, x1, tol)
                if result.converged:
                    # Check if we already found this root
                    if not any(abs(r - result.root) < tol * 10 for r in roots):
                        roots.append(result.root)
            except ValueError:
                pass

    return sorted(roots)


def simulate_roots(operations: list[str]) -> list[str]:
    """Simulate root finding operations."""
    results: list[str] = []

    # Test function: x^2 - 2 (root at sqrt(2))
    def f(x):
        return x**2 - 2

    def df(x):
        return 2 * x

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "bisection":
            result = bisection(f, 1, 2)
            results.append(f"root={result.root:.6f} iter={result.iterations}")
        elif cmd == "newton":
            result = newton(f, df, 1.5)
            results.append(f"root={result.root:.6f} iter={result.iterations}")
        elif cmd == "secant":
            result = secant(f, 1, 2)
            results.append(f"root={result.root:.6f} iter={result.iterations}")
        elif cmd == "sin_roots":
            roots = find_all_roots(math.sin, 0, 10)
            results.append(f"roots={[round(r, 4) for r in roots]}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: num_roots_cli.py <command>")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":

        def f(x):
            return x**3 - x - 2

        def df(x):
            return 3 * x**2 - 1

        print("Finding root of x^3 - x - 2:")
        result = bisection(f, 1, 2)
        print(f"Bisection: root={result.root:.10f}, iterations={result.iterations}")

        result = newton(f, df, 1.5)
        print(f"Newton: root={result.root:.10f}, iterations={result.iterations}")

        result = secant(f, 1, 2)
        print(f"Secant: root={result.root:.10f}, iterations={result.iterations}")

        print("\nRoots of sin(x) in [0, 10]:")
        roots = find_all_roots(math.sin, 0, 10)
        print(f"Roots: {[f'{r:.4f}' for r in roots]}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
