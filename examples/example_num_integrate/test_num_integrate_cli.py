"""Tests for num_integrate_cli.py"""

import math

from num_integrate_cli import (
    IntegrationResult,
    adaptive_simpson,
    double_integral,
    gauss_legendre,
    improper_integral,
    midpoint,
    monte_carlo,
    romberg,
    simpson,
    simpson38,
    simulate_integrate,
    trapezoidal,
)


class TestTrapezoidal:
    def test_constant(self):
        def f(x):
            return 5.0
        result = trapezoidal(f, 0, 2, 10)
        assert abs(result - 10.0) < 1e-10

    def test_linear(self):
        def f(x):
            return x
        result = trapezoidal(f, 0, 1, 100)
        assert abs(result - 0.5) < 1e-10

    def test_quadratic(self):
        def f(x):
            return x ** 2
        result = trapezoidal(f, 0, 1, 1000)
        assert abs(result - 1 / 3) < 1e-5

    def test_sin(self):
        result = trapezoidal(math.sin, 0, math.pi, 1000)
        assert abs(result - 2.0) < 1e-5

    def test_exp(self):
        result = trapezoidal(math.exp, 0, 1, 1000)
        assert abs(result - (math.e - 1)) < 1e-5


class TestSimpson:
    def test_constant(self):
        def f(x):
            return 5.0
        result = simpson(f, 0, 2, 10)
        assert abs(result - 10.0) < 1e-10

    def test_linear(self):
        def f(x):
            return x
        result = simpson(f, 0, 1, 100)
        assert abs(result - 0.5) < 1e-10

    def test_quadratic(self):
        def f(x):
            return x ** 2
        result = simpson(f, 0, 1, 100)
        assert abs(result - 1 / 3) < 1e-10

    def test_cubic(self):
        def f(x):
            return x ** 3
        result = simpson(f, 0, 1, 100)
        assert abs(result - 0.25) < 1e-10

    def test_sin(self):
        result = simpson(math.sin, 0, math.pi, 100)
        assert abs(result - 2.0) < 1e-7

    def test_more_accurate_than_trapezoidal(self):
        def f(x):
            return x ** 2
        trap = trapezoidal(f, 0, 1, 10)
        simp = simpson(f, 0, 1, 10)
        exact = 1 / 3
        assert abs(simp - exact) < abs(trap - exact)


class TestSimpson38:
    def test_constant(self):
        def f(x):
            return 5.0
        result = simpson38(f, 0, 2, 9)
        assert abs(result - 10.0) < 1e-10

    def test_quadratic(self):
        def f(x):
            return x ** 2
        result = simpson38(f, 0, 1, 99)
        assert abs(result - 1 / 3) < 1e-8

    def test_cubic(self):
        def f(x):
            return x ** 3
        result = simpson38(f, 0, 1, 99)
        assert abs(result - 0.25) < 1e-8


class TestMidpoint:
    def test_constant(self):
        def f(x):
            return 5.0
        result = midpoint(f, 0, 2, 10)
        assert abs(result - 10.0) < 1e-10

    def test_linear(self):
        def f(x):
            return x
        result = midpoint(f, 0, 1, 100)
        assert abs(result - 0.5) < 1e-10

    def test_quadratic(self):
        def f(x):
            return x ** 2
        result = midpoint(f, 0, 1, 1000)
        assert abs(result - 1 / 3) < 1e-5


class TestRomberg:
    def test_quadratic(self):
        def f(x):
            return x ** 2
        result = romberg(f, 0, 1)
        assert abs(result.value - 1 / 3) < 1e-10

    def test_sin(self):
        result = romberg(math.sin, 0, math.pi)
        assert abs(result.value - 2.0) < 1e-10

    def test_exp(self):
        result = romberg(math.exp, 0, 1)
        assert abs(result.value - (math.e - 1)) < 1e-10

    def test_efficient(self):
        def f(x):
            return x ** 2
        result = romberg(f, 0, 1)
        assert result.n_evaluations < 100

    def test_returns_result_struct(self):
        def f(x):
            return x
        result = romberg(f, 0, 1)
        assert isinstance(result, IntegrationResult)
        assert result.n_evaluations > 0


