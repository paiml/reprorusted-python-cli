#!/usr/bin/env python3
"""
Markdown report generator for benchmark results.

Generates comprehensive markdown reports with tables and statistics.
"""

import json
import sys
from datetime import datetime
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


def extract_benchmark_data(results: list[dict[str, Any]]) -> dict[str, list]:
    """Extract benchmark data from results."""
    data = {
        "labels": [],
        "python_times": [],
        "rust_times": [],
        "python_memory": [],
        "rust_memory": [],
        "python_stddev": [],
        "rust_stddev": [],
        "speedups": [],
        "memory_reductions": []
    }

    for result in results:
        if "example" not in result:
            continue

        example = result["example"]
        data["labels"].append(example)

        # Extract times
        py_time = result.get("python_time_ms", 0)
        rs_time = result.get("rust_time_ms", 0)
        data["python_times"].append(py_time)
        data["rust_times"].append(rs_time)

        # Extract standard deviations
        py_stddev = result.get("python_stddev_ms", 0)
        rs_stddev = result.get("rust_stddev_ms", 0)
        data["python_stddev"].append(py_stddev)
        data["rust_stddev"].append(rs_stddev)

        # Extract memory
        py_mem = result.get("python_memory_kb", 0)
        rs_mem = result.get("rust_memory_kb", 0)
        data["python_memory"].append(py_mem)
        data["rust_memory"].append(rs_mem)

        # Calculate speedup
        speedup = py_time / rs_time if rs_time > 0 else 0
        data["speedups"].append(speedup)

        # Calculate memory reduction
        mem_reduction = ((py_mem - rs_mem) / py_mem * 100) if py_mem > 0 else 0
        data["memory_reductions"].append(mem_reduction)

    return data


