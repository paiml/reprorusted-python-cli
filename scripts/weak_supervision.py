#!/usr/bin/env python3
"""Weak Supervision Labeling for Training Data (GH-8).

Book Reference: MLSE Ch. 9.2 - Weak Supervision for Code
Uses Tarantula fault localization scores as labeling function weights.

Usage:
    python scripts/weak_supervision.py data/corpus.parquet --output labeled.parquet
    python scripts/weak_supervision.py corpus.parquet --stats
    python scripts/weak_supervision.py corpus.parquet --lfs async_pattern,generator_pattern
    python scripts/weak_supervision.py corpus.parquet --threshold 0.7
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto

# Tarantula-derived weights for labeling functions
TARANTULA_WEIGHTS: dict[str, float] = {
    "async_pattern": 0.946,
    "generator_pattern": 0.927,
    "walrus_pattern": 0.850,
    "lambda_pattern": 0.783,
    "context_manager_pattern": 0.652,
    "class_pattern": 0.612,
    "exception_pattern": 0.577,
}


class Label(Enum):
    """Risk labels for code transpilation."""

    HIGH_RISK = auto()
    MEDIUM_RISK = auto()
    LOW_RISK = auto()
    ABSTAIN = auto()


@dataclass
class LabelingFunction:
    """A programmatic labeling function with Tarantula weight."""

    name: str
    weight: float
    pattern: str
    label: Label = Label.HIGH_RISK

    def apply(self, code: str) -> Label:
        """Apply LF to code, return label or ABSTAIN."""
        if re.search(self.pattern, code):
            return self.label
        return Label.ABSTAIN


@dataclass
class LabeledExample:
    """Result of weak supervision labeling."""

    code: str
    label: Label
    confidence: float
    lf_votes: dict[str, Label] = field(default_factory=dict)


class WeakSupervisionLabeler:
    """Label code using programmatic labeling functions."""

    def __init__(self, threshold: float = 0.5):
        """Initialize with built-in Tarantula-weighted LFs."""
        self.threshold = threshold
        self._stats = {"labeled": 0, "conflicts": 0, "abstentions": 0}
        self.labeling_functions = [
            LabelingFunction(
                name="async_pattern",
                weight=TARANTULA_WEIGHTS["async_pattern"],
                pattern=r"async def|await ",
                label=Label.HIGH_RISK,
            ),
            LabelingFunction(
                name="generator_pattern",
                weight=TARANTULA_WEIGHTS["generator_pattern"],
                pattern=r"yield ",
                label=Label.HIGH_RISK,
            ),
            LabelingFunction(
                name="lambda_pattern",
                weight=TARANTULA_WEIGHTS["lambda_pattern"],
                pattern=r"lambda ",
                label=Label.MEDIUM_RISK,
            ),
            LabelingFunction(
                name="context_manager_pattern",
                weight=TARANTULA_WEIGHTS["context_manager_pattern"],
                pattern=r"with .+:",
                label=Label.MEDIUM_RISK,
            ),
        ]

    def label(self, code: str) -> LabeledExample:
        """Apply all LFs and aggregate labels."""
        votes: dict[str, Label] = {}
        weighted_scores: dict[Label, float] = {
            Label.HIGH_RISK: 0.0,
            Label.MEDIUM_RISK: 0.0,
            Label.LOW_RISK: 0.0,
        }

        for lf in self.labeling_functions:
            vote = lf.apply(code)
            votes[lf.name] = vote
            if vote != Label.ABSTAIN:
                weighted_scores[vote] += lf.weight

        # Determine final label
        non_abstain = [v for v in votes.values() if v != Label.ABSTAIN]
        if not non_abstain:
            final_label = Label.LOW_RISK
            confidence = 1.0
            self._stats["abstentions"] += 1
        else:
            final_label = max(weighted_scores, key=weighted_scores.get)
            total_weight = sum(weighted_scores.values())
            confidence = weighted_scores[final_label] / total_weight if total_weight else 0.5
            if len(set(non_abstain)) > 1:
                self._stats["conflicts"] += 1

        self._stats["labeled"] += 1
        return LabeledExample(code=code, label=final_label, confidence=confidence, lf_votes=votes)

    def get_stats(self) -> dict:
        """Return labeling statistics."""
        total = self._stats["labeled"] or 1
        return {
            "total_labeled": self._stats["labeled"],
            "coverage": (total - self._stats["abstentions"]) / total,
            "conflicts": self._stats["conflicts"] / total,
            "abstentions": self._stats["abstentions"],
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Weak Supervision Labeling")
    parser.add_argument("input", help="Input parquet file")
    parser.add_argument("--output", "-o", help="Output parquet file")
    parser.add_argument("--stats", action="store_true", help="Show LF statistics")
    parser.add_argument("--lfs", help="Comma-separated LF names to use")
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()

    labeler = WeakSupervisionLabeler(threshold=args.threshold)
    print(f"Labeler initialized with {len(labeler.labeling_functions)} LFs")
