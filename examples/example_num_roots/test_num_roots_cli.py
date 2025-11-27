"""Tests for num_roots_cli.py"""

import math

import pytest
from num_roots_cli import (
    RootResult,
    bisection,
    brent,
    find_all_roots,
    fixed_point,
    newton,
    regula_falsi,
    secant,
    simulate_roots,
)


class TestBisection:
    def test_sqrt2(self):
        def f(x):
            return x**2 - 2
        result = bisection(f, 1, 2)
        assert result.converged
        assert abs(result.root - math.sqrt(2)) < 1e-9

    def test_cubic(self):
        def f(x):
            return x**3 - x - 2
        result = bisection(f, 1, 2)
        assert result.converged
        assert abs(f(result.root)) < 1e-9

    def test_sign_error(self):
        def f(x):
            return x**2 + 1  # No real root
        with pytest.raises(ValueError):
            bisection(f, 0, 1)

    def test_converges_quickly(self):
        def f(x):
            return x - 0.5
        result = bisection(f, 0, 1)
        assert result.converged
        assert result.iterations < 50

    def test_exact_root_at_midpoint(self):
        def f(x):
            return x
        result = bisection(f, -1, 1)
        assert result.converged
        assert abs(result.root) < 1e-9


class TestNewton:
    def test_sqrt2(self):
        def f(x):
            return x**2 - 2
        def df(x):
            return 2 * x
        result = newton(f, df, 1.5)
        assert result.converged
        assert abs(result.root - math.sqrt(2)) < 1e-9

    def test_cubic(self):
        def f(x):
            return x**3 - x - 2
        def df(x):
            return 3 * x**2 - 1
        result = newton(f, df, 1.5)
        assert result.converged
        assert abs(f(result.root)) < 1e-9

    def test_faster_than_bisection(self):
        def f(x):
            return x**2 - 2
        def df(x):
            return 2 * x
        newton_result = newton(f, df, 1.5)
        bisect_result = bisection(f, 1, 2)
        assert newton_result.iterations < bisect_result.iterations

    def test_zero_derivative(self):
        def f(x):
            return x**3
        def df(x):
            return 3 * x**2  # Zero at x=0
        result = newton(f, df, 0.0)
        # Should fail or converge with difficulty
        assert not result.converged or abs(result.root) < 1e-9

    def test_converges_quadratically(self):
        def f(x):
            return x**2 - 2
        def df(x):
            return 2 * x
        result = newton(f, df, 1.5)
        assert result.iterations < 10


class TestSecant:
    def test_sqrt2(self):
        def f(x):
            return x**2 - 2
        result = secant(f, 1, 2)
        assert result.converged
        assert abs(result.root - math.sqrt(2)) < 1e-9

    def test_cubic(self):
        def f(x):
            return x**3 - x - 2
        result = secant(f, 1, 2)
        assert result.converged
        assert abs(f(result.root)) < 1e-9

    def test_linear(self):
        def f(x):
            return 2 * x - 4
        result = secant(f, 0, 3)
        assert result.converged
        assert abs(result.root - 2) < 1e-9

    def test_no_derivative_needed(self):
        def f(x):
            return x**4 - x - 1
        result = secant(f, 1, 2)
        assert result.converged
        assert abs(f(result.root)) < 1e-9


class TestRegulaFalsi:
    def test_sqrt2(self):
        def f(x):
            return x**2 - 2
        result = regula_falsi(f, 1, 2)
        assert result.converged
        assert abs(result.root - math.sqrt(2)) < 1e-9

    def test_cubic(self):
        def f(x):
            return x**3 - x - 2
        result = regula_falsi(f, 1, 2)
        assert result.converged
        assert abs(f(result.root)) < 1e-9

    def test_sign_error(self):
        def f(x):
            return x**2 + 1
        with pytest.raises(ValueError):
            regula_falsi(f, 0, 1)


class TestBrent:
    def test_sqrt2(self):
        def f(x):
            return x**2 - 2
        result = brent(f, 1, 2)
        assert result.converged
        assert abs(result.root - math.sqrt(2)) < 1e-9

    def test_cubic(self):
        def f(x):
            return x**3 - x - 2
        result = brent(f, 1, 2)
        assert result.converged
        assert abs(f(result.root)) < 1e-9

    def test_sign_error(self):
        def f(x):
            return x**2 + 1
        with pytest.raises(ValueError):
            brent(f, 0, 1)

    def test_efficient(self):
        def f(x):
            return x**2 - 2
        result = brent(f, 1, 2)
        assert result.iterations < 20


class TestFixedPoint:
    def test_sqrt2(self):
        def g(x):
            return (x + 2 / x) / 2  # Babylonian method
        result = fixed_point(g, 1.5)
        assert result.converged
        assert abs(result.root - math.sqrt(2)) < 1e-9

    def test_convergent(self):
        def g(x):
            return math.cos(x)
        result = fixed_point(g, 0.5)
        # Fixed point of cos(x) is ~0.739
        assert result.converged
        assert abs(result.root - 0.7390851332151607) < 1e-9

    def test_linear(self):
        def g(x):
            return x / 2 + 1  # x = x/2 + 1 => x = 2
        result = fixed_point(g, 0.0)
        assert result.converged
        assert abs(result.root - 2) < 1e-9


class TestFindAllRoots:
    def test_sin_roots(self):
        roots = find_all_roots(math.sin, 0.1, 10)  # Start past 0 to avoid edge
        # Should find roots at pi, 2*pi, 3*pi
        assert len(roots) >= 2
        for r in roots:
            assert abs(math.sin(r)) < 1e-9

    def test_quadratic_two_roots(self):
        def f(x):
            return x**2 - 4  # Roots at -2 and 2
        roots = find_all_roots(f, -3, 3)
        assert len(roots) == 2
        for r in roots:
            assert abs(f(r)) < 1e-9

    def test_cubic_one_real_root(self):
        def f(x):
            return x**3 + x + 1
        roots = find_all_roots(f, -2, 2)
        assert len(roots) >= 1
        for r in roots:
            assert abs(f(r)) < 1e-9

    def test_no_roots(self):
        def f(x):
            return x**2 + 1  # No real roots
        roots = find_all_roots(f, -10, 10)
        assert len(roots) == 0


class TestRootResult:
    def test_create(self):
        result = RootResult(1.414, 5, True, 1e-10)
        assert result.root == 1.414
        assert result.iterations == 5
        assert result.converged is True
        assert result.error == 1e-10

    def test_not_converged(self):
        result = RootResult(1.5, 100, False, 0.01)
        assert not result.converged


class TestSimulateRoots:
    def test_bisection(self):
        result = simulate_roots(["bisection:"])
        assert "root=" in result[0]
        assert "iter=" in result[0]

    def test_newton(self):
        result = simulate_roots(["newton:"])
        assert "root=" in result[0]

    def test_secant(self):
        result = simulate_roots(["secant:"])
        assert "root=" in result[0]

    def test_sin_roots(self):
        result = simulate_roots(["sin_roots:"])
        assert "roots=" in result[0]

    def test_multiple_operations(self):
        result = simulate_roots(["bisection:", "newton:"])
        assert len(result) == 2
