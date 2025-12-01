#!/usr/bin/env python3
"""Golden Traces Analyzer (GH-23) - CITL Oracle Training Seed.

Analyzes failing Rust compilations and selects candidates for human-verified
"Golden Traces" - high-quality (error → fix) patterns that seed the oracle.

Usage:
    python scripts/golden_traces_analyzer.py [OPTIONS]

Options:
    --json          Output JSON format
    --dry-run       Analyze only, don't write files
    --per-code N    Examples per error code (default: 10)
    -o, --output    Output file (default: data/golden_traces.json)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Top 5 error codes from README (targets for golden traces)
TOP_ERROR_CODES = ["E0308", "E0433", "E0599", "E0425", "E0277"]

# Error code descriptions
ERROR_DESCRIPTIONS = {
    "E0308": "Type mismatch",
    "E0433": "Failed to resolve (unresolved import)",
    "E0599": "Method not found",
    "E0425": "Cannot find value",
    "E0277": "Trait bound not satisfied",
    "E0412": "Cannot find type",
    "E0382": "Use of moved value",
    "E0507": "Cannot move out of borrowed content",
    "E0432": "Unresolved import",
    "E0015": "Calls in constants are limited",
}


@dataclass
class CompileError:
    """Represents a single compilation error."""

    code: str
    message: str
    file: str
    line: int
    example: str


@dataclass
class ErrorSummary:
    """Summary of errors by code."""

    code: str
    description: str
    count: int
    examples: list[str] = field(default_factory=list)


@dataclass
class GoldenTrace:
    """A candidate golden trace for oracle training."""

    example: str
    error_code: str
    error_message: str
    file: str | None = None
    line: int | None = None
    status: str = "pending"  # pending, verified, rejected
    fix_pattern: str | None = None
    rationale: str | None = None


def analyze_errors(examples_dir: Path) -> dict[str, ErrorSummary]:
    """Analyze all examples and categorize errors by code.

    Args:
        examples_dir: Path to examples directory

    Returns:
        Dict mapping error codes to ErrorSummary
    """
    errors: dict[str, ErrorSummary] = {}

    for cargo_toml in examples_dir.glob("example_*/Cargo.toml"):
        example_name = cargo_toml.parent.name

        try:
            result = subprocess.run(
                ["cargo", "check", "--manifest-path", str(cargo_toml)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parse error codes from stderr
            for match in re.finditer(r"error\[E(\d{4})\]", result.stderr):
                code = f"E{match.group(1)}"
                if code not in errors:
                    desc = ERROR_DESCRIPTIONS.get(code, "Unknown error")
                    errors[code] = ErrorSummary(
                        code=code, description=desc, count=0, examples=[]
                    )
                errors[code].count += 1
                if example_name not in errors[code].examples:
                    errors[code].examples.append(example_name)

        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue

    return errors


def select_golden_candidates(
    errors: dict[str, ErrorSummary], per_code: int = 10
) -> list[GoldenTrace]:
    """Select candidate examples for golden traces.

    Args:
        errors: Error summary by code
        per_code: Number of examples to select per error code

    Returns:
        List of GoldenTrace candidates
    """
    candidates = []

    # Prioritize TOP_ERROR_CODES
    for code in TOP_ERROR_CODES:
        if code in errors:
            summary = errors[code]
            # Select up to per_code examples
            for example in summary.examples[:per_code]:
                candidates.append(
                    GoldenTrace(
                        example=example,
                        error_code=code,
                        error_message=summary.description,
                        status="pending",
                    )
                )

    return candidates


def generate_golden_traces(candidates: list[GoldenTrace | dict]) -> dict[str, Any]:
    """Generate the golden traces JSON structure.

    Args:
        candidates: List of GoldenTrace objects or dicts

    Returns:
        Dict with version and traces
    """
    traces = []
    for c in candidates:
        if isinstance(c, dict):
            trace = {
                "example": c.get("example", ""),
                "error_code": c.get("error_code", ""),
                "error_message": c.get("error_msg", c.get("error_message", "")),
                "file": c.get("file"),
                "line": c.get("line"),
                "status": c.get("status", "pending"),
                "fix_pattern": c.get("fix_pattern"),
                "rationale": c.get("rationale"),
            }
        else:
            trace = asdict(c)
        traces.append(trace)

    return {
        "version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "description": "Golden traces for CITL oracle training (GH-23)",
        "target_codes": TOP_ERROR_CODES,
        "traces": traces,
        "stats": {
            "total": len(traces),
            "by_code": {},
        },
    }


def get_detailed_errors(example_dir: Path) -> list[CompileError]:
    """Get detailed error information for an example.

    Args:
        example_dir: Path to example directory

    Returns:
        List of CompileError objects
    """
    errors = []
    cargo_toml = example_dir / "Cargo.toml"

    if not cargo_toml.exists():
        return errors

    try:
        result = subprocess.run(
            ["cargo", "check", "--manifest-path", str(cargo_toml), "--message-format=json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        for line in result.stdout.splitlines():
            try:
                msg = json.loads(line)
                if msg.get("reason") == "compiler-message":
                    rendered = msg.get("message", {})
                    code_obj = rendered.get("code")
                    if code_obj and isinstance(code_obj, dict):
                        code = code_obj.get("code", "")
                        if code.startswith("E"):
                            spans = rendered.get("spans", [])
                            file_name = ""
                            line_num = 0
                            if spans:
                                file_name = spans[0].get("file_name", "")
                                line_num = spans[0].get("line_start", 0)

                            errors.append(
                                CompileError(
                                    code=code,
                                    message=rendered.get("message", ""),
                                    file=file_name,
                                    line=line_num,
                                    example=example_dir.name,
                                )
                            )
            except json.JSONDecodeError:
                continue

    except Exception:
        pass

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and generate golden traces for CITL oracle"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument(
        "--dry-run", action="store_true", help="Analyze only, don't write files"
    )
    parser.add_argument(
        "--per-code",
        type=int,
        default=10,
        help="Examples per error code (default: 10)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("data/golden_traces.json"),
        help="Output file",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    examples_dir = project_root / "examples"

    if args.verbose and not args.json:
        print("Analyzing compilation errors...", file=sys.stderr)

    # Analyze errors
    errors = analyze_errors(examples_dir)

    if not errors:
        if args.json:
            print(json.dumps({"error": "No compilation errors found", "traces": []}))
        else:
            print("No compilation errors found.")
        return 0

    # Select candidates
    candidates = select_golden_candidates(errors, per_code=args.per_code)

    # Enhance with detailed error info
    enhanced_candidates = []
    for candidate in candidates:
        example_dir = examples_dir / candidate.example
        detailed = get_detailed_errors(example_dir)
        # Find matching error
        for err in detailed:
            if err.code == candidate.error_code:
                candidate.file = err.file
                candidate.line = err.line
                candidate.error_message = err.message
                break
        enhanced_candidates.append(candidate)

    # Generate output
    output = generate_golden_traces(enhanced_candidates)

    # Update stats
    for trace in output["traces"]:
        code = trace["error_code"]
        output["stats"]["by_code"][code] = output["stats"]["by_code"].get(code, 0) + 1

    if args.json:
        print(json.dumps(output, indent=2, default=str))
    elif args.dry_run:
        print(f"Would generate {len(enhanced_candidates)} golden trace candidates:")
        print()
        for code in TOP_ERROR_CODES:
            count = output["stats"]["by_code"].get(code, 0)
            desc = ERROR_DESCRIPTIONS.get(code, "Unknown")
            print(f"  {code} ({desc}): {count} candidates")
        print()
        print(f"Total: {output['stats']['total']} traces")
    else:
        # Write to file
        output_path = project_root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2, default=str)
        print(f"Golden traces written to {output_path}")
        print(f"Total: {output['stats']['total']} traces")

    return 0


if __name__ == "__main__":
    sys.exit(main())
