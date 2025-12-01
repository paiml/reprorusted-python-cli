#!/usr/bin/env python3
"""Clippy Gate (GH-24) - Blocking quality gate for idiomatic Rust.

Runs cargo clippy on all examples and fails if warnings are present.
This ensures transpiled Rust is not just compilable but idiomatic.

Usage:
    python scripts/clippy_gate.py [OPTIONS]

Options:
    --strict        Fail on any clippy warning (exit 1)
    --json          Output JSON format
    --limit N       Limit to N examples (for testing)
    -v, --verbose   Show detailed output
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ClippyWarning:
    """A single clippy warning."""

    code: str
    message: str
    file: str
    line: int
    level: str = "warning"  # warning, error


@dataclass
class ClippyResult:
    """Result of running clippy on an example."""

    example: str
    passed: bool
    warnings: list[ClippyWarning] = field(default_factory=list)
    errors: list[ClippyWarning] = field(default_factory=list)
    compile_error: bool = False
    error_message: str | None = None


def run_clippy(example_dir: Path, pedantic: bool = False) -> ClippyResult:
    """Run clippy on a single example.

    Args:
        example_dir: Path to example directory
        pedantic: Use pedantic warnings

    Returns:
        ClippyResult with warnings/errors
    """
    example_name = example_dir.name
    cargo_toml = example_dir / "Cargo.toml"

    if not cargo_toml.exists():
        return ClippyResult(
            example=example_name,
            passed=False,
            compile_error=True,
            error_message="No Cargo.toml found",
        )

    cmd = ["cargo", "clippy", "--manifest-path", str(cargo_toml)]
    if pedantic:
        cmd.extend(["--", "-W", "clippy::pedantic"])
    else:
        cmd.extend(["--", "-D", "warnings"])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=example_dir,
        )

        warnings = []
        errors = []

        # Parse clippy output for warnings/errors
        for line in result.stderr.splitlines():
            # Match warning/error patterns
            if match := re.match(
                r"(warning|error)(?:\[([^\]]+)\])?: (.+)", line
            ):
                level = match.group(1)
                code = match.group(2) or ""
                msg = match.group(3)

                # Try to get file location from next lines
                file_info = ""
                line_num = 0

                warning = ClippyWarning(
                    code=code,
                    message=msg,
                    file=file_info,
                    line=line_num,
                    level=level,
                )

                if level == "warning":
                    warnings.append(warning)
                else:
                    errors.append(warning)

        # Check if compilation failed
        compile_error = result.returncode != 0 and any(
            "error[E" in line for line in result.stderr.splitlines()
        )

        passed = result.returncode == 0 and len(warnings) == 0

        return ClippyResult(
            example=example_name,
            passed=passed,
            warnings=warnings,
            errors=errors,
            compile_error=compile_error,
            error_message=result.stderr[:500] if compile_error else None,
        )

    except subprocess.TimeoutExpired:
        return ClippyResult(
            example=example_name,
            passed=False,
            compile_error=True,
            error_message="Timeout expired",
        )
    except Exception as e:
        return ClippyResult(
            example=example_name,
            passed=False,
            compile_error=True,
            error_message=str(e),
        )


def analyze_all(
    examples_dir: Path,
    limit: int | None = None,
    pedantic: bool = False,
    verbose: bool = False,
) -> dict[str, Any]:
    """Analyze all examples with clippy.

    Args:
        examples_dir: Path to examples directory
        limit: Limit number of examples to check
        pedantic: Use pedantic clippy warnings
        verbose: Print progress

    Returns:
        Summary dict with results
    """
    results = []
    example_dirs = sorted(examples_dir.glob("example_*/"))

    if limit:
        example_dirs = example_dirs[:limit]

    total = len(example_dirs)
    clippy_clean = 0
    clippy_warnings = 0
    compile_errors = 0

    for i, example_dir in enumerate(example_dirs, 1):
        cargo_toml = example_dir / "Cargo.toml"
        if not cargo_toml.exists():
            continue

        if verbose:
            print(f"[{i}/{total}] Checking {example_dir.name}...", file=sys.stderr)

        result = run_clippy(example_dir, pedantic=pedantic)
        results.append(result)

        if result.compile_error:
            compile_errors += 1
        elif result.passed:
            clippy_clean += 1
        else:
            clippy_warnings += 1

    return {
        "total": len(results),
        "clippy_clean": clippy_clean,
        "clippy_warnings": clippy_warnings,
        "compile_errors": compile_errors,
        "clean_rate": round(clippy_clean * 100 / len(results), 1) if results else 0,
        "results": results,
        "generated": datetime.now().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run clippy on all examples (GH-24 quality gate)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any clippy warning (exit 1)",
    )
    parser.add_argument(
        "--soft",
        action="store_true",
        help="Report warnings but don't fail (for progressive adoption)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output JSON format"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit to N examples (for testing)",
    )
    parser.add_argument(
        "--pedantic",
        action="store_true",
        help="Use clippy::pedantic warnings",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed output"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    examples_dir = project_root / "examples"

    summary = analyze_all(
        examples_dir,
        limit=args.limit,
        pedantic=args.pedantic,
        verbose=args.verbose,
    )

    # Convert results for JSON serialization
    if args.json:
        output = {
            "total": summary["total"],
            "clippy_clean": summary["clippy_clean"],
            "clippy_warnings": summary["clippy_warnings"],
            "compile_errors": summary["compile_errors"],
            "clean_rate": summary["clean_rate"],
            "generated": summary["generated"],
            "results": [
                {
                    "example": r.example,
                    "passed": r.passed,
                    "warning_count": len(r.warnings),
                    "error_count": len(r.errors),
                    "compile_error": r.compile_error,
                }
                for r in summary["results"]
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print()
        print("━" * 50)
        print("CLIPPY QUALITY GATE (GH-24)")
        print("━" * 50)
        print(f"Total examples:    {summary['total']}")
        print(f"Clippy clean:      {summary['clippy_clean']} ({summary['clean_rate']}%)")
        print(f"With warnings:     {summary['clippy_warnings']}")
        print(f"Compile errors:    {summary['compile_errors']}")
        print("━" * 50)

        if args.verbose and summary["clippy_warnings"] > 0:
            print()
            print("Examples with warnings:")
            for result in summary["results"]:
                if not result.passed and not result.compile_error:
                    print(f"  - {result.example}: {len(result.warnings)} warnings")

    # Exit with error if strict and warnings found
    if args.strict and summary["clippy_warnings"] > 0:
        if not args.json:
            print()
            print(f"FAILED: {summary['clippy_warnings']} examples have clippy warnings")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
