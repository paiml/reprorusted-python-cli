#!/usr/bin/env python3
"""HITL Sampler (GH-25) - Human-in-the-Loop review sampling.

Generates a stratified sample of examples for human review to identify
anti-patterns that automated tests cannot catch.

Usage:
    python scripts/hitl_sampler.py [OPTIONS]

Options:
    --sample-pct N   Sample percentage (default: 5)
    --json           Output JSON format
    --report         Summarize existing review findings
    --guide          Output review guide markdown
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Review checklist items
REVIEW_CHECKLIST = [
    {
        "id": "no_unsafe",
        "description": "No unnecessary `unsafe` blocks",
        "severity": "critical",
    },
    {
        "id": "minimal_cloning",
        "description": "Minimal cloning (prefer borrowing)",
        "severity": "high",
    },
    {
        "id": "idiomatic_error_handling",
        "description": "Idiomatic error handling (Result/Option, no unwrap in lib code)",
        "severity": "high",
    },
    {
        "id": "iterator_usage",
        "description": "Appropriate use of iterators (no explicit loops where iter works)",
        "severity": "medium",
    },
    {
        "id": "no_pythonisms",
        "description": "No Python-isms (Arc<Mutex<>> overuse, String everywhere)",
        "severity": "medium",
    },
    {
        "id": "proper_lifetimes",
        "description": "Proper lifetime annotations where needed",
        "severity": "medium",
    },
    {
        "id": "no_magic_numbers",
        "description": "No magic numbers (use constants)",
        "severity": "low",
    },
    {
        "id": "documentation",
        "description": "Public APIs have doc comments",
        "severity": "low",
    },
]

# Example categories for stratified sampling
CATEGORIES = [
    "cli",
    "async",
    "file_io",
    "math",
    "data_structures",
    "string_ops",
    "datetime",
    "error_handling",
    "other",
]


@dataclass
class ReviewItem:
    """A single item to review."""

    example: str
    category: str
    rust_file: str | None = None
    python_file: str | None = None
    review_status: str = "pending"  # pending, approved, rejected, needs_work
    checklist: dict[str, bool | None] = field(default_factory=dict)
    notes: str = ""
    reviewer: str | None = None
    reviewed_at: str | None = None


def categorize_example(example_name: str) -> str:
    """Determine category based on example name."""
    name = example_name.lower()

    if "async" in name:
        return "async"
    if any(x in name for x in ["file", "path", "io", "read", "write"]):
        return "file_io"
    if any(x in name for x in ["math", "numpy", "stat", "calc", "vector"]):
        return "math"
    if any(x in name for x in ["list", "dict", "set", "queue", "stack", "tree", "graph"]):
        return "data_structures"
    if any(x in name for x in ["string", "text", "parse", "format", "split"]):
        return "string_ops"
    if any(x in name for x in ["date", "time", "datetime", "timezone"]):
        return "datetime"
    if any(x in name for x in ["error", "exception", "result", "try"]):
        return "error_handling"
    if any(x in name for x in ["cli", "argparse", "flag", "command"]):
        return "cli"

    return "other"


def generate_sample(
    examples_dir: Path,
    sample_pct: int = 5,
    stratified: bool = True,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """Generate a sample of examples for review.

    Args:
        examples_dir: Path to examples directory
        sample_pct: Percentage to sample (default 5%)
        stratified: Use stratified sampling by category
        seed: Random seed for reproducibility

    Returns:
        List of ReviewItem dicts
    """
    if seed is not None:
        random.seed(seed)

    # Collect all examples with Rust files
    examples = []
    for example_dir in examples_dir.glob("example_*/"):
        rust_files = list(example_dir.glob("*.rs")) + list(
            example_dir.glob("src/*.rs")
        )
        if rust_files:
            examples.append(
                {
                    "name": example_dir.name,
                    "dir": example_dir,
                    "rust_files": rust_files,
                    "category": categorize_example(example_dir.name),
                }
            )

    if not examples:
        return []

    # Calculate sample size
    sample_size = max(1, int(len(examples) * sample_pct / 100))

    if stratified:
        # Group by category
        by_category: dict[str, list] = {}
        for ex in examples:
            cat = ex["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(ex)

        # Sample proportionally from each category
        sampled = []
        remaining = sample_size
        categories = list(by_category.keys())

        for cat in categories:
            cat_examples = by_category[cat]
            # Proportional allocation
            cat_sample_size = max(1, int(len(cat_examples) * sample_pct / 100))
            cat_sample_size = min(cat_sample_size, len(cat_examples), remaining)

            if cat_sample_size > 0:
                sampled.extend(random.sample(cat_examples, cat_sample_size))
                remaining -= cat_sample_size

            if remaining <= 0:
                break
    else:
        sampled = random.sample(examples, min(sample_size, len(examples)))

    # Convert to ReviewItems
    result = []
    for ex in sampled:
        rust_file = ex["rust_files"][0].name if ex["rust_files"] else None
        python_files = list(ex["dir"].glob("*.py"))
        python_file = python_files[0].name if python_files else None

        item = ReviewItem(
            example=ex["name"],
            category=ex["category"],
            rust_file=rust_file,
            python_file=python_file,
            checklist={check["id"]: None for check in REVIEW_CHECKLIST},
        )
        result.append(asdict(item))

    return result


def generate_review_guide() -> str:
    """Generate the HITL review guide markdown."""
    guide = """# HITL Review Guide (GH-25)

