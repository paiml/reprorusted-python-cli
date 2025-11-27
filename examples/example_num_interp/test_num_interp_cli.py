"""Tests for num_interp_cli.py"""


from num_interp_cli import (
    CubicSpline,
    Interpolator,
    hermite_interp,
    lagrange,
    linear_interp,
    newton_divided_diff,
    newton_interp,
    piecewise_linear,
    simulate_interp,
)


class TestLinearInterp:
    def test_midpoint(self):
        result = linear_interp(0.5, 0.0, 0.0, 1.0, 1.0)
        assert abs(result - 0.5) < 1e-10

    def test_endpoints(self):
        assert linear_interp(0.0, 0.0, 0.0, 1.0, 1.0) == 0.0
        assert linear_interp(1.0, 0.0, 0.0, 1.0, 1.0) == 1.0

    def test_extrapolate(self):
        result = linear_interp(2.0, 0.0, 0.0, 1.0, 1.0)
        assert abs(result - 2.0) < 1e-10


class TestPiecewiseLinear:
    def test_at_points(self):
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 1.0, 4.0]
        assert piecewise_linear(xs, ys, 0.0) == 0.0
        assert piecewise_linear(xs, ys, 1.0) == 1.0
        assert piecewise_linear(xs, ys, 2.0) == 4.0

    def test_between_points(self):
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 1.0, 4.0]
        result = piecewise_linear(xs, ys, 0.5)
        assert abs(result - 0.5) < 1e-10

    def test_clamp_left(self):
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 1.0, 4.0]
        assert piecewise_linear(xs, ys, -1.0) == 0.0

    def test_clamp_right(self):
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 1.0, 4.0]
        assert piecewise_linear(xs, ys, 3.0) == 4.0


class TestLagrange:
    def test_at_points(self):
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 1.0, 4.0]
        for x, y in zip(xs, ys, strict=False):
            assert abs(lagrange(xs, ys, x) - y) < 1e-10

    def test_polynomial_exact(self):
        # y = x^2, should be exact with 3+ points
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 1.0, 4.0]
        for x in [0.5, 1.5]:
            expected = x**2
            assert abs(lagrange(xs, ys, x) - expected) < 1e-10

    def test_two_points(self):
        xs = [0.0, 1.0]
        ys = [0.0, 1.0]
        assert abs(lagrange(xs, ys, 0.5) - 0.5) < 1e-10


class TestNewtonDividedDiff:
    def test_linear(self):
        xs = [0.0, 1.0]
        ys = [0.0, 2.0]
        coefs = newton_divided_diff(xs, ys)
        assert abs(coefs[0] - 0.0) < 1e-10
        assert abs(coefs[1] - 2.0) < 1e-10

    def test_quadratic(self):
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 1.0, 4.0]
        coefs = newton_divided_diff(xs, ys)
        assert len(coefs) == 3


class TestNewtonInterp:
    def test_matches_lagrange(self):
        xs = [0.0, 1.0, 2.0, 3.0]
        ys = [0.0, 1.0, 4.0, 9.0]
        coefs = newton_divided_diff(xs, ys)

        for x in [0.5, 1.5, 2.5]:
            newton_result = newton_interp(xs, coefs, x)
            lagrange_result = lagrange(xs, ys, x)
            assert abs(newton_result - lagrange_result) < 1e-10


class TestCubicSpline:
    def test_at_points(self):
        xs = [0.0, 1.0, 2.0, 3.0]
        ys = [0.0, 1.0, 4.0, 9.0]
        spline = CubicSpline.natural(xs, ys)
        for x, y in zip(xs, ys, strict=False):
            assert abs(spline(x) - y) < 1e-10

    def test_continuity(self):
        xs = [0.0, 1.0, 2.0, 3.0]
        ys = [0.0, 1.0, 4.0, 9.0]
        spline = CubicSpline.natural(xs, ys)
        # Check continuity at interior points
        for x in [1.0, 2.0]:
            left = spline(x - 0.0001)
            right = spline(x + 0.0001)
            assert abs(left - right) < 0.01

    def test_clamp_left(self):
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 1.0, 4.0]
        spline = CubicSpline.natural(xs, ys)
        assert spline(-1.0) == 0.0

    def test_clamp_right(self):
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 1.0, 4.0]
        spline = CubicSpline.natural(xs, ys)
        assert spline(3.0) == 4.0


class TestHermiteInterp:
    def test_endpoints(self):
        result = hermite_interp(0, 0, 1, 1, 1, 1, 0)
        assert abs(result - 0) < 1e-10
        result = hermite_interp(0, 0, 1, 1, 1, 1, 1)
        assert abs(result - 1) < 1e-10

    def test_midpoint(self):
        # Linear function y=x, derivative=1
        result = hermite_interp(0, 0, 1, 2, 2, 1, 1)
        assert abs(result - 1) < 1e-10


class TestInterpolator:
    def test_linear(self):
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 1.0, 4.0]
        f = Interpolator.linear(xs, ys)
        assert abs(f(0.5) - 0.5) < 1e-10

    def test_polynomial(self):
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 1.0, 4.0]
        f = Interpolator.polynomial(xs, ys)
        assert abs(f(1.5) - 2.25) < 1e-10

    def test_cubic_spline(self):
        xs = [0.0, 1.0, 2.0, 3.0]
        ys = [0.0, 1.0, 4.0, 9.0]
        f = Interpolator.cubic_spline(xs, ys)
        assert abs(f(1.0) - 1.0) < 1e-10


class TestSimulateInterp:
    def test_linear(self):
        result = simulate_interp(["linear:0.5"])
        assert result == ["0.50"]

    def test_lagrange(self):
        result = simulate_interp(["lagrange:0.5"])
        assert result == ["0.25"]  # x^2 at 0.5

    def test_spline(self):
        result = simulate_interp(["spline:1.0"])
        assert result == ["1.00"]

    def test_newton(self):
        result = simulate_interp(["newton:0.5"])
        assert result == ["0.25"]  # x^2 at 0.5
