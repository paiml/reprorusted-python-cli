#!/usr/bin/env python3
"""Zero-Success Category Analyzer for Depyler Prioritization (GH-12).

Analyzes failing categories to help depyler team prioritize.

Usage:
    python scripts/zero_success_analyzer.py data/labeled_corpus.parquet \
        --output reports/zero_success_analysis.json
    python scripts/zero_success_analyzer.py corpus.parquet --for-depyler
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

# Feature detection patterns
FEATURE_PATTERNS = {
    "async_await": [r"async def", r"await ", r"asyncio"],
    "generator": [r"yield ", r"yield\("],
    "lambda": [r"lambda "],
    "context_manager": [r"with ", r"__enter__", r"__exit__"],
    "class_definition": [r"class "],
    "exception_handling": [r"try:", r"except ", r"raise "],
    "walrus_operator": [r":="],
    "decorator": [r"@\w+"],
    "comprehension": [r"\[.+for.+in.+\]", r"\{.+for.+in.+\}"],
}

# Tarantula scores
TARANTULA_SCORES = {
    "async_await": 0.946,
    "generator": 0.927,
    "walrus_operator": 0.850,
    "lambda": 0.783,
    "context_manager": 0.652,
    "class_definition": 0.612,
    "exception_handling": 0.577,
}


@dataclass
class CategoryAnalysis:
    """Analysis of a zero-success category."""

    category: str
    blocking_features: list[str]
    sample_code: str
    recommendation: str
    group: str = ""
    impact_score: float = 0.0


def group_categories(categories: list[str]) -> dict[str, list[str]]:
    """Group categories by prefix pattern."""
    groups: dict[str, list[str]] = {}

    prefixes = ["async", "func", "state", "mem", "serial", "typed", "thread"]

    for cat in categories:
        matched = False
        for prefix in prefixes:
            if cat.startswith(f"{prefix}_"):
                if prefix not in groups:
                    groups[prefix] = []
                groups[prefix].append(cat)
                matched = True
                break
        if not matched:
            if "other" not in groups:
                groups["other"] = []
            groups["other"].append(cat)

    return groups


def detect_features(code: str) -> list[str]:
    """Detect blocking features in code."""
    features = []
    if not code:
        return features
    for feature, patterns in FEATURE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, code):
                features.append(feature)
                break
    return features


def generate_depyler_recommendations(df: pd.DataFrame) -> list[dict]:
    """Generate prioritized recommendations for depyler team."""
    # Count blocking features across zero-success categories
    feature_counts: dict[str, int] = {}
    zero_success_cats = df.groupby("category")["has_rust"].apply(lambda x: x.sum() == 0)
    zero_cats = zero_success_cats[zero_success_cats].index.tolist()

    for cat in zero_cats:
        cat_df = df[df["category"] == cat]
        for _, row in cat_df.iterrows():
            code = row.get("python_code", "") or ""
            features = detect_features(code)
            for feat in features:
                feature_counts[feat] = feature_counts.get(feat, 0) + 1

    # Build recommendations sorted by impact
    recommendations = []
    for feat, count in sorted(feature_counts.items(), key=lambda x: -x[1]):
        score = TARANTULA_SCORES.get(feat, 0.5)
        impact = count * score
        recommendations.append({
            "feature": feat,
            "priority": "HIGH" if score > 0.7 else "MEDIUM",
            "affected_categories": count,
            "suspiciousness": score,
            "impact": round(impact, 2),
            "action": f"Add support for '{feat}' pattern",
        })

    return sorted(recommendations, key=lambda x: -x["impact"])


class ZeroSuccessAnalyzer:
    """Analyze zero-success categories."""

    def __init__(self):
        """Initialize analyzer."""
        self._analyses: list[CategoryAnalysis] = []

    def find_zero_success(self, df: pd.DataFrame) -> list[str]:
        """Find categories with 0% success rate."""
        if "has_rust" not in df.columns or "category" not in df.columns:
            return []

        cat_success = df.groupby("category")["has_rust"].agg(["sum", "count"])
        zero_success = cat_success[cat_success["sum"] == 0].index.tolist()
        return zero_success

    def analyze(self, df: pd.DataFrame) -> list[CategoryAnalysis]:
        """Analyze all zero-success categories."""
        zero_cats = self.find_zero_success(df)
        groups = group_categories(zero_cats)

        analyses = []
        for cat in zero_cats:
            cat_df = df[df["category"] == cat]
            sample_code = ""
            all_features: set[str] = set()

            for _, row in cat_df.iterrows():
                code = row.get("python_code", "") or ""
                if code and not sample_code:
                    sample_code = code[:200]
                features = detect_features(code)
                all_features.update(features)

            # Find group
            group = "other"
            for g, cats in groups.items():
                if cat in cats:
                    group = g
                    break

            # Calculate impact
            blocking = list(all_features)
            impact = sum(TARANTULA_SCORES.get(f, 0.5) for f in blocking)

            # Generate recommendation
            if blocking:
                top_blocker = max(blocking, key=lambda f: TARANTULA_SCORES.get(f, 0))
                rec = f"Implement '{top_blocker}' support to unblock this category"
            else:
                rec = "Investigate specific failure patterns"

            analyses.append(CategoryAnalysis(
                category=cat,
                blocking_features=blocking,
                sample_code=sample_code,
                recommendation=rec,
                group=group,
                impact_score=round(impact, 2),
            ))

        self._analyses = sorted(analyses, key=lambda a: -a.impact_score)
        return self._analyses

    def to_json(self) -> str:
        """Serialize analyses to JSON."""
        return json.dumps({
            "total_zero_success": len(self._analyses),
            "by_group": self._group_summary(),
            "analyses": [
                {
                    "category": a.category,
                    "group": a.group,
                    "blocking_features": a.blocking_features,
                    "impact_score": a.impact_score,
                    "recommendation": a.recommendation,
                }
                for a in self._analyses
            ],
        }, indent=2)

    def _group_summary(self) -> dict:
        """Summarize by group."""
        groups: dict[str, int] = {}
        for a in self._analyses:
            groups[a.group] = groups.get(a.group, 0) + 1
        return groups


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze zero-success categories")
    parser.add_argument("input", type=Path, help="Input parquet file")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file")
    parser.add_argument("--for-depyler", action="store_true", help="Generate depyler recs")
    args = parser.parse_args()

    print(f"Loading corpus from {args.input}...")
    df = pq.read_table(args.input).to_pandas()

    analyzer = ZeroSuccessAnalyzer()
    analyses = analyzer.analyze(df)

    print(f"\nFound {len(analyses)} zero-success categories\n")

    if args.for_depyler:
        recs = generate_depyler_recommendations(df)
        print("=== DEPYLER RECOMMENDATIONS ===\n")
        for i, rec in enumerate(recs[:10], 1):
            print(f"{i}. [{rec['priority']}] {rec['feature']}")
            print(f"   Impact: {rec['impact']} | Affected: {rec['affected_categories']} cats")
    else:
        print(analyzer.to_json())

    if args.output:
        with open(args.output, "w") as f:
            f.write(analyzer.to_json())
        print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
