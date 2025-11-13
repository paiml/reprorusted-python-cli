#!/usr/bin/env python3
"""
Performance regression detection for benchmarks.

Compares current benchmark results against baseline and detects regressions.
A regression is defined as:
- Execution time increased by more than THRESHOLD% (default: 5%)
- Memory usage increased by more than MEMORY_THRESHOLD% (default: 10%)

Exit codes:
- 0: No regressions detected
- 1: Regressions detected
- 2: Error (missing files, parse errors, etc.)
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

# Thresholds for regression detection
DEFAULT_TIME_THRESHOLD = 5.0  # 5% slower is a regression
DEFAULT_MEMORY_THRESHOLD = 10.0  # 10% more memory is a regression


@dataclass
class BenchmarkResult:
    """Single benchmark result from JSON."""

    name: str
    mean_ms: float
    stddev_ms: float
    memory_kb: float | None = None


@dataclass
class Regression:
    """Detected performance regression."""

    example: str
    implementation: str
    metric: str
    baseline: float
    current: float
    percent_change: float


class RegressionDetector:
    """Detect performance regressions by comparing benchmark results."""

    def __init__(
        self,
        time_threshold: float = DEFAULT_TIME_THRESHOLD,
        memory_threshold: float = DEFAULT_MEMORY_THRESHOLD,
    ):
        self.time_threshold = time_threshold
        self.memory_threshold = memory_threshold

    def load_benchmark_file(self, filepath: Path) -> list[BenchmarkResult]:
        """Load benchmark results from JSON file."""
        try:
            with open(filepath) as f:
                data = json.load(f)

            results = []
            for bench in data.get("benchmarks", []):
                stats = bench.get("statistics", {})
                script = bench.get("script", "")

                # Determine implementation type from script path
                if "python" in script:
                    name = "python"
                elif "rust" in script:
                    name = "rust"
                else:
                    name = script

                results.append(
                    BenchmarkResult(
                        name=name,
                        mean_ms=stats.get("mean_ms", 0.0),
                        stddev_ms=stats.get("stddev_ms", 0.0),
                        memory_kb=stats.get("memory", {}).get("mean_kb"),
                    )
                )

            return results
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {filepath}: {e}", file=sys.stderr)
            return []

    def compare_results(
        self,
        baseline: BenchmarkResult,
        current: BenchmarkResult,
    ) -> list[Regression]:
        """Compare two benchmark results and detect regressions."""
        regressions = []

        # Check execution time regression
        if baseline.mean_ms > 0:
            time_change = (current.mean_ms - baseline.mean_ms) / baseline.mean_ms * 100
            if time_change > self.time_threshold:
                regressions.append(
                    Regression(
                        example="",  # Set by caller
                        implementation=current.name,
                        metric="execution_time",
                        baseline=baseline.mean_ms,
                        current=current.mean_ms,
                        percent_change=time_change,
                    )
                )

        # Check memory regression
        if baseline.memory_kb and current.memory_kb:
            if baseline.memory_kb > 0:
                memory_change = (current.memory_kb - baseline.memory_kb) / baseline.memory_kb * 100
                if memory_change > self.memory_threshold:
                    regressions.append(
                        Regression(
                            example="",  # Set by caller
                            implementation=current.name,
                            metric="memory",
                            baseline=baseline.memory_kb,
                            current=current.memory_kb,
                            percent_change=memory_change,
                        )
                    )

        return regressions

    def check_example(
        self,
        example_name: str,
        baseline_file: Path,
        current_file: Path,
    ) -> list[Regression]:
        """Check a single example for regressions."""
        baseline_results = self.load_benchmark_file(baseline_file)
        current_results = self.load_benchmark_file(current_file)

        if not baseline_results or not current_results:
            return []

        # Create lookup dictionaries
        baseline_by_name = {r.name: r for r in baseline_results}
        current_by_name = {r.name: r for r in current_results}

        # Compare matching implementations
        regressions = []
        for name in baseline_by_name.keys():
            if name in current_by_name:
                found = self.compare_results(baseline_by_name[name], current_by_name[name])
                for reg in found:
                    reg.example = example_name
                    regressions.append(reg)

        return regressions

    def check_all(
        self,
        baseline_dir: Path,
        results_dir: Path,
    ) -> list[Regression]:
        """Check all benchmark files for regressions."""
        all_regressions = []

        # Find all benchmark JSON files in results directory
        for result_file in results_dir.glob("*-bench.json"):
            example_name = result_file.stem.replace("-bench", "")
            baseline_file = baseline_dir / result_file.name

            if baseline_file.exists():
                regressions = self.check_example(example_name, baseline_file, result_file)
                all_regressions.extend(regressions)
            else:
                print(
                    f"Warning: No baseline found for {example_name}",
                    file=sys.stderr,
                )

        return all_regressions


def format_regression_report(regressions: list[Regression]) -> str:
    """Format regression report as readable text."""
    if not regressions:
        return "✅ No performance regressions detected!"

    lines = [
        "❌ Performance regressions detected:",
        "",
    ]

    # Group by example
    by_example: dict[str, list[Regression]] = {}
    for reg in regressions:
        if reg.example not in by_example:
            by_example[reg.example] = []
        by_example[reg.example].append(reg)

    for example, regs in sorted(by_example.items()):
        lines.append(f"📊 {example}:")
        for reg in regs:
            metric_name = reg.metric.replace("_", " ").title()
            unit = "ms" if reg.metric == "execution_time" else "KB"

            lines.append(
                f"  - {reg.implementation} {metric_name}: "
                f"{reg.baseline:.2f}{unit} → {reg.current:.2f}{unit} "
                f"(+{reg.percent_change:.1f}%)"
            )
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Detect performance regressions in benchmarks")
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=Path("benchmarks/baseline"),
        help="Directory containing baseline benchmark results",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("benchmarks/reports"),
        help="Directory containing current benchmark results",
    )
    parser.add_argument(
        "--time-threshold",
        type=float,
        default=DEFAULT_TIME_THRESHOLD,
        help=f"Time regression threshold in percent (default: {DEFAULT_TIME_THRESHOLD}%%)",
    )
    parser.add_argument(
        "--memory-threshold",
        type=float,
        default=DEFAULT_MEMORY_THRESHOLD,
        help=f"Memory regression threshold in percent (default: {DEFAULT_MEMORY_THRESHOLD}%%)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if any baseline files are missing",
    )

    args = parser.parse_args()

    # Validate directories exist
    if not args.baseline_dir.exists():
        print(f"Error: Baseline directory not found: {args.baseline_dir}", file=sys.stderr)
        print(
            "Run benchmarks first and create baseline with: cp benchmarks/reports/*.json benchmarks/baseline/"
        )
        sys.exit(2)

    if not args.results_dir.exists():
        print(f"Error: Results directory not found: {args.results_dir}", file=sys.stderr)
        sys.exit(2)

    # Run regression detection
    detector = RegressionDetector(
        time_threshold=args.time_threshold,
        memory_threshold=args.memory_threshold,
    )

    regressions = detector.check_all(args.baseline_dir, args.results_dir)

    # Print report
    report = format_regression_report(regressions)
    print(report)

    # Exit with appropriate code
    if regressions:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
