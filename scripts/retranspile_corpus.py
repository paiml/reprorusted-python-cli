#!/usr/bin/python3
"""Re-transpile corpus with latest depyler and enrich with insights."""

import json
import subprocess
import sys
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq

# Tarantula suspiciousness scores
TARANTULA_SCORES = {
    "async_await": 0.946,
    "generator": 0.927,
    "walrus_operator": 0.850,
    "lambda": 0.783,
    "context_manager": 0.652,
    "class_definition": 0.612,
    "exception_handling": 0.577,
    "stdin_usage": 0.566,
    "list_comprehension": 0.538,
    "import_statement": 0.500,
    "function_definition": 0.500,
    "generator_expression": 0.890,
}

# Feature detection patterns
FEATURE_PATTERNS = {
    "async_await": ["async def", "await ", "asyncio"],
    "generator": ["yield ", "yield("],
    "lambda": ["lambda "],
    "context_manager": ["with ", "__enter__", "__exit__"],
    "class_definition": ["class "],
    "exception_handling": ["try:", "except ", "raise "],
    "stdin_usage": ["stdin", "input("],
    "walrus_operator": [":="],
    "decorator": ["@"],
    "multiprocessing": ["multiprocessing", "Pool", "Process"],
    "functools": ["functools", "partial", "reduce"],
    "eval_exec": ["eval(", "exec("],
}

def detect_features(code: str) -> list[str]:
    """Detect Python features in code."""
    features = []
    if not code:
        return features
    for feature, patterns in FEATURE_PATTERNS.items():
        if any(p in code for p in patterns):
            features.append(feature)
    return features

def compute_suspiciousness(features: list[str]) -> float:
    """Compute max suspiciousness from features."""
    if not features:
        return 0.0
    return max(TARANTULA_SCORES.get(f, 0.5) for f in features)

def transpile_python(python_path: Path, depyler_bin: Path) -> tuple[str | None, str | None]:
    """Transpile Python file to Rust using depyler."""
    try:
        result = subprocess.run(
            [str(depyler_bin), "transpile", str(python_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout, None
        return None, result.stderr
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except Exception as e:
        return None, str(e)

def main():
    project_root = Path(__file__).parent.parent
    examples_dir = project_root / "examples"
    depyler_bin = Path.home() / "src" / "depyler" / "target" / "release" / "depyler"

    if not depyler_bin.exists():
        print(f"Error: depyler binary not found at {depyler_bin}")
        sys.exit(1)

    print(f"Using depyler: {depyler_bin}")

    # Collect all examples
    records = []
    total = 0
    success = 0
    improved = 0

    # Load existing corpus to compare
    existing_path = project_root / "data" / "depyler_citl_corpus_uncompressed.parquet"
    existing_df = pq.read_table(existing_path).to_pandas()
    existing_rust = set(existing_df[existing_df['has_rust']]['category'].tolist())

    for example_dir in sorted(examples_dir.iterdir()):
        if not example_dir.is_dir() or not example_dir.name.startswith("example_"):
            continue

        # Find ALL Python files
        python_files = list(example_dir.glob("*.py"))
        if not python_files:
            continue

        category = example_dir.name.replace("example_", "")

        # Process each Python file in the example
        for python_file in sorted(python_files):
            python_code = python_file.read_text()

            total += 1

            # Transpile
            rust_code, error = transpile_python(python_file, depyler_bin)
            has_rust = rust_code is not None and len(rust_code.strip()) > 0

            if has_rust:
                success += 1
                if category not in existing_rust:
                    improved += 1
                    print(f"  NEW: {category} ({python_file.name})")

            # Detect features and compute suspiciousness
            features = detect_features(python_code)
            suspiciousness = compute_suspiciousness(features)

            records.append({
                "example_name": example_dir.name,
                "python_file": python_file.name,
                "python_code": python_code,
                "rust_code": rust_code or "",
                "has_rust": has_rust,
                "category": category,
                "python_lines": len(python_code.splitlines()),
                "rust_lines": len(rust_code.splitlines()) if rust_code else 0,
                "blocking_features": features,
                "suspiciousness": suspiciousness,
                "error": error[:500] if error else None,
            })

            if total % 50 == 0:
                print(f"  Processed {total}...")

    print(f"\nResults:")
    print(f"  Total: {total}")
    print(f"  Success: {success} ({100*success/total:.1f}%)")
    print(f"  Previous: {len(existing_rust)}")
    print(f"  Improved: {improved}")

    # Create Arrow table
    schema = pa.schema([
        ("example_name", pa.string()),
        ("python_file", pa.string()),
        ("python_code", pa.string()),
        ("rust_code", pa.string()),
        ("has_rust", pa.bool_()),
        ("category", pa.string()),
        ("python_lines", pa.int32()),
        ("rust_lines", pa.int32()),
        ("blocking_features", pa.list_(pa.string())),
        ("suspiciousness", pa.float32()),
        ("error", pa.string()),
    ])

    table = pa.Table.from_pydict({
        "example_name": [r["example_name"] for r in records],
        "python_file": [r["python_file"] for r in records],
        "python_code": [r["python_code"] for r in records],
        "rust_code": [r["rust_code"] for r in records],
        "has_rust": [r["has_rust"] for r in records],
        "category": [r["category"] for r in records],
        "python_lines": [r["python_lines"] for r in records],
        "rust_lines": [r["rust_lines"] for r in records],
        "blocking_features": [r["blocking_features"] for r in records],
        "suspiciousness": [r["suspiciousness"] for r in records],
        "error": [r["error"] for r in records],
    }, schema=schema)

    # Save enriched parquet
    output_path = project_root / "data" / "depyler_citl_corpus_v2.parquet"
    pq.write_table(table, output_path, compression="snappy")
    print(f"\nSaved enriched corpus to: {output_path}")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    main()