class TestGaussLegendre:
    def test_constant(self):
        def f(x):
            return 5.0
        result = gauss_legendre(f, 0, 2, 2)
        assert abs(result - 10.0) < 1e-10

    def test_linear(self):
        def f(x):
            return x
        result = gauss_legendre(f, 0, 1, 2)
        assert abs(result - 0.5) < 1e-10

    def test_quadratic(self):
        def f(x):
            return x ** 2
        result = gauss_legendre(f, 0, 1, 2)
        assert abs(result - 1 / 3) < 1e-10

    def test_polynomial_exact(self):
        # 5-point Gauss integrates polynomials up to degree 9 exactly
        def f(x):
            return x ** 5
        result = gauss_legendre(f, 0, 1, 5)
        assert abs(result - 1 / 6) < 1e-10

    def test_sin(self):
        result = gauss_legendre(math.sin, 0, math.pi, 5)
        assert abs(result - 2.0) < 1e-5

    def test_different_points(self):
        def f(x):
            return x ** 2
        r2 = gauss_legendre(f, 0, 1, 2)
        r3 = gauss_legendre(f, 0, 1, 3)
        r5 = gauss_legendre(f, 0, 1, 5)
        # All should give exact result for x^2
        assert abs(r2 - 1 / 3) < 1e-10
        assert abs(r3 - 1 / 3) < 1e-10
        assert abs(r5 - 1 / 3) < 1e-10


class TestAdaptiveSimpson:
    def test_quadratic(self):
        def f(x):
            return x ** 2
        result = adaptive_simpson(f, 0, 1)
        assert abs(result.value - 1 / 3) < 1e-10

    def test_sin(self):
        result = adaptive_simpson(math.sin, 0, math.pi)
        assert abs(result.value - 2.0) < 1e-10

    def test_handles_discontinuity_like(self):
        # Step-like function
        def f(x):
            return 1.0 if x > 0.5 else 0.0
        result = adaptive_simpson(f, 0, 1, tol=1e-6)
        assert abs(result.value - 0.5) < 0.01


class TestMonteCarlo:
    def test_constant(self):
        def f(x):
            return 5.0
        result = monte_carlo(f, 0, 2, n_samples=1000)
        assert abs(result.value - 10.0) < 0.5

    def test_linear(self):
        def f(x):
            return x
        result = monte_carlo(f, 0, 1, n_samples=10000)
        assert abs(result.value - 0.5) < 0.1

    def test_returns_error_estimate(self):
        def f(x):
            return x ** 2
        result = monte_carlo(f, 0, 1, n_samples=10000)
        assert result.error_estimate > 0
        assert result.n_evaluations == 10000

    def test_reproducible_with_seed(self):
        def f(x):
            return x ** 2
        r1 = monte_carlo(f, 0, 1, seed=12345)
        r2 = monte_carlo(f, 0, 1, seed=12345)
        assert r1.value == r2.value


class TestDoubleIntegral:
    def test_constant(self):
        def f(x, y):
            return 1.0
        result = double_integral(f, 0, 1, 0, 1)
        assert abs(result - 1.0) < 1e-5

    def test_product(self):
        # Integral of x*y over [0,1]x[0,1] = 1/4
        def f(x, y):
            return x * y
        result = double_integral(f, 0, 1, 0, 1, nx=100, ny=100)
        assert abs(result - 0.25) < 1e-5

    def test_sum(self):
        # Integral of (x+y) over [0,1]x[0,1] = 1
        def f(x, y):
            return x + y
        result = double_integral(f, 0, 1, 0, 1, nx=100, ny=100)
        assert abs(result - 1.0) < 1e-5

    def test_rectangular_region(self):
        def f(x, y):
            return 1.0
        result = double_integral(f, 0, 2, 0, 3)
        assert abs(result - 6.0) < 1e-5


class TestImproperIntegral:
    def test_exponential_decay(self):
        # Integral of e^(-x) from 0 to inf = 1
        def f(x):
            return math.exp(-x)
        result = improper_integral(f, 0, method="exponential", n=200)
        assert abs(result - 1.0) < 0.1

    def test_inverse_square(self):
        # Integral of 1/x^2 from 1 to inf = 1
        def f(x):
            return 1 / (x ** 2)
        result = improper_integral(f, 1, method="rational", n=200)
        assert abs(result - 1.0) < 0.1


class TestIntegrationResult:
    def test_create(self):
        result = IntegrationResult(1.5, 0.01, 100)
        assert result.value == 1.5
        assert result.error_estimate == 0.01
        assert result.n_evaluations == 100


class TestSimulateIntegrate:
    def test_trapezoidal(self):
        result = simulate_integrate(["trapezoidal:"])
        # Integral of x^2 from 0 to 1 = 1/3
        assert "0.33" in result[0]

    def test_simpson(self):
        result = simulate_integrate(["simpson:"])
        assert "0.33" in result[0]

    def test_gauss(self):
        result = simulate_integrate(["gauss:"])
        assert "0.33" in result[0]

    def test_romberg(self):
        result = simulate_integrate(["romberg:"])
        assert "0.33" in result[0]

    def test_sin(self):
        result = simulate_integrate(["sin:"])
        # Integral of sin(x) from 0 to pi = 2
        assert "2.0" in result[0]

    def test_multiple_operations(self):
        result = simulate_integrate(["trapezoidal:", "simpson:"])
        assert len(result) == 2
