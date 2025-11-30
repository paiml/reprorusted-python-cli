#!/usr/bin/env python3
"""Category Diff Tracking (GH-16).

Shows which categories changed status after depyler fixes.

Usage:
    python scripts/category_diff.py baseline.parquet current.parquet
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


@dataclass
class CategoryChanges:
    """Tracks category status changes."""

    now_passing: list[str] = field(default_factory=list)
    regressed: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)

    @property
    def net_change(self) -> int:
        """Net change in passing categories."""
        return len(self.now_passing) - len(self.regressed)

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps({
            "now_passing": self.now_passing,
            "regressed": self.regressed,
            "unchanged": self.unchanged,
            "net_change": self.net_change,
        }, indent=2)


def get_category_success(df: pd.DataFrame) -> dict[str, bool]:
    """Get success status per category (any success = passing)."""
    if "category" not in df.columns or "has_rust" not in df.columns:
        return {}
    return df.groupby("category")["has_rust"].any().to_dict()


def compare_category_success(baseline_df: pd.DataFrame, current_df: pd.DataFrame) -> CategoryChanges:
    """Compare category success between two corpus versions."""
    baseline_status = get_category_success(baseline_df)
    current_status = get_category_success(current_df)

    all_categories = set(baseline_status.keys()) | set(current_status.keys())

    now_passing = []
    regressed = []
    unchanged = []

    for cat in sorted(all_categories):
        was_passing = baseline_status.get(cat, False)
        is_passing = current_status.get(cat, False)

        if not was_passing and is_passing:
            now_passing.append(cat)
        elif was_passing and not is_passing:
            regressed.append(cat)
        else:
            unchanged.append(cat)

    return CategoryChanges(
        now_passing=now_passing,
        regressed=regressed,
        unchanged=unchanged,
    )


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: python scripts/category_diff.py baseline.parquet current.parquet")
        sys.exit(1)

    baseline_path = Path(sys.argv[1])
    current_path = Path(sys.argv[2])

    baseline_df = pq.read_table(baseline_path).to_pandas()
    current_df = pq.read_table(current_path).to_pandas()

    changes = compare_category_success(baseline_df, current_df)

    # Output for shell script parsing
    if changes.now_passing:
        print("NOW_PASSING:" + ",".join(changes.now_passing))
    else:
        print("NOW_PASSING:")

    if changes.regressed:
        print("REGRESSED:" + ",".join(changes.regressed))
    else:
        print("REGRESSED:")

    print(f"NET_CHANGE:{changes.net_change}")


if __name__ == "__main__":
    main()
