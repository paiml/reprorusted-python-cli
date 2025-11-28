#!/usr/bin/env python3
"""Statistics Calculator CLI.

Pure Python statistical functions without external dependencies.
"""

import argparse
import math
import sys


def mean(data: list[float]) -> float:
    """Calculate arithmetic mean."""
    if not data:
        raise ValueError("Cannot calculate mean of empty list")
    return sum(data) / len(data)


def geometric_mean(data: list[float]) -> float:
    """Calculate geometric mean."""
    if not data:
        raise ValueError("Cannot calculate mean of empty list")
    if any(x <= 0 for x in data):
        raise ValueError("Geometric mean requires positive values")

    product = 1.0
    for x in data:
        product *= x

    return product ** (1.0 / len(data))


def harmonic_mean(data: list[float]) -> float:
    """Calculate harmonic mean."""
    if not data:
        raise ValueError("Cannot calculate mean of empty list")
    if any(x <= 0 for x in data):
        raise ValueError("Harmonic mean requires positive values")

    return len(data) / sum(1.0 / x for x in data)


def median(data: list[float]) -> float:
    """Calculate median."""
    if not data:
        raise ValueError("Cannot calculate median of empty list")

    sorted_data = sorted(data)
    n = len(sorted_data)

    if n % 2 == 0:
        return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    return sorted_data[n // 2]


def mode(data: list[float]) -> list[float]:
    """Calculate mode(s) - most frequent values."""
    if not data:
        raise ValueError("Cannot calculate mode of empty list")

    counts: dict[float, int] = {}
    for x in data:
        counts[x] = counts.get(x, 0) + 1

    max_count = max(counts.values())
    modes = [x for x, count in counts.items() if count == max_count]

    return sorted(modes)


def variance(data: list[float], population: bool = False) -> float:
    """Calculate variance."""
    if not data:
        raise ValueError("Cannot calculate variance of empty list")

    n = len(data)
    if n == 1 and not population:
        return 0.0

    m = mean(data)
    ss = sum((x - m) ** 2 for x in data)

    if population:
        return ss / n
    return ss / (n - 1)


def std_dev(data: list[float], population: bool = False) -> float:
    """Calculate standard deviation."""
    return variance(data, population) ** 0.5


def covariance(x: list[float], y: list[float], population: bool = False) -> float:
    """Calculate covariance between two variables."""
    if len(x) != len(y):
        raise ValueError("Lists must have same length")
    if not x:
        raise ValueError("Cannot calculate covariance of empty lists")

    n = len(x)
    mean_x = mean(x)
    mean_y = mean(y)

    cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))

    if population:
        return cov / n
    return cov / (n - 1)


def correlation(x: list[float], y: list[float]) -> float:
    """Calculate Pearson correlation coefficient."""
    if len(x) != len(y):
        raise ValueError("Lists must have same length")

    std_x = std_dev(x)
    std_y = std_dev(y)

    if std_x == 0 or std_y == 0:
        return 0.0

    return covariance(x, y) / (std_x * std_y)


def percentile(data: list[float], p: float) -> float:
    """Calculate p-th percentile (0-100)."""
    if not data:
        raise ValueError("Cannot calculate percentile of empty list")
    if not 0 <= p <= 100:
        raise ValueError("Percentile must be between 0 and 100")

    sorted_data = sorted(data)
    n = len(sorted_data)

    k = (n - 1) * (p / 100)
    f = int(k)
    c = f + 1 if f < n - 1 else f

    return sorted_data[f] + (sorted_data[c] - sorted_data[f]) * (k - f)


def quartiles(data: list[float]) -> tuple[float, float, float]:
    """Calculate Q1, Q2 (median), Q3."""
    q1 = percentile(data, 25)
    q2 = percentile(data, 50)
    q3 = percentile(data, 75)
    return q1, q2, q3


def iqr(data: list[float]) -> float:
    """Calculate interquartile range."""
    q1, _, q3 = quartiles(data)
    return q3 - q1


def range_stat(data: list[float]) -> float:
    """Calculate range (max - min)."""
    if not data:
        raise ValueError("Cannot calculate range of empty list")
    return max(data) - min(data)


def skewness(data: list[float]) -> float:
    """Calculate skewness (Fisher's)."""
    if len(data) < 3:
        raise ValueError("Need at least 3 values for skewness")

    n = len(data)
    m = mean(data)
    s = std_dev(data)

    if s == 0:
        return 0.0

    m3 = sum((x - m) ** 3 for x in data) / n
    return m3 / (s**3)


def kurtosis(data: list[float]) -> float:
    """Calculate excess kurtosis (Fisher's)."""
    if len(data) < 4:
        raise ValueError("Need at least 4 values for kurtosis")

    n = len(data)
    m = mean(data)
    s = std_dev(data, population=True)

    if s == 0:
        return 0.0

    m4 = sum((x - m) ** 4 for x in data) / n
    return (m4 / (s**4)) - 3


def zscore(data: list[float]) -> list[float]:
    """Calculate z-scores for data."""
    m = mean(data)
    s = std_dev(data)

    if s == 0:
        return [0.0] * len(data)

    return [(x - m) / s for x in data]


def sem(data: list[float]) -> float:
    """Calculate standard error of the mean."""
    return std_dev(data) / (len(data) ** 0.5)


def coefficient_of_variation(data: list[float]) -> float:
    """Calculate coefficient of variation (CV)."""
    m = mean(data)
    if m == 0:
        raise ValueError("Mean is zero, CV undefined")
    return std_dev(data) / m


