#!/usr/bin/env python3
"""
Benchmark visualization and reporting tool.

Generates ASCII and PNG charts from benchmark results.
"""

import json
import sys
from pathlib import Path
from typing import Any


def load_benchmark_results(results_dir: Path) -> list[dict[str, Any]]:
    """Load all benchmark result files from a directory."""
    results = []
    if not results_dir.exists():
        return results

    for json_file in sorted(results_dir.glob("*.json")):
        try:
            with open(json_file) as f:
                data = json.load(f)
                results.append(data)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load {json_file}: {e}", file=sys.stderr)

    return results


def generate_ascii_chart(
    labels: list[str],
    python_times: list[float],
    rust_times: list[float],
    max_width: int = 60
) -> str:
    """Generate ASCII bar chart comparing Python vs Rust execution times."""
    lines = []
    lines.append("=" * 70)
    lines.append("Execution Time Comparison (Python vs Rust)")
    lines.append("=" * 70)
    lines.append("")

    max_time = max(max(python_times), max(rust_times))

    for label, py_time, rs_time in zip(labels, python_times, rust_times, strict=False):
        # Calculate bar lengths
        py_bar_len = int((py_time / max_time) * max_width)
        rs_bar_len = int((rs_time / max_time) * max_width)

        # Speedup calculation
        speedup = py_time / rs_time if rs_time > 0 else 0

        lines.append(f"{label:20s}")
        lines.append(f"  Python: {'█' * py_bar_len} {py_time:6.2f}ms")
        lines.append(f"  Rust:   {'█' * rs_bar_len} {rs_time:6.2f}ms ({speedup:.2f}x)")
        lines.append("")

    return "\n".join(lines)


def generate_memory_chart(
    labels: list[str],
    python_mem: list[int],
    rust_mem: list[int],
    max_width: int = 60
) -> str:
    """Generate ASCII bar chart comparing memory usage."""
    lines = []
    lines.append("=" * 70)
    lines.append("Memory Usage Comparison (Python vs Rust)")
    lines.append("=" * 70)
    lines.append("")

    max_mem = max(max(python_mem), max(rust_mem))

    for label, py_mem, rs_mem in zip(labels, python_mem, rust_mem, strict=False):
        # Calculate bar lengths
        py_bar_len = int((py_mem / max_mem) * max_width)
        rs_bar_len = int((rs_mem / max_mem) * max_width)

        # Reduction calculation
        reduction = ((py_mem - rs_mem) / py_mem * 100) if py_mem > 0 else 0

        # Convert to MB for display
        py_mb = py_mem / 1024
        rs_mb = rs_mem / 1024

        lines.append(f"{label:20s}")
        lines.append(f"  Python: {'█' * py_bar_len} {py_mb:6.1f}MB")
        lines.append(f"  Rust:   {'█' * rs_bar_len} {rs_mb:6.1f}MB ({reduction:.1f}% reduction)")
        lines.append("")

    return "\n".join(lines)


def generate_speedup_chart(
    labels: list[str],
    speedups: list[float],
    max_width: int = 60
) -> str:
    """Generate ASCII bar chart showing speedup factors."""
    lines = []
    lines.append("=" * 70)
    lines.append("Speedup Factor (Python time / Rust time)")
    lines.append("=" * 70)
    lines.append("")

    max_speedup = max(speedups)
    avg_speedup = sum(speedups) / len(speedups)

    for label, speedup in zip(labels, speedups, strict=False):
        bar_len = int((speedup / max_speedup) * max_width)
        lines.append(f"{label:20s} {'█' * bar_len} {speedup:5.2f}x")

    lines.append("")
    lines.append(f"{'Average speedup:':20s} {avg_speedup:5.2f}x")
    lines.append("=" * 70)

    return "\n".join(lines)


