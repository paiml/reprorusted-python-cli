#!/usr/bin/env python3
"""Export CITL corpus to HuggingFace-compatible parquet format."""

import json
import os
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


def find_pairs(examples_dir: Path) -> list[dict]:
    """Find Python/Rust pairs in examples directory."""
    pairs = []

    for example_dir in sorted(examples_dir.iterdir()):
        if not example_dir.is_dir() or example_dir.name.startswith('.'):
            continue

        # Find Python files
        py_files = list(example_dir.glob("*.py"))
        rs_files = list(example_dir.glob("*.rs"))

        for py_file in py_files:
            python_code = py_file.read_text(errors='ignore')

            # Look for corresponding Rust file
            rs_name = py_file.stem + ".rs"
            rs_file = example_dir / rs_name
            rust_code = rs_file.read_text(errors='ignore') if rs_file.exists() else ""

            # Extract category from directory name
            category = example_dir.name.replace("example_", "")

            pairs.append({
                "example_name": example_dir.name,
                "python_file": py_file.name,
                "python_code": python_code,
                "rust_code": rust_code,
                "has_rust": bool(rust_code),
                "category": category,
                "python_lines": len(python_code.splitlines()),
                "rust_lines": len(rust_code.splitlines()) if rust_code else 0,
            })

    return pairs


def export_parquet(pairs: list[dict], output_path: Path):
    """Export pairs to parquet format."""
    # Create Arrow table
    table = pa.Table.from_pylist(pairs)

    # Write parquet
    pq.write_table(table, output_path, compression='zstd')
    print(f"Exported {len(pairs)} pairs to {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")


def main():
    examples_dir = Path(__file__).parent.parent / "examples"
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)

    pairs = find_pairs(examples_dir)

    # Stats
    with_rust = sum(1 for p in pairs if p["has_rust"])
    print(f"Found {len(pairs)} Python files")
    print(f"  With Rust: {with_rust}")
    print(f"  Without Rust: {len(pairs) - with_rust}")

    # Export
    export_parquet(pairs, output_dir / "depyler_citl_corpus.parquet")

    # Also export JSON for inspection
    with open(output_dir / "corpus_stats.json", "w") as f:
        json.dump({
            "total_pairs": len(pairs),
            "with_rust": with_rust,
            "categories": list(set(p["category"] for p in pairs)),
        }, f, indent=2)


if __name__ == "__main__":
    main()