def moving_average(data: list[float], window: int) -> list[float]:
    """Calculate simple moving average."""
    if window < 1:
        raise ValueError("Window must be at least 1")
    if window > len(data):
        raise ValueError("Window larger than data")

    result = []
    for i in range(len(data) - window + 1):
        result.append(mean(data[i : i + window]))

    return result


def weighted_mean(data: list[float], weights: list[float]) -> float:
    """Calculate weighted arithmetic mean."""
    if len(data) != len(weights):
        raise ValueError("Data and weights must have same length")
    if not data:
        raise ValueError("Cannot calculate mean of empty list")

    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("Total weight is zero")

    return sum(d * w for d, w in zip(data, weights, strict=False)) / total_weight


def trimmed_mean(data: list[float], proportion: float) -> float:
    """Calculate trimmed mean."""
    if not 0 <= proportion < 0.5:
        raise ValueError("Proportion must be between 0 and 0.5")

    sorted_data = sorted(data)
    n = len(sorted_data)
    k = int(n * proportion)

    trimmed = sorted_data[k : n - k] if k > 0 else sorted_data
    return mean(trimmed)


def describe(data: list[float]) -> dict[str, float]:
    """Generate summary statistics."""
    n = len(data)
    q1, q2, q3 = quartiles(data)

    return {
        "count": float(n),
        "mean": mean(data),
        "std": std_dev(data),
        "min": min(data),
        "25%": q1,
        "50%": q2,
        "75%": q3,
        "max": max(data),
        "range": range_stat(data),
        "iqr": q3 - q1,
        "variance": variance(data),
        "skewness": skewness(data) if n >= 3 else float("nan"),
        "kurtosis": kurtosis(data) if n >= 4 else float("nan"),
    }


def linear_regression(x: list[float], y: list[float]) -> tuple[float, float, float]:
    """Simple linear regression. Returns (slope, intercept, r_squared)."""
    if len(x) != len(y):
        raise ValueError("Lists must have same length")

    n = len(x)
    mean_x = mean(x)
    mean_y = mean(y)

    ss_xx = sum((xi - mean_x) ** 2 for xi in x)
    ss_xy = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    ss_yy = sum((yi - mean_y) ** 2 for yi in y)

    if ss_xx == 0:
        raise ValueError("Variance of x is zero")

    slope = ss_xy / ss_xx
    intercept = mean_y - slope * mean_x

    r_squared = (ss_xy**2) / (ss_xx * ss_yy) if ss_yy != 0 else 0

    return slope, intercept, r_squared


def main() -> int:
    parser = argparse.ArgumentParser(description="Statistical calculations")
    parser.add_argument("values", nargs="*", type=float, help="Data values")
    parser.add_argument(
        "--mode",
        choices=[
            "describe",
            "mean",
            "median",
            "std",
            "var",
            "corr",
            "zscore",
            "percentile",
            "regression",
        ],
        default="describe",
        help="Calculation mode",
    )
    parser.add_argument("--y", nargs="*", type=float, help="Y values for correlation/regression")
    parser.add_argument("-p", type=float, default=50, help="Percentile value (0-100)")

    args = parser.parse_args()

    if not args.values:
        values = [float(x) for x in sys.stdin.read().split()]
    else:
        values = args.values

    if args.mode == "describe":
        stats = describe(values)
        print("Summary Statistics:")
        print("-" * 30)
        for key, val in stats.items():
            if math.isnan(val):
                print(f"{key:>12}: N/A")
            else:
                print(f"{key:>12}: {val:.4f}")

    elif args.mode == "mean":
        print(f"Mean: {mean(values):.6f}")
        print(f"Geometric Mean: {geometric_mean([x for x in values if x > 0]):.6f}")
        print(f"Harmonic Mean: {harmonic_mean([x for x in values if x > 0]):.6f}")

    elif args.mode == "median":
        print(f"Median: {median(values):.6f}")
        modes = mode(values)
        print(f"Mode(s): {', '.join(f'{m:.6f}' for m in modes)}")

    elif args.mode == "std":
        print(f"Std Dev (sample): {std_dev(values):.6f}")
        print(f"Std Dev (population): {std_dev(values, population=True):.6f}")
        print(f"SEM: {sem(values):.6f}")

    elif args.mode == "var":
        print(f"Variance (sample): {variance(values):.6f}")
        print(f"Variance (population): {variance(values, population=True):.6f}")

    elif args.mode == "corr" and args.y:
        r = correlation(values, args.y)
        cov = covariance(values, args.y)
        print(f"Correlation: {r:.6f}")
        print(f"Covariance: {cov:.6f}")

    elif args.mode == "zscore":
        z = zscore(values)
        print("Z-scores:")
        for _i, (v, zs) in enumerate(zip(values, z, strict=False)):
            print(f"  {v:.2f} -> {zs:.4f}")

    elif args.mode == "percentile":
        p = percentile(values, args.p)
        print(f"{args.p}th percentile: {p:.6f}")

        q1, q2, q3 = quartiles(values)
        print(f"Q1 (25%): {q1:.6f}")
        print(f"Q2 (50%): {q2:.6f}")
        print(f"Q3 (75%): {q3:.6f}")
        print(f"IQR: {iqr(values):.6f}")

    elif args.mode == "regression" and args.y:
        slope, intercept, r2 = linear_regression(values, args.y)
        print(f"y = {slope:.6f}x + {intercept:.6f}")
        print(f"R-squared: {r2:.6f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