def extract_benchmark_data(results: list[dict[str, Any]]) -> dict[str, list]:
    """Extract benchmark data from results."""
    data = {
        "labels": [],
        "python_times": [],
        "rust_times": [],
        "python_memory": [],
        "rust_memory": [],
        "speedups": []
    }

    for result in results:
        if "example" not in result:
            continue

        example = result["example"]
        data["labels"].append(example)

        # Extract times (convert to ms)
        py_time = result.get("python_time_ms", 0)
        rs_time = result.get("rust_time_ms", 0)
        data["python_times"].append(py_time)
        data["rust_times"].append(rs_time)

        # Extract memory (in KB)
        py_mem = result.get("python_memory_kb", 0)
        rs_mem = result.get("rust_memory_kb", 0)
        data["python_memory"].append(py_mem)
        data["rust_memory"].append(rs_mem)

        # Calculate speedup
        speedup = py_time / rs_time if rs_time > 0 else 0
        data["speedups"].append(speedup)

    return data


def generate_summary_report(data: dict[str, list]) -> str:
    """Generate summary report with key statistics."""
    lines = []
    lines.append("=" * 70)
    lines.append("BENCHMARK SUMMARY REPORT")
    lines.append("=" * 70)
    lines.append("")

    if not data["labels"]:
        lines.append("No benchmark data available.")
        return "\n".join(lines)

    # Calculate averages
    avg_py_time = sum(data["python_times"]) / len(data["python_times"])
    avg_rs_time = sum(data["rust_times"]) / len(data["rust_times"])
    avg_speedup = sum(data["speedups"]) / len(data["speedups"])

    avg_py_mem = sum(data["python_memory"]) / len(data["python_memory"])
    avg_rs_mem = sum(data["rust_memory"]) / len(data["rust_memory"])
    avg_mem_reduction = ((avg_py_mem - avg_rs_mem) / avg_py_mem * 100) if avg_py_mem > 0 else 0

    lines.append(f"Benchmarks analyzed: {len(data['labels'])}")
    lines.append("")
    lines.append("EXECUTION TIME:")
    lines.append(f"  Average Python time: {avg_py_time:6.2f}ms")
    lines.append(f"  Average Rust time:   {avg_rs_time:6.2f}ms")
    lines.append(f"  Average speedup:     {avg_speedup:6.2f}x")
    lines.append("")
    lines.append("MEMORY USAGE:")
    lines.append(f"  Average Python memory: {avg_py_mem/1024:6.1f}MB")
    lines.append(f"  Average Rust memory:   {avg_rs_mem/1024:6.1f}MB")
    lines.append(f"  Average reduction:     {avg_mem_reduction:6.1f}%")
    lines.append("")
    lines.append("INDIVIDUAL RESULTS:")
    lines.append(f"{'Example':20s} {'Python':>10s} {'Rust':>10s} {'Speedup':>10s}")
    lines.append("-" * 70)

    for i, label in enumerate(data["labels"]):
        py_time = data["python_times"][i]
        rs_time = data["rust_times"][i]
        speedup = data["speedups"][i]
        lines.append(f"{label:20s} {py_time:8.2f}ms {rs_time:8.2f}ms {speedup:9.2f}x")

    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    """Main entry point."""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    results_dir = project_root / "benchmarks" / "reports"

    # Load benchmark results
    print(f"Loading benchmark results from {results_dir}...")
    results = load_benchmark_results(results_dir)

    if not results:
        print("No benchmark results found. Run 'make bench-all' first.")
        sys.exit(1)

    print(f"Loaded {len(results)} benchmark result(s).")
    print()

    # Extract data
    data = extract_benchmark_data(results)

    if not data["labels"]:
        print("No valid benchmark data found.")
        sys.exit(1)

    # Generate reports
    print(generate_summary_report(data))
    print()
    print(generate_speedup_chart(data["labels"], data["speedups"]))
    print()
    print(generate_ascii_chart(data["labels"], data["python_times"], data["rust_times"]))
    print()
    print(generate_memory_chart(data["labels"], data["python_memory"], data["rust_memory"]))


if __name__ == "__main__":
    main()
