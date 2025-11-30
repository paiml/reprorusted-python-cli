"""Extreme TDD tests for Corpus Augmentation Pipeline (GH-10).

Generates augmented corpus with synthetic high-risk examples.
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

# TDD Red phase - imports will fail until implementation
try:
    from scripts.augment_corpus import (
        CorpusAugmenter,
        AugmentationConfig,
        load_corpus,
        save_augmented_corpus,
    )
except ImportError:
    CorpusAugmenter = None
    AugmentationConfig = None
    load_corpus = None
    save_augmented_corpus = None


@pytest.fixture
def sample_labeled_df():
    """Create sample labeled corpus for testing."""
    return pd.DataFrame({
        "python_code": [
            "def add(a, b): return a + b",
            "def multiply(x, y): return x * y",
            "async def fetch(): await sleep(1)",
            "process = lambda x: x * 2",
        ],
        "rust_code": [
            "fn add(a: i32, b: i32) -> i32 { a + b }",
            "fn multiply(x: i32, y: i32) -> i32 { x * y }",
            None,
            None,
        ],
        "has_rust": [True, True, False, False],
        "category": ["math", "math", "async", "lambda"],
        "risk_label": ["LOW_RISK", "LOW_RISK", "HIGH_RISK", "HIGH_RISK"],
        "confidence": [1.0, 1.0, 0.95, 0.78],
        "lf_votes": ["{}", "{}", "{}", "{}"],
    })


class TestAugmentationConfig:
    """Test augmentation configuration."""

    def test_config_has_multiplier(self):
        """Config should have multiplier setting."""
        if AugmentationConfig is None:
            pytest.skip("AugmentationConfig not implemented")
        config = AugmentationConfig(multiplier=2)
        assert config.multiplier == 2

    def test_config_has_target_patterns(self):
        """Config should specify target patterns."""
        if AugmentationConfig is None:
            pytest.skip("AugmentationConfig not implemented")
        config = AugmentationConfig(patterns=["async_await", "lambda"])
        assert "async_await" in config.patterns


class TestCorpusAugmenter:
    """Test CorpusAugmenter class."""

    def test_augmenter_initialization(self):
        """CorpusAugmenter should initialize."""
        if CorpusAugmenter is None:
            pytest.skip("CorpusAugmenter not implemented")
        augmenter = CorpusAugmenter()
        assert augmenter is not None

    def test_augment_increases_size(self, sample_labeled_df):
        """Augmentation should increase corpus size."""
        if CorpusAugmenter is None:
            pytest.skip("CorpusAugmenter not implemented")
        augmenter = CorpusAugmenter(config=AugmentationConfig(multiplier=2))
        result = augmenter.augment(sample_labeled_df)
        assert len(result) > len(sample_labeled_df)

    def test_augment_adds_is_synthetic_column(self, sample_labeled_df):
        """Augmented corpus should have is_synthetic column."""
        if CorpusAugmenter is None:
            pytest.skip("CorpusAugmenter not implemented")
        augmenter = CorpusAugmenter()
        result = augmenter.augment(sample_labeled_df)
        assert "is_synthetic" in result.columns

    def test_original_rows_not_synthetic(self, sample_labeled_df):
        """Original rows should have is_synthetic=False."""
        if CorpusAugmenter is None:
            pytest.skip("CorpusAugmenter not implemented")
        augmenter = CorpusAugmenter()
        result = augmenter.augment(sample_labeled_df)
        original_count = len(sample_labeled_df)
        # First N rows should be originals
        assert not result.iloc[:original_count]["is_synthetic"].any()

    def test_synthetic_rows_marked(self, sample_labeled_df):
        """Synthetic rows should have is_synthetic=True."""
        if CorpusAugmenter is None:
            pytest.skip("CorpusAugmenter not implemented")
        augmenter = CorpusAugmenter(config=AugmentationConfig(multiplier=2))
        result = augmenter.augment(sample_labeled_df)
        synthetic = result[result["is_synthetic"] == True]
        assert len(synthetic) > 0

    def test_augment_targets_low_risk(self, sample_labeled_df):
        """Augmentation should primarily target LOW_RISK samples."""
        if CorpusAugmenter is None:
            pytest.skip("CorpusAugmenter not implemented")
        augmenter = CorpusAugmenter()
        result = augmenter.augment(sample_labeled_df)
        # Synthetic samples should be mutations of low-risk originals
        synthetic = result[result["is_synthetic"] == True]
        # They should now be HIGH_RISK due to mutations
        high_risk_synthetic = synthetic[synthetic["risk_label"] == "HIGH_RISK"]
        assert len(high_risk_synthetic) > 0


class TestAugmentationStats:
    """Test augmentation statistics."""

    def test_get_stats_returns_dict(self, sample_labeled_df):
        """get_stats should return statistics dict."""
        if CorpusAugmenter is None:
            pytest.skip("CorpusAugmenter not implemented")
        augmenter = CorpusAugmenter()
        augmenter.augment(sample_labeled_df)
        stats = augmenter.get_stats()
        assert isinstance(stats, dict)

    def test_stats_has_synthetic_count(self, sample_labeled_df):
        """Stats should include synthetic sample count."""
        if CorpusAugmenter is None:
            pytest.skip("CorpusAugmenter not implemented")
        augmenter = CorpusAugmenter()
        augmenter.augment(sample_labeled_df)
        stats = augmenter.get_stats()
        assert "synthetic_count" in stats

    def test_stats_has_mutation_distribution(self, sample_labeled_df):
        """Stats should show mutation type distribution."""
        if CorpusAugmenter is None:
            pytest.skip("CorpusAugmenter not implemented")
        augmenter = CorpusAugmenter()
        augmenter.augment(sample_labeled_df)
        stats = augmenter.get_stats()
        assert "mutation_distribution" in stats


class TestSaveAugmentedCorpus:
    """Test saving augmented corpus."""

    def test_save_creates_parquet(self, sample_labeled_df):
        """save_augmented_corpus should create parquet file."""
        if save_augmented_corpus is None or CorpusAugmenter is None:
            pytest.skip("Not implemented")
        augmenter = CorpusAugmenter()
        augmented = augmenter.augment(sample_labeled_df)
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            save_augmented_corpus(augmented, Path(f.name))
            assert Path(f.name).exists()
            Path(f.name).unlink()
