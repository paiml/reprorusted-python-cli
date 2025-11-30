#!/usr/bin/env python3
"""Generate Augmented Corpus with Synthetic Examples (GH-10).

Expands training data using Tarantula-targeted mutations.

Usage:
    python scripts/augment_corpus.py data/labeled_corpus.parquet \
        --output data/augmented_corpus.parquet --multiplier 2
    python scripts/augment_corpus.py corpus.parquet --patterns async_await,lambda
    python scripts/augment_corpus.py corpus.parquet --dry-run --verbose
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

# Add scripts directory to path for sibling imports
sys.path.insert(0, str(Path(__file__).parent))
from synthetic_augmenter import MutationStrategy, SyntheticAugmenter
from weak_supervision import WeakSupervisionLabeler


def load_corpus(path: Path) -> pd.DataFrame:
    """Load corpus from parquet file."""
    return pq.read_table(path).to_pandas()


def save_augmented_corpus(df: pd.DataFrame, path: Path) -> None:
    """Save augmented corpus to parquet file."""
    df.to_parquet(path, index=False)


@dataclass
class AugmentationConfig:
    """Configuration for corpus augmentation."""

    multiplier: int = 2
    patterns: list[str] = field(default_factory=lambda: ["async_await", "lambda", "generator"])
    target_risk: str = "LOW_RISK"


class CorpusAugmenter:
    """Augment corpus with synthetic high-risk examples."""

    def __init__(self, config: AugmentationConfig | None = None):
        """Initialize with augmentation config."""
        self.config = config or AugmentationConfig()
        self._augmenter = SyntheticAugmenter(strategy=MutationStrategy.TARANTULA)
        self._labeler = WeakSupervisionLabeler()
        self._stats = {
            "original_count": 0,
            "synthetic_count": 0,
            "mutation_distribution": {},
        }

    def augment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Augment corpus with synthetic examples."""
        self._stats["original_count"] = len(df)

        # Add is_synthetic column to original data
        result_df = df.copy()
        result_df["is_synthetic"] = False

        # Find LOW_RISK samples to augment
        low_risk_mask = result_df["risk_label"] == self.config.target_risk
        low_risk_samples = result_df[low_risk_mask]

        synthetic_rows = []
        mutation_counts = {}

        # Generate synthetic mutations
        for _, row in low_risk_samples.iterrows():
            code = row.get("python_code", "") or ""
            if not code.strip():
                continue

            # Generate mutations based on multiplier
            mutations = self._augmenter.generate_batch(code, count=self.config.multiplier - 1)

            for mutation in mutations:
                # Re-label the mutated code
                label_result = self._labeler.label(mutation.mutated_code)

                synthetic_row = {
                    "python_code": mutation.mutated_code,
                    "rust_code": None,
                    "has_rust": False,
                    "category": row.get("category", "synthetic"),
                    "risk_label": label_result.label.name,
                    "confidence": label_result.confidence,
                    "lf_votes": "{}",
                    "is_synthetic": True,
                    "mutation_type": mutation.mutation_type,
                    "original_category": row.get("category", "unknown"),
                }
                synthetic_rows.append(synthetic_row)

                # Track mutation distribution
                mt = mutation.mutation_type
                mutation_counts[mt] = mutation_counts.get(mt, 0) + 1

        # Append synthetic rows
        if synthetic_rows:
            synthetic_df = pd.DataFrame(synthetic_rows)
            # Ensure columns match (some may be missing in synthetic)
            for col in result_df.columns:
                if col not in synthetic_df.columns:
                    synthetic_df[col] = None
            result_df = pd.concat([result_df, synthetic_df[result_df.columns]], ignore_index=True)

        self._stats["synthetic_count"] = len(synthetic_rows)
        self._stats["mutation_distribution"] = mutation_counts

        return result_df

    def get_stats(self) -> dict:
        """Return augmentation statistics."""
        return self._stats.copy()

    def print_stats(self) -> None:
        """Print formatted statistics."""
        stats = self.get_stats()
        print(f"\n{'='*50}")
        print("CORPUS AUGMENTATION STATISTICS")
        print(f"{'='*50}")
        print(f"Original samples: {stats['original_count']}")
        print(f"Synthetic samples: {stats['synthetic_count']}")
        print(f"Total samples: {stats['original_count'] + stats['synthetic_count']}")
        print("\nMutation Distribution:")
        for mt, count in stats["mutation_distribution"].items():
            print(f"  {mt}: {count}")
        print(f"{'='*50}\n")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Augment corpus with synthetic examples")
    parser.add_argument("input", type=Path, help="Input parquet file")
    parser.add_argument("--output", "-o", type=Path, help="Output parquet file")
    parser.add_argument("--multiplier", "-m", type=int, default=2, help="Augmentation multiplier")
    parser.add_argument("--patterns", type=str, help="Comma-separated mutation patterns")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print(f"Loading corpus from {args.input}...")
    df = load_corpus(args.input)
    print(f"Loaded {len(df)} samples")

    patterns = args.patterns.split(",") if args.patterns else ["async_await", "lambda", "generator"]
    config = AugmentationConfig(multiplier=args.multiplier, patterns=patterns)

    augmenter = CorpusAugmenter(config=config)
    print(f"Augmenting with multiplier={args.multiplier}...")
    augmented_df = augmenter.augment(df)

    augmenter.print_stats()

    # Show label distribution after augmentation
    print("Label Distribution (after augmentation):")
    for label, count in augmented_df["risk_label"].value_counts().items():
        pct = count / len(augmented_df) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")

    if args.output and not args.dry_run:
        save_augmented_corpus(augmented_df, args.output)
        print(f"\nSaved augmented corpus to {args.output}")


if __name__ == "__main__":
    main()
