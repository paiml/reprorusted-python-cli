#!/usr/bin/env python3
"""Apply Weak Supervision Labels to CITL Corpus (GH-9).

Creates training-ready labeled data using Tarantula-weighted labeling functions.

Usage:
    python scripts/label_corpus.py data/depyler_citl_corpus_v2.parquet \
        --output data/labeled_corpus.parquet
    python scripts/label_corpus.py data/corpus.parquet --stats
    python scripts/label_corpus.py corpus.parquet --threshold 0.7
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

# Add scripts directory to path for sibling imports
sys.path.insert(0, str(Path(__file__).parent))
from weak_supervision import WeakSupervisionLabeler


def load_corpus(path: Path) -> pd.DataFrame:
    """Load corpus from parquet file."""
    return pq.read_table(path).to_pandas()


def save_labeled_corpus(df: pd.DataFrame, path: Path) -> None:
    """Save labeled corpus to parquet file."""
    df.to_parquet(path, index=False)


@dataclass
class LabelingStats:
    """Statistics from corpus labeling."""

    total: int = 0
    label_distribution: dict = field(default_factory=dict)
    coverage: float = 0.0
    conflicts: int = 0
    risk_vs_success: dict = field(default_factory=dict)


class CorpusLabeler:
    """Apply weak supervision labels to corpus."""

    def __init__(self, threshold: float = 0.5):
        """Initialize with WeakSupervisionLabeler."""
        self._labeler = WeakSupervisionLabeler(threshold=threshold)
        self._stats = LabelingStats()
        self._labeled_df: pd.DataFrame | None = None

    def label_corpus(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply labels to all rows in corpus."""
        labels = []
        confidences = []
        lf_votes_list = []

        for _, row in df.iterrows():
            code = row.get("python_code", "") or ""
            result = self._labeler.label(code)

            labels.append(result.label.name)
            confidences.append(result.confidence)
            lf_votes_list.append(json.dumps({k: v.name for k, v in result.lf_votes.items()}))

        result_df = df.copy()
        result_df["risk_label"] = labels
        result_df["confidence"] = confidences
        result_df["lf_votes"] = lf_votes_list

        self._labeled_df = result_df
        self._compute_stats(result_df)
        return result_df

    def _compute_stats(self, df: pd.DataFrame) -> None:
        """Compute labeling statistics."""
        self._stats.total = len(df)

        # Label distribution
        label_counts = df["risk_label"].value_counts().to_dict()
        self._stats.label_distribution = label_counts

        # Coverage (non-ABSTAIN)
        non_abstain = len(df[df["risk_label"] != "ABSTAIN"])
        self._stats.coverage = non_abstain / len(df) if len(df) > 0 else 0

        # Get conflict count from underlying labeler
        labeler_stats = self._labeler.get_stats()
        self._stats.conflicts = labeler_stats.get("conflicts", 0)

        # Risk vs success correlation
        if "has_rust" in df.columns:
            risk_success = {}
            for label in df["risk_label"].unique():
                subset = df[df["risk_label"] == label]
                if len(subset) > 0:
                    success_rate = subset["has_rust"].mean()
                    risk_success[label] = {
                        "count": len(subset),
                        "success_rate": round(success_rate, 3),
                    }
            self._stats.risk_vs_success = risk_success

    def get_stats(self) -> dict:
        """Return labeling statistics."""
        return {
            "total": self._stats.total,
            "label_distribution": self._stats.label_distribution,
            "coverage": self._stats.coverage,
            "conflicts": self._stats.conflicts,
            "risk_vs_success": self._stats.risk_vs_success,
        }

    def print_stats(self) -> None:
        """Print formatted statistics."""
        stats = self.get_stats()
        print(f"\n{'='*50}")
        print("CORPUS LABELING STATISTICS")
        print(f"{'='*50}")
        print(f"Total samples: {stats['total']}")
        print(f"Coverage: {stats['coverage']*100:.1f}%")
        print("\nLabel Distribution:")
        for label, count in stats["label_distribution"].items():
            pct = count / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"  {label}: {count} ({pct:.1f}%)")
        if stats["risk_vs_success"]:
            print("\nRisk vs Transpilation Success:")
            for label, info in stats["risk_vs_success"].items():
                print(f"  {label}: {info['success_rate']*100:.1f}% success ({info['count']} samples)")
        print(f"{'='*50}\n")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Apply weak supervision labels to corpus")
    parser.add_argument("input", type=Path, help="Input parquet file")
    parser.add_argument("--output", "-o", type=Path, help="Output parquet file")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    parser.add_argument("--threshold", type=float, default=0.5, help="Confidence threshold")
    args = parser.parse_args()

    print(f"Loading corpus from {args.input}...")
    df = load_corpus(args.input)
    print(f"Loaded {len(df)} samples")

    labeler = CorpusLabeler(threshold=args.threshold)
    print("Applying weak supervision labels...")
    labeled_df = labeler.label_corpus(df)

    labeler.print_stats()

    if args.output and not args.stats:
        save_labeled_corpus(labeled_df, args.output)
        print(f"Saved labeled corpus to {args.output}")


if __name__ == "__main__":
    main()
