#!/usr/bin/env python3
"""Corpus Quality Report Generator (GH-11).

Generates comprehensive quality reports for tracking corpus health.

Usage:
    python scripts/corpus_quality_report.py data/labeled_corpus.parquet \
        --output reports/quality_report.json
    python scripts/corpus_quality_report.py corpus.parquet --markdown
    python scripts/corpus_quality_report.py corpus.parquet --compare previous.json
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

# Tarantula scores for prioritization
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
class QualityReport:
    """Quality report for corpus."""

    metrics: dict
    blocking_patterns: list
    recommendations: list
    generated: str = field(default_factory=lambda: datetime.now().isoformat())
    corpus_version: str = "2.0"

    def to_json(self) -> str:
        """Serialize report to JSON."""
        return json.dumps({
            "generated": self.generated,
            "corpus_version": self.corpus_version,
            "metrics": self.metrics,
            "blocking_patterns": self.blocking_patterns,
            "recommendations": self.recommendations,
        }, indent=2)

    def to_markdown(self) -> str:
        """Generate markdown summary."""
        lines = [
            "# Corpus Quality Report",
            f"\nGenerated: {self.generated}",
            "\n## Key Metrics",
            "\n| Metric | Value |",
            "|--------|-------|",
        ]
        for key, value in self.metrics.items():
            if isinstance(value, float):
                lines.append(f"| {key} | {value:.1f} |")
            elif isinstance(value, dict):
                lines.append(f"| {key} | (see breakdown) |")
            else:
                lines.append(f"| {key} | {value} |")

        lines.append("\n## Risk Distribution")
        if "risk_distribution" in self.metrics:
            for label, count in self.metrics["risk_distribution"].items():
                lines.append(f"- **{label}**: {count}")

        lines.append("\n## Top Blocking Patterns")
        for bp in self.blocking_patterns[:5]:
            lines.append(f"- {bp['pattern']}: {bp['suspiciousness']:.3f} ({bp['affected_count']} affected)")

        lines.append("\n## Recommendations")
        for i, rec in enumerate(self.recommendations[:5], 1):
            lines.append(f"{i}. [{rec['priority']}] {rec['action']}")

        return "\n".join(lines)


def generate_recommendations(df: pd.DataFrame) -> list[dict]:
    """Generate actionable recommendations from corpus analysis."""
    recommendations = []

    # Check success rate
    if "has_rust" in df.columns:
        success_rate = df["has_rust"].mean() * 100
        if success_rate < 80:
            recommendations.append({
                "priority": "HIGH",
                "action": f"Improve success rate from {success_rate:.1f}% to 80%+",
                "impact": "Major corpus quality improvement",
            })

    # Check HIGH_RISK representation
    if "risk_label" in df.columns:
        high_risk_pct = (df["risk_label"] == "HIGH_RISK").mean() * 100
        if high_risk_pct < 20:
            recommendations.append({
                "priority": "MEDIUM",
                "action": f"Increase HIGH_RISK examples from {high_risk_pct:.1f}% to 20%+",
                "impact": "Better training data balance",
            })

    # Recommend top Tarantula patterns
    for pattern, score in sorted(TARANTULA_SCORES.items(), key=lambda x: -x[1])[:3]:
        recommendations.append({
            "priority": "HIGH" if score > 0.8 else "MEDIUM",
            "action": f"Add depyler support for '{pattern}' (suspiciousness: {score})",
            "impact": f"Reduces failure correlation by {score*100:.0f}%",
        })

    return recommendations


def compare_reports(old: QualityReport, new: QualityReport) -> dict:
    """Compare two reports and return deltas."""
    delta = {}

    old_success = old.metrics.get("success_rate", 0)
    new_success = new.metrics.get("success_rate", 0)
    delta["success_rate_delta"] = new_success - old_success

    old_total = old.metrics.get("total_samples", 0)
    new_total = new.metrics.get("total_samples", 0)
    delta["total_samples_delta"] = new_total - old_total

    delta["improved"] = delta["success_rate_delta"] > 0

    return delta


class QualityReportGenerator:
    """Generate quality reports from corpus data."""

    def __init__(self):
        """Initialize generator."""
        pass

    def generate(self, df: pd.DataFrame) -> QualityReport:
        """Generate quality report from DataFrame."""
        metrics = self._compute_metrics(df)
        blocking = self._find_blocking_patterns(df)
        recs = generate_recommendations(df)

        return QualityReport(
            metrics=metrics,
            blocking_patterns=blocking,
            recommendations=recs,
        )

    def _compute_metrics(self, df: pd.DataFrame) -> dict:
        """Compute quality metrics."""
        metrics = {
            "total_samples": len(df),
        }

        if "has_rust" in df.columns:
            metrics["success_rate"] = round(df["has_rust"].mean() * 100, 1)
            metrics["successful_count"] = int(df["has_rust"].sum())

        if "risk_label" in df.columns:
            metrics["risk_distribution"] = df["risk_label"].value_counts().to_dict()

        if "confidence" in df.columns:
            metrics["avg_confidence"] = round(df["confidence"].mean(), 3)

        return metrics

    def _find_blocking_patterns(self, df: pd.DataFrame) -> list[dict]:
        """Find patterns blocking transpilation."""
        blocking = []

        # Use Tarantula scores as proxy for blocking patterns
        for pattern, score in sorted(TARANTULA_SCORES.items(), key=lambda x: -x[1]):
            blocking.append({
                "pattern": pattern,
                "suspiciousness": score,
                "affected_count": int(len(df) * (1 - df.get("has_rust", pd.Series([True]*len(df))).mean()) * score),
            })

        return blocking


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate corpus quality report")
    parser.add_argument("input", type=Path, help="Input parquet file")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file")
    parser.add_argument("--markdown", "-m", action="store_true", help="Output markdown")
    parser.add_argument("--compare", type=Path, help="Compare with previous report")
    args = parser.parse_args()

    print(f"Loading corpus from {args.input}...")
    df = pq.read_table(args.input).to_pandas()
    print(f"Loaded {len(df)} samples")

    gen = QualityReportGenerator()
    report = gen.generate(df)

    if args.markdown:
        print(report.to_markdown())
    else:
        print(report.to_json())

    if args.output:
        with open(args.output, "w") as f:
            f.write(report.to_json())
        print(f"\nSaved report to {args.output}")


if __name__ == "__main__":
    main()
