#!/usr/bin/env python3
"""Measure single-shot compile rate for transpiled Rust code.

Counts both [[bin]] and [lib] crate types that compile with cargo check.
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import tomllib


@dataclass
class CrateInfo:
    """Information about a Rust crate."""

    path: Path
    name: str
    crate_type: Literal["bin", "lib"]
    compiles: bool = False
    error: str | None = None


@dataclass
class CompileResults:
    """Results of compile rate measurement."""

    bins_total: int = 0
    bins_success: int = 0
    libs_total: int = 0
    libs_success: int = 0
    crates: list[CrateInfo] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.bins_total + self.libs_total

    @property
    def success(self) -> int:
        return self.bins_success + self.libs_success

    @property
    def rate(self) -> float:
        return (self.success / self.total * 100) if self.total > 0 else 0.0

    @property
    def bins_rate(self) -> float:
        return (
            (self.bins_success / self.bins_total * 100) if self.bins_total > 0 else 0.0
        )

    @property
    def libs_rate(self) -> float:
        return (
            (self.libs_success / self.libs_total * 100) if self.libs_total > 0 else 0.0
        )


def parse_cargo_toml(cargo_path: Path) -> tuple[str | None, Literal["bin", "lib"] | None]:
    """Parse Cargo.toml to get crate name and type."""
    try:
        with open(cargo_path, "rb") as f:
            cargo = tomllib.load(f)

        # Check for [[bin]] section (non-test binaries)
        if "bin" in cargo:
            for bin_entry in cargo["bin"]:
                name = bin_entry.get("name", "")
                if name and not name.startswith("test_"):
                    return name, "bin"

        # Check for [lib] section
        if "lib" in cargo:
            name = cargo.get("package", {}).get("name", "")
            return name, "lib"

        return None, None
    except Exception:
        return None, None


def check_compiles(cargo_path: Path, name: str, crate_type: Literal["bin", "lib"]) -> tuple[bool, str | None]:
    """Check if a crate compiles with cargo check."""
    try:
        if crate_type == "bin":
            cmd = ["cargo", "check", "--manifest-path", str(cargo_path), "--bin", name]
        else:
            cmd = ["cargo", "check", "--manifest-path", str(cargo_path), "--lib"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return True, None
        # Extract first error
        for line in result.stderr.split("\n"):
            if line.startswith("error[E"):
                return False, line
        return False, "Unknown error"
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def measure_compile_rate(examples_dir: Path, verbose: bool = False) -> CompileResults:
    """Measure compile rate for all examples."""
    results = CompileResults()

    example_dirs = sorted(examples_dir.glob("example_*"))
    for example_dir in example_dirs:
        cargo_path = example_dir / "Cargo.toml"
        if not cargo_path.exists():
            continue

        name, crate_type = parse_cargo_toml(cargo_path)
        if not name or not crate_type:
            continue

        compiles, error = check_compiles(cargo_path, name, crate_type)

        crate_info = CrateInfo(
            path=example_dir,
            name=name,
            crate_type=crate_type,
            compiles=compiles,
            error=error,
        )
        results.crates.append(crate_info)

        if crate_type == "bin":
            results.bins_total += 1
            if compiles:
                results.bins_success += 1
        else:
            results.libs_total += 1
            if compiles:
                results.libs_success += 1

        if verbose:
            status = "✓" if compiles else "✗"
            print(f"  {status} {example_dir.name} ({crate_type})")

    return results


def print_summary(results: CompileResults) -> None:
    """Print summary in box format."""
    print("━" * 51)
    print("SINGLE-SHOT COMPILE RATE")
    print("━" * 51)
    print(f"Binaries:   {results.bins_success:3} / {results.bins_total:3} ({results.bins_rate:5.1f}%)")
    print(f"Libraries:  {results.libs_success:3} / {results.libs_total:3} ({results.libs_rate:5.1f}%)")
    print("━" * 51)
    print(f"TOTAL:      {results.success:3} / {results.total:3} ({results.rate:5.1f}%)")
    print("━" * 51)


def print_json(results: CompileResults) -> None:
    """Print results as JSON."""
    data = {
        "bins_total": results.bins_total,
        "bins_success": results.bins_success,
        "bins_rate": round(results.bins_rate, 1),
        "libs_total": results.libs_total,
        "libs_success": results.libs_success,
        "libs_rate": round(results.libs_rate, 1),
        "total": results.total,
        "success": results.success,
        "rate": round(results.rate, 1),
        "failing": [
            {
                "name": c.name,
                "type": c.crate_type,
                "error": c.error,
            }
            for c in results.crates
            if not c.compiles
        ],
    }
    print(json.dumps(data, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure single-shot compile rate")
    parser.add_argument(
        "-d", "--dir",
        type=Path,
        default=Path("examples"),
        help="Examples directory (default: examples)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show per-crate results",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--target",
        type=float,
        default=80.0,
        help="Target compile rate (default: 80%%)",
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Exit with error if below target rate",
    )
    args = parser.parse_args()

    if not args.dir.exists():
        print(f"Error: Directory {args.dir} not found", file=sys.stderr)
        return 1

    results = measure_compile_rate(args.dir, verbose=args.verbose)

    if args.json:
        print_json(results)
    else:
        print_summary(results)

        # Show progress toward target
        if results.rate < args.target:
            needed = int((args.target / 100) * results.total) - results.success
            print(f"Gap to {args.target:.0f}%: +{needed} files needed")

    # Only fail if --fail-below-target is set
    if hasattr(args, 'fail') and args.fail and results.rate < args.target:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
