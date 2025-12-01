#!/usr/bin/env python3
"""Check that test files use [lib] crate type, not [[bin]].

This prevents regression of fix #195 where test_*.rs files should
be libraries (no main function) not binaries.
"""

import sys
from pathlib import Path


def check_test_lib_crates(examples_dir: Path) -> tuple[int, int, list[str]]:
    """Check all examples for correct crate type."""
    total = 0
    violations = []

    for example_dir in sorted(examples_dir.glob("example_*")):
        cargo_toml = example_dir / "Cargo.toml"
        if not cargo_toml.exists():
            continue

        # Check if directory has test files
        test_files = list(example_dir.glob("test_*.rs"))
        if not test_files:
            continue

        total += 1
        content = cargo_toml.read_text()

        # Test files should use [lib], not [[bin]]
        if "[[bin]]" in content and "[lib]" not in content:
            violations.append(example_dir.name)

    return total, len(violations), violations


def main() -> int:
    examples_dir = Path("examples")
    if not examples_dir.exists():
        print("Error: examples directory not found", file=sys.stderr)
        return 1

    total, fail_count, violations = check_test_lib_crates(examples_dir)

    print("━" * 50)
    print("TEST FILE CRATE TYPE CHECK")
    print("━" * 50)
    print(f"Checked: {total} examples with test files")
    print(f"Passed:  {total - fail_count}")
    print(f"Failed:  {fail_count}")
    print("━" * 50)

    if violations:
        print("\nVIOLATIONS (test files using [[bin]] instead of [lib]):")
        for v in violations[:10]:
            print(f"  - {v}")
        if len(violations) > 10:
            print(f"  ... and {len(violations) - 10} more")
        print("\nFix: depyler should generate [lib] for test_*.py files")
        return 1

    print("OK: All test files use [lib] crate type")
    return 0


if __name__ == "__main__":
    sys.exit(main())
