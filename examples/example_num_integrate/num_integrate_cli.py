"""Numerical Integration CLI.

Demonstrates numerical integration methods: trapezoidal, Simpson, Gaussian.
"""

import math
import sys
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class IntegrationResult:
    """Result of numerical integration."""

    value: float
    error_estimate: float
    n_evaluations: int


def trapezoidal(f: Callable[[float], float], a: float, b: float, n: int = 100) -> float:
    """Trapezoidal rule integration."""
    h = (b - a) / n
    total = (f(a) + f(b)) / 2
    for i in range(1, n):
        total += f(a + i * h)
    return total * h


def simpson(f: Callable[[float], float], a: float, b: float, n: int = 100) -> float:
    """Simpson's rule integration (n must be even)."""
    if n % 2 != 0:
        n += 1
    h = (b - a) / n
    total = f(a) + f(b)

    for i in range(1, n):
        x = a + i * h
        if i % 2 == 0:
            total += 2 * f(x)
        else:
            total += 4 * f(x)

    return total * h / 3


def simpson38(f: Callable[[float], float], a: float, b: float, n: int = 99) -> float:
    """Simpson's 3/8 rule integration (n must be multiple of 3)."""
    while n % 3 != 0:
        n += 1
    h = (b - a) / n
    total = f(a) + f(b)

    for i in range(1, n):
        x = a + i * h
        if i % 3 == 0:
            total += 2 * f(x)
        else:
            total += 3 * f(x)

    return total * 3 * h / 8


def midpoint(f: Callable[[float], float], a: float, b: float, n: int = 100) -> float:
    """Midpoint rule integration."""
    h = (b - a) / n
    total = 0.0
    for i in range(n):
        x_mid = a + (i + 0.5) * h
        total += f(x_mid)
    return total * h


def romberg(
    f: Callable[[float], float], a: float, b: float, max_iter: int = 10, tol: float = 1e-10
) -> IntegrationResult:
    """Romberg integration with Richardson extrapolation."""
    R = [[0.0] * (max_iter + 1) for _ in range(max_iter + 1)]
    n_evals = 2

    R[0][0] = (b - a) * (f(a) + f(b)) / 2

    for i in range(1, max_iter + 1):
        h = (b - a) / (2**i)

        # Composite trapezoidal
        n_points = 2 ** (i - 1)
        inner_sum = sum(f(a + (2 * k - 1) * h) for k in range(1, n_points + 1))
        R[i][0] = R[i - 1][0] / 2 + h * inner_sum
        n_evals += n_points

        # Richardson extrapolation
        for j in range(1, i + 1):
            R[i][j] = (4**j * R[i][j - 1] - R[i - 1][j - 1]) / (4**j - 1)

        if i > 1 and abs(R[i][i] - R[i - 1][i - 1]) < tol:
            return IntegrationResult(R[i][i], abs(R[i][i] - R[i - 1][i - 1]), n_evals)

    return IntegrationResult(
        R[max_iter][max_iter], abs(R[max_iter][max_iter] - R[max_iter - 1][max_iter - 1]), n_evals
    )


# Gaussian quadrature nodes and weights
GAUSS_LEGENDRE_2 = [(-0.5773502691896257, 1.0), (0.5773502691896257, 1.0)]

GAUSS_LEGENDRE_3 = [
    (-0.7745966692414834, 0.5555555555555556),
    (0.0, 0.8888888888888888),
    (0.7745966692414834, 0.5555555555555556),
]

GAUSS_LEGENDRE_5 = [
    (-0.9061798459386640, 0.2369268850561891),
    (-0.5384693101056831, 0.4786286704993665),
    (0.0, 0.5688888888888889),
    (0.5384693101056831, 0.4786286704993665),
    (0.9061798459386640, 0.2369268850561891),
]


def gauss_legendre(f: Callable[[float], float], a: float, b: float, n_points: int = 5) -> float:
    """Gaussian quadrature integration."""
    if n_points == 2:
        nodes_weights = GAUSS_LEGENDRE_2
    elif n_points == 3:
        nodes_weights = GAUSS_LEGENDRE_3
    else:
        nodes_weights = GAUSS_LEGENDRE_5

    # Transform from [-1, 1] to [a, b]
    c1 = (b - a) / 2
    c2 = (b + a) / 2

    total = 0.0
    for node, weight in nodes_weights:
        x = c1 * node + c2
        total += weight * f(x)

    return total * c1