def generate_markdown_report(data: dict[str, list]) -> str:
    """Generate comprehensive markdown report."""
    lines = []

    # Header
    lines.append("# Benchmark Results Report")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Benchmarks**: {len(data['labels'])} examples")
    lines.append("")

    # Summary statistics
    if data["labels"]:
        avg_py_time = sum(data["python_times"]) / len(data["python_times"])
        avg_rs_time = sum(data["rust_times"]) / len(data["rust_times"])
        avg_speedup = sum(data["speedups"]) / len(data["speedups"])
        avg_py_mem = sum(data["python_memory"]) / len(data["python_memory"])
        avg_rs_mem = sum(data["rust_memory"]) / len(data["rust_memory"])
        avg_mem_reduction = sum(data["memory_reductions"]) / len(data["memory_reductions"])

        lines.append("## Executive Summary")
        lines.append("")
        lines.append("| Metric | Python | Rust | Improvement |")
        lines.append("|--------|--------|------|-------------|")
        lines.append(f"| **Avg Execution Time** | {avg_py_time:.2f}ms | {avg_rs_time:.2f}ms | **{avg_speedup:.2f}x faster** |")
        lines.append(f"| **Avg Memory Usage** | {avg_py_mem/1024:.1f}MB | {avg_rs_mem/1024:.1f}MB | **{avg_mem_reduction:.1f}% less** |")
        lines.append(f"| **Peak Speedup** | - | - | **{max(data['speedups']):.2f}x** |")
        lines.append(f"| **Min Speedup** | - | - | **{min(data['speedups']):.2f}x** |")
        lines.append("")

    # Detailed results table
    lines.append("## Detailed Results")
    lines.append("")
    lines.append("### Execution Time")
    lines.append("")
    lines.append("| Example | Python (ms) | Rust (ms) | Speedup | Python σ | Rust σ |")
    lines.append("|---------|-------------|-----------|---------|----------|--------|")

    for i, label in enumerate(data["labels"]):
        py_time = data["python_times"][i]
        rs_time = data["rust_times"][i]
        speedup = data["speedups"][i]
        py_std = data["python_stddev"][i]
        rs_std = data["rust_stddev"][i]

        lines.append(f"| {label} | {py_time:.2f} | {rs_time:.2f} | **{speedup:.2f}x** | ±{py_std:.2f} | ±{rs_std:.2f} |")

    # Average row
    if data["labels"]:
        avg_py_time = sum(data["python_times"]) / len(data["python_times"])
        avg_rs_time = sum(data["rust_times"]) / len(data["rust_times"])
        avg_speedup = sum(data["speedups"]) / len(data["speedups"])
        avg_py_std = sum(data["python_stddev"]) / len(data["python_stddev"])
        avg_rs_std = sum(data["rust_stddev"]) / len(data["rust_stddev"])

        lines.append(f"| **Average** | **{avg_py_time:.2f}** | **{avg_rs_time:.2f}** | **{avg_speedup:.2f}x** | **±{avg_py_std:.2f}** | **±{avg_rs_std:.2f}** |")

    lines.append("")

    # Memory table
    lines.append("### Memory Usage")
    lines.append("")
    lines.append("| Example | Python (MB) | Rust (MB) | Reduction |")
    lines.append("|---------|-------------|-----------|-----------|")

    for i, label in enumerate(data["labels"]):
        py_mem = data["python_memory"][i] / 1024
        rs_mem = data["rust_memory"][i] / 1024
        reduction = data["memory_reductions"][i]

        lines.append(f"| {label} | {py_mem:.1f} | {rs_mem:.1f} | **{reduction:.1f}%** |")

    # Average row
    if data["labels"]:
        avg_py_mem = sum(data["python_memory"]) / len(data["python_memory"]) / 1024
        avg_rs_mem = sum(data["rust_memory"]) / len(data["rust_memory"]) / 1024
        avg_reduction = sum(data["memory_reductions"]) / len(data["memory_reductions"])

        lines.append(f"| **Average** | **{avg_py_mem:.1f}** | **{avg_rs_mem:.1f}** | **{avg_reduction:.1f}%** |")

    lines.append("")

    # Performance insights
    lines.append("## Performance Insights")
    lines.append("")

    if data["speedups"]:
        best_idx = data["speedups"].index(max(data["speedups"]))
        worst_idx = data["speedups"].index(min(data["speedups"]))

        lines.append(f"- **Best performing example**: {data['labels'][best_idx]} ({data['speedups'][best_idx]:.2f}x speedup)")
        lines.append(f"- **Slowest example**: {data['labels'][worst_idx]} ({data['speedups'][worst_idx]:.2f}x speedup)")
        lines.append(f"- **Consistency**: Speedups range from {min(data['speedups']):.2f}x to {max(data['speedups']):.2f}x")
        lines.append("")

    if data["memory_reductions"]:
        best_mem_idx = data["memory_reductions"].index(max(data["memory_reductions"]))
        lines.append(f"- **Best memory optimization**: {data['labels'][best_mem_idx]} ({data['memory_reductions'][best_mem_idx]:.1f}% reduction)")
        lines.append("")

    # Methodology
    lines.append("## Methodology")
    lines.append("")
    lines.append("- **Benchmarking tool**: bashrs bench v6.34.0")
    lines.append("- **Iterations**: 10 measured iterations per benchmark")
    lines.append("- **Warmup**: 3 warmup iterations (discarded)")
    lines.append("- **Statistical analysis**: Mean, standard deviation, outlier detection via MAD")
    lines.append("- **Memory profiling**: Peak RSS via `/usr/bin/time`")
    lines.append("")
    lines.append("See [BENCHMARKS.md](../BENCHMARKS.md) for full methodology and academic references.")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*Generated by reprorusted-python-cli benchmark framework*")
    lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point."""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    results_dir = project_root / "benchmarks" / "reports"
    output_file = project_root / "benchmarks" / "LATEST_RESULTS.md"

    # Load benchmark results
    print(f"Loading benchmark results from {results_dir}...")
    results = load_benchmark_results(results_dir)

    if not results:
        print("No benchmark results found. Run 'make bench-all' first.")
        sys.exit(1)

    print(f"Loaded {len(results)} benchmark result(s).")

    # Extract data
    data = extract_benchmark_data(results)

    if not data["labels"]:
        print("No valid benchmark data found.")
        sys.exit(1)

    # Generate report
    print("Generating markdown report...")
    report = generate_markdown_report(data)

    # Write report
    output_file.write_text(report)
    print(f"✅ Report generated: {output_file}")

    # Also output to stdout
    print()
    print(report)


if __name__ == "__main__":
    main()
