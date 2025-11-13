#!/usr/bin/env python3
"""
PNG chart generator for benchmark results using matplotlib.

Generates professional-quality PNG charts for documentation.
"""

import json
import sys
from pathlib import Path
from typing import Any

try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print(
        "Warning: matplotlib not available. Install with: pip install matplotlib", file=sys.stderr
    )


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
        "speedups": [],
    }

    for result in results:
        if "example" not in result:
            continue

        example = result["example"]
        # Shorten label for better chart readability
        short_label = example.replace("example_", "")
        data["labels"].append(short_label)

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


def generate_execution_time_chart(data: dict[str, list], output_path: Path):
    """Generate grouped bar chart for execution times."""
    if not MATPLOTLIB_AVAILABLE:
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(data["labels"]))
    width = 0.35

    bars1 = ax.bar(x - width / 2, data["python_times"], width, label="Python", color="#3776ab")
    bars2 = ax.bar(x + width / 2, data["rust_times"], width, label="Rust", color="#ce422b")

    ax.set_xlabel("Example", fontsize=12, fontweight="bold")
    ax.set_ylabel("Execution Time (ms)", fontsize=12, fontweight="bold")
    ax.set_title("Execution Time Comparison: Python vs Rust", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(data["labels"], rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Generated: {output_path}")


def generate_speedup_chart(data: dict[str, list], output_path: Path):
    """Generate bar chart for speedup factors."""
    if not MATPLOTLIB_AVAILABLE:
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(data["labels"]))
    bars = ax.bar(x, data["speedups"], color="#2ecc71", edgecolor="black", linewidth=1.2)

    # Add average line
    avg_speedup = sum(data["speedups"]) / len(data["speedups"])
    ax.axhline(
        y=avg_speedup,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Average: {avg_speedup:.2f}x",
    )

    ax.set_xlabel("Example", fontsize=12, fontweight="bold")
    ax.set_ylabel("Speedup Factor (x)", fontsize=12, fontweight="bold")
    ax.set_title("Rust Speedup Over Python", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(data["labels"], rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.2f}x",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Generated: {output_path}")


def generate_memory_chart(data: dict[str, list], output_path: Path):
    """Generate grouped bar chart for memory usage."""
    if not MATPLOTLIB_AVAILABLE:
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    # Convert KB to MB
    python_mem_mb = [m / 1024 for m in data["python_memory"]]
    rust_mem_mb = [m / 1024 for m in data["rust_memory"]]

    x = np.arange(len(data["labels"]))
    width = 0.35

    bars1 = ax.bar(x - width / 2, python_mem_mb, width, label="Python", color="#3776ab")
    bars2 = ax.bar(x + width / 2, rust_mem_mb, width, label="Rust", color="#ce422b")

    ax.set_xlabel("Example", fontsize=12, fontweight="bold")
    ax.set_ylabel("Memory Usage (MB)", fontsize=12, fontweight="bold")
    ax.set_title("Memory Usage Comparison: Python vs Rust", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(data["labels"], rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.1f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Generated: {output_path}")


def generate_combined_chart(data: dict[str, list], output_path: Path):
    """Generate combined chart with multiple subplots."""
    if not MATPLOTLIB_AVAILABLE:
        return

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Benchmark Results: Python vs Rust", fontsize=16, fontweight="bold")

    x = np.arange(len(data["labels"]))
    width = 0.35

    # 1. Execution Time
    ax1.bar(x - width / 2, data["python_times"], width, label="Python", color="#3776ab")
    ax1.bar(x + width / 2, data["rust_times"], width, label="Rust", color="#ce422b")
    ax1.set_xlabel("Example")
    ax1.set_ylabel("Execution Time (ms)")
    ax1.set_title("Execution Time Comparison")
    ax1.set_xticks(x)
    ax1.set_xticklabels(data["labels"], rotation=45, ha="right")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    # 2. Speedup
    bars = ax2.bar(x, data["speedups"], color="#2ecc71", edgecolor="black", linewidth=1)
    avg_speedup = sum(data["speedups"]) / len(data["speedups"])
    ax2.axhline(
        y=avg_speedup, color="red", linestyle="--", linewidth=2, label=f"Avg: {avg_speedup:.2f}x"
    )
    ax2.set_xlabel("Example")
    ax2.set_ylabel("Speedup Factor (x)")
    ax2.set_title("Speedup Factor")
    ax2.set_xticks(x)
    ax2.set_xticklabels(data["labels"], rotation=45, ha="right")
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)
    for bar in bars:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.1f}x",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    # 3. Memory Usage
    python_mem_mb = [m / 1024 for m in data["python_memory"]]
    rust_mem_mb = [m / 1024 for m in data["rust_memory"]]
    ax3.bar(x - width / 2, python_mem_mb, width, label="Python", color="#3776ab")
    ax3.bar(x + width / 2, rust_mem_mb, width, label="Rust", color="#ce422b")
    ax3.set_xlabel("Example")
    ax3.set_ylabel("Memory Usage (MB)")
    ax3.set_title("Memory Usage Comparison")
    ax3.set_xticks(x)
    ax3.set_xticklabels(data["labels"], rotation=45, ha="right")
    ax3.legend()
    ax3.grid(axis="y", alpha=0.3)

    # 4. Summary Statistics
    ax4.axis("off")
    summary_text = f"""
SUMMARY STATISTICS

Benchmarks: {len(data["labels"])}

Execution Time:
  Avg Python: {sum(data["python_times"]) / len(data["python_times"]):.2f}ms
  Avg Rust:   {sum(data["rust_times"]) / len(data["rust_times"]):.2f}ms
  Avg Speedup: {avg_speedup:.2f}x

Memory Usage:
  Avg Python: {sum(python_mem_mb) / len(python_mem_mb):.1f}MB
  Avg Rust:   {sum(rust_mem_mb) / len(rust_mem_mb):.1f}MB
  Avg Reduction: {((sum(data["python_memory"]) - sum(data["rust_memory"])) / sum(data["python_memory"]) * 100):.1f}%

Peak Speedup: {max(data["speedups"]):.2f}x
Min Speedup:  {min(data["speedups"]):.2f}x
    """
    ax4.text(
        0.1,
        0.5,
        summary_text,
        fontsize=12,
        family="monospace",
        verticalalignment="center",
        bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5},
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Generated: {output_path}")


def main():
    """Main entry point."""
    if not MATPLOTLIB_AVAILABLE:
        print("❌ matplotlib is required for PNG chart generation.")
        print("Install with: pip install matplotlib")
        sys.exit(1)

    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    results_dir = project_root / "benchmarks" / "reports"
    output_dir = project_root / "benchmarks" / "charts"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

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

    # Generate charts
    print(f"\nGenerating PNG charts in {output_dir}...")
    generate_execution_time_chart(data, output_dir / "execution_time.png")
    generate_speedup_chart(data, output_dir / "speedup.png")
    generate_memory_chart(data, output_dir / "memory_usage.png")
    generate_combined_chart(data, output_dir / "combined.png")

    print(f"\n✅ All charts generated successfully in {output_dir}/")


if __name__ == "__main__":
    main()