def adaptive_simpson(
    f: Callable[[float], float], a: float, b: float, tol: float = 1e-10, max_depth: int = 50
) -> IntegrationResult:
    """Adaptive Simpson's rule."""
    n_evals = [0]

    def simpson_helper(a: float, b: float, fa: float, fb: float, s: float, depth: int) -> float:
        c = (a + b) / 2
        fc = f(c)
        n_evals[0] += 1

        d = (a + c) / 2
        e = (c + b) / 2
        fd = f(d)
        fe = f(e)
        n_evals[0] += 2

        h = b - a
        s_left = (h / 12) * (fa + 4 * fd + fc)
        s_right = (h / 12) * (fc + 4 * fe + fb)
        s_new = s_left + s_right

        if depth <= 0 or abs(s_new - s) < 15 * tol:
            return s_new + (s_new - s) / 15

        return simpson_helper(a, c, fa, fc, s_left, depth - 1) + simpson_helper(
            c, b, fc, fb, s_right, depth - 1
        )

    fa = f(a)
    fb = f(b)
    fc = f((a + b) / 2)
    n_evals[0] = 3

    s = (b - a) * (fa + 4 * fc + fb) / 6
    result = simpson_helper(a, b, fa, fb, s, max_depth)

    return IntegrationResult(result, tol, n_evals[0])


def monte_carlo(
    f: Callable[[float], float], a: float, b: float, n_samples: int = 10000, seed: int = 42
) -> IntegrationResult:
    """Monte Carlo integration."""
    # Simple LCG random number generator
    state = seed
    samples = []
    for _ in range(n_samples):
        state = (1103515245 * state + 12345) % (2**31)
        u = state / (2**31)
        x = a + u * (b - a)
        samples.append(f(x))

    mean = sum(samples) / n_samples
    integral = (b - a) * mean

    # Estimate error (standard error of the mean)
    variance = sum((s - mean) ** 2 for s in samples) / (n_samples - 1)
    error = (b - a) * math.sqrt(variance / n_samples)

    return IntegrationResult(integral, error, n_samples)


def double_integral(
    f: Callable[[float, float], float],
    ax: float,
    bx: float,
    ay: float,
    by: float,
    nx: int = 50,
    ny: int = 50,
) -> float:
    """Double integral using trapezoidal rule."""
    hx = (bx - ax) / nx
    hy = (by - ay) / ny

    total = 0.0
    for i in range(nx + 1):
        x = ax + i * hx
        wx = 0.5 if i == 0 or i == nx else 1.0
        for j in range(ny + 1):
            y = ay + j * hy
            wy = 0.5 if j == 0 or j == ny else 1.0
            total += wx * wy * f(x, y)

    return total * hx * hy


def improper_integral(
    f: Callable[[float], float], a: float, method: str = "exponential", n: int = 100
) -> float:
    """Integrate from a to infinity using transformation."""
    if method == "exponential":
        # Transform x in [a, inf) to t in [0, 1) via x = a - ln(1-t)
        def g(t: float) -> float:
            if t >= 1:
                return 0.0
            x = a - math.log(1 - t)
            return f(x) / (1 - t)

        return simpson(g, 0, 0.9999, n)
    else:
        # Transform x in [a, inf) to t in [0, 1) via x = a + t/(1-t)
        def g(t: float) -> float:
            if t >= 1:
                return 0.0
            x = a + t / (1 - t)
            return f(x) / ((1 - t) ** 2)

        return simpson(g, 0, 0.9999, n)


def simulate_integrate(operations: list[str]) -> list[str]:
    """Simulate integration operations."""
    results: list[str] = []

    # Test function: x^2
    def f(x):
        return x**2

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "trapezoidal":
            result = trapezoidal(f, 0, 1, 100)
            results.append(f"{result:.6f}")
        elif cmd == "simpson":
            result = simpson(f, 0, 1, 100)
            results.append(f"{result:.6f}")
        elif cmd == "gauss":
            result = gauss_legendre(f, 0, 1, 5)
            results.append(f"{result:.6f}")
        elif cmd == "romberg":
            result = romberg(f, 0, 1)
            results.append(f"{result.value:.6f}")
        elif cmd == "sin":
            # Integral of sin(x) from 0 to pi = 2
            result = simpson(math.sin, 0, math.pi, 100)
            results.append(f"{result:.6f}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: num_integrate_cli.py <command>")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":

        def f(x):
            return x**2

        print("Integrating x^2 from 0 to 1 (exact = 1/3):")
        print(f"Trapezoidal (n=10):  {trapezoidal(f, 0, 1, 10):.10f}")
        print(f"Trapezoidal (n=100): {trapezoidal(f, 0, 1, 100):.10f}")
        print(f"Simpson (n=10):      {simpson(f, 0, 1, 10):.10f}")
        print(f"Simpson (n=100):     {simpson(f, 0, 1, 100):.10f}")
        print(f"Gauss-Legendre (5):  {gauss_legendre(f, 0, 1, 5):.10f}")

        result = romberg(f, 0, 1)
        print(f"Romberg:             {result.value:.10f} (evals={result.n_evaluations})")

        result = adaptive_simpson(f, 0, 1)
        print(f"Adaptive Simpson:    {result.value:.10f} (evals={result.n_evaluations})")

        print("\nIntegral of sin(x) from 0 to pi (exact = 2):")
        print(f"Simpson: {simpson(math.sin, 0, math.pi, 100):.10f}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
