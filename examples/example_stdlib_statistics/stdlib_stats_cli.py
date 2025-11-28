#!/usr/bin/env python3
"""Standard Library Statistics CLI.

Statistical functions using Python's statistics module.
"""

import argparse
import statistics
import sys


def mean(data: list[float]) -> float:
    """Arithmetic mean."""
    return statistics.mean(data)


def fmean(data: list[float]) -> float:
    """Fast floating-point arithmetic mean."""
    return statistics.fmean(data)


def geometric_mean(data: list[float]) -> float:
    """Geometric mean."""
    return statistics.geometric_mean(data)


def harmonic_mean(data: list[float]) -> float:
    """Harmonic mean."""
    return statistics.harmonic_mean(data)


def median(data: list[float]) -> float:
    """Median (middle value)."""
    return statistics.median(data)


def median_low(data: list[float]) -> float:
    """Low median."""
    return statistics.median_low(data)


def median_high(data: list[float]) -> float:
    """High median."""
    return statistics.median_high(data)


def median_grouped(data: list[float], interval: float = 1.0) -> float:
    """Median of grouped data."""
    return statistics.median_grouped(data, interval)


def mode(data: list) -> any:
    """Mode (most common value)."""
    return statistics.mode(data)


def multimode(data: list) -> list:
    """All modes."""
    return statistics.multimode(data)


def pstdev(data: list[float], mu: float | None = None) -> float:
    """Population standard deviation."""
    if mu is not None:
        return statistics.pstdev(data, mu)
    return statistics.pstdev(data)


def pvariance(data: list[float], mu: float | None = None) -> float:
    """Population variance."""
    if mu is not None:
        return statistics.pvariance(data, mu)
    return statistics.pvariance(data)


def stdev(data: list[float], xbar: float | None = None) -> float:
    """Sample standard deviation."""
    if xbar is not None:
        return statistics.stdev(data, xbar)
    return statistics.stdev(data)


def variance(data: list[float], xbar: float | None = None) -> float:
    """Sample variance."""
    if xbar is not None:
        return statistics.variance(data, xbar)
    return statistics.variance(data)


def quantiles(data: list[float], n: int = 4) -> list[float]:
    """Quantiles dividing data into n intervals."""
    return statistics.quantiles(data, n=n)


def covariance(x: list[float], y: list[float]) -> float:
    """Covariance of two datasets."""
    return statistics.covariance(x, y)


def correlation(x: list[float], y: list[float]) -> float:
    """Pearson correlation coefficient."""
    return statistics.correlation(x, y)


def linear_regression(x: list[float], y: list[float]) -> tuple[float, float]:
    """Simple linear regression."""
    result = statistics.linear_regression(x, y)
    return (result.slope, result.intercept)


def z_score(value: float, data: list[float]) -> float:
    """Calculate z-score of a value relative to data."""
    m = mean(data)
    s = stdev(data)
    return (value - m) / s


def percentile_rank(value: float, data: list[float]) -> float:
    """Calculate percentile rank of a value."""
    sorted_data = sorted(data)
    count_below = sum(1 for x in sorted_data if x < value)
    count_equal = sum(1 for x in sorted_data if x == value)
    return 100 * (count_below + 0.5 * count_equal) / len(data)


def interquartile_range(data: list[float]) -> float:
    """Calculate IQR (Q3 - Q1)."""
    q = quantiles(data, n=4)
    return q[2] - q[0]


def coefficient_of_variation(data: list[float]) -> float:
    """Coefficient of variation (CV)."""
    return stdev(data) / mean(data)


def describe(data: list[float]) -> dict:
    """Descriptive statistics summary."""
    return {
        "count": len(data),
        "mean": mean(data),
        "median": median(data),
        "mode": mode(data) if len(set(data)) < len(data) else None,
        "stdev": stdev(data) if len(data) > 1 else 0,
        "variance": variance(data) if len(data) > 1 else 0,
        "min": min(data),
        "max": max(data),
        "range": max(data) - min(data),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Statistics CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # mean
    mean_p = subparsers.add_parser("mean", help="Arithmetic mean")
    mean_p.add_argument("values", type=float, nargs="+")

    # median
    median_p = subparsers.add_parser("median", help="Median")
    median_p.add_argument("values", type=float, nargs="+")

    # mode
    mode_p = subparsers.add_parser("mode", help="Mode")
    mode_p.add_argument("values", type=float, nargs="+")

    # stdev
    stdev_p = subparsers.add_parser("stdev", help="Standard deviation")
    stdev_p.add_argument("values", type=float, nargs="+")

    # variance
    var_p = subparsers.add_parser("variance", help="Variance")
    var_p.add_argument("values", type=float, nargs="+")

    # quantiles
    quant_p = subparsers.add_parser("quantiles", help="Quantiles")
    quant_p.add_argument("values", type=float, nargs="+")
    quant_p.add_argument("-n", type=int, default=4)

    # describe
    desc_p = subparsers.add_parser("describe", help="Descriptive statistics")
    desc_p.add_argument("values", type=float, nargs="+")

    # correlation
    corr_p = subparsers.add_parser("correlation", help="Correlation")
    corr_p.add_argument("--x", type=float, nargs="+", required=True)
    corr_p.add_argument("--y", type=float, nargs="+", required=True)

    # regression
    reg_p = subparsers.add_parser("regression", help="Linear regression")
    reg_p.add_argument("--x", type=float, nargs="+", required=True)
    reg_p.add_argument("--y", type=float, nargs="+", required=True)

    args = parser.parse_args()

    if args.command == "mean":
        print(mean(args.values))
    elif args.command == "median":
        print(median(args.values))
    elif args.command == "mode":
        print(mode(args.values))
    elif args.command == "stdev":
        print(stdev(args.values))
    elif args.command == "variance":
        print(variance(args.values))
    elif args.command == "quantiles":
        print(quantiles(args.values, n=args.n))
    elif args.command == "describe":
        stats = describe(args.values)
        for key, value in stats.items():
            print(f"{key}: {value}")
    elif args.command == "correlation":
        print(correlation(args.x, args.y))
    elif args.command == "regression":
        slope, intercept = linear_regression(args.x, args.y)
        print(f"y = {slope:.4f}x + {intercept:.4f}")
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