## Overview

This guide describes the Human-in-the-Loop (HITL) review process for the
reprorusted-python-cli corpus. Senior Rust engineers review a 5% sample
to identify anti-patterns that automated tests cannot catch.

## Review Checklist

Each example should be evaluated against the following criteria:

"""
    for check in REVIEW_CHECKLIST:
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
        }.get(check["severity"], "⚪")

        guide += f"### {severity_emoji} {check['id']}\n"
        guide += f"**Severity:** {check['severity'].upper()}\n\n"
        guide += f"{check['description']}\n\n"

    guide += """## Review Process

1. **Generate Sample**: `make corpus-hitl-sample`
2. **Review Each Example**: Check against the checklist above
3. **Document Findings**: Update `data/hitl_reviews/YYYY-QN-review.json`
4. **Report Summary**: `make corpus-hitl-report`

## Status Values

- `pending`: Not yet reviewed
- `approved`: Passes all critical/high checks
- `needs_work`: Has issues that need fixing
- `rejected`: Has critical anti-patterns

## Quarterly Schedule

- Q1: January-March
- Q2: April-June
- Q3: July-September
- Q4: October-December

---
Generated by `hitl_sampler.py` (GH-25)
"""
    return guide


def load_existing_reviews(reviews_dir: Path) -> list[dict]:
    """Load existing review files."""
    reviews = []
    for review_file in reviews_dir.glob("*.json"):
        with open(review_file) as f:
            data = json.load(f)
            if "sample" in data:
                reviews.extend(data["sample"])
    return reviews


def generate_report(reviews_dir: Path) -> dict[str, Any]:
    """Generate summary report of review findings."""
    reviews = load_existing_reviews(reviews_dir)

    if not reviews:
        return {"error": "No reviews found", "total": 0}

    status_counts = {"pending": 0, "approved": 0, "needs_work": 0, "rejected": 0}
    check_failures: dict[str, int] = {}

    for review in reviews:
        status = review.get("review_status", "pending")
        status_counts[status] = status_counts.get(status, 0) + 1

        checklist = review.get("checklist", {})
        for check_id, passed in checklist.items():
            if passed is False:
                check_failures[check_id] = check_failures.get(check_id, 0) + 1

    return {
        "total_reviewed": len(reviews),
        "status_breakdown": status_counts,
        "approval_rate": round(
            status_counts["approved"] * 100 / len(reviews), 1
        ) if reviews else 0,
        "top_failures": sorted(
            check_failures.items(), key=lambda x: x[1], reverse=True
        )[:5],
        "generated": datetime.now().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate HITL review sample (GH-25)"
    )
    parser.add_argument(
        "--sample-pct",
        type=int,
        default=5,
        help="Sample percentage (default: 5)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output JSON format"
    )
    parser.add_argument(
        "--report", action="store_true", help="Summarize existing review findings"
    )
    parser.add_argument(
        "--guide", action="store_true", help="Output review guide markdown"
    )
    parser.add_argument(
        "--seed", type=int, help="Random seed for reproducibility"
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="Output file path"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    examples_dir = project_root / "examples"
    reviews_dir = project_root / "data" / "hitl_reviews"

    if args.guide:
        print(generate_review_guide())
        return 0

    if args.report:
        report = generate_report(reviews_dir)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print()
            print("━" * 50)
            print("HITL REVIEW SUMMARY")
            print("━" * 50)
            print(f"Total reviewed: {report.get('total_reviewed', 0)}")
            print(f"Approval rate: {report.get('approval_rate', 0)}%")
            print()
            print("Status breakdown:")
            for status, count in report.get("status_breakdown", {}).items():
                print(f"  {status}: {count}")
            print("━" * 50)
        return 0

    # Generate sample
    sample = generate_sample(
        examples_dir,
        sample_pct=args.sample_pct,
        seed=args.seed,
    )

    output = {
        "version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "sample_pct": args.sample_pct,
        "checklist": REVIEW_CHECKLIST,
        "sample": sample,
    }

    if args.json:
        print(json.dumps(output, indent=2, default=str))
    elif args.output:
        reviews_dir.mkdir(parents=True, exist_ok=True)
        output_path = args.output
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2, default=str)
        print(f"Sample written to {output_path}")
        print(f"Total examples: {len(sample)}")
    else:
        # Default: write to data/hitl_reviews/
        reviews_dir.mkdir(parents=True, exist_ok=True)
        quarter = f"Q{(datetime.now().month - 1) // 3 + 1}"
        filename = f"{datetime.now().year}-{quarter}-sample.json"
        output_path = reviews_dir / filename

        with open(output_path, "w") as f:
            json.dump(output, f, indent=2, default=str)

        print(f"Sample written to {output_path}")
        print(f"Total examples: {len(sample)}")
        print()
        print("Categories sampled:")
        categories = {}
        for item in sample:
            cat = item["category"]
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
