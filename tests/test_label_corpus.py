"""Extreme TDD tests for Corpus Labeling Pipeline (GH-9).

Applies weak supervision labels to CITL corpus for ML training.
"""

import json
import tempfile
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import pytest

# TDD Red phase - imports will fail until implementation
try:
    from scripts.label_corpus import (
        CorpusLabeler,
        LabelingStats,
        load_corpus,
        save_labeled_corpus,
    )
except ImportError:
    CorpusLabeler = None
    LabelingStats = None
    load_corpus = None
    save_labeled_corpus = None


@pytest.fixture
def sample_corpus_df():
    """Create sample corpus DataFrame for testing."""
    return pd.DataFrame({
        "python_code": [
            "async def fetch(): await asyncio.sleep(1)",
            "def add(a, b): return a + b",
            "def gen(): yield 1; yield 2",
            "process = lambda x: x * 2",
            "with open('f') as f: pass",
        ],
        "rust_code": [
            None,
            "fn add(a: i32, b: i32) -> i32 { a + b }",
            None,
            None,
            "let f = File::open(\"f\")?;",
        ],
        "has_rust": [False, True, False, False, True],
        "category": ["async_basic", "math_ops", "generator", "lambda", "file_io"],
    })


@pytest.fixture
def temp_parquet(sample_corpus_df):
    """Create temporary parquet file."""
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
        sample_corpus_df.to_parquet(f.name)
        yield Path(f.name)
    Path(f.name).unlink(missing_ok=True)


class TestLoadCorpus:
    """Test corpus loading functionality."""

    def test_load_corpus_returns_dataframe(self, temp_parquet):
        """load_corpus should return pandas DataFrame."""
        if load_corpus is None:
            pytest.skip("load_corpus not implemented")
        df = load_corpus(temp_parquet)
        assert isinstance(df, pd.DataFrame)

    def test_load_corpus_has_required_columns(self, temp_parquet):
        """Loaded corpus should have python_code column."""
        if load_corpus is None:
            pytest.skip("load_corpus not implemented")
        df = load_corpus(temp_parquet)
        assert "python_code" in df.columns


class TestCorpusLabeler:
    """Test CorpusLabeler class."""

    def test_labeler_initialization(self):
        """CorpusLabeler should initialize."""
        if CorpusLabeler is None:
            pytest.skip("CorpusLabeler not implemented")
        labeler = CorpusLabeler()
        assert labeler is not None

    def test_label_corpus_adds_columns(self, sample_corpus_df):
        """label_corpus should add risk_label, confidence, lf_votes columns."""
        if CorpusLabeler is None:
            pytest.skip("CorpusLabeler not implemented")
        labeler = CorpusLabeler()
        result = labeler.label_corpus(sample_corpus_df)
        assert "risk_label" in result.columns
        assert "confidence" in result.columns
        assert "lf_votes" in result.columns

    def test_async_code_labeled_high_risk(self, sample_corpus_df):
        """Async code should be labeled HIGH_RISK."""
        if CorpusLabeler is None:
            pytest.skip("CorpusLabeler not implemented")
        labeler = CorpusLabeler()
        result = labeler.label_corpus(sample_corpus_df)
        async_row = result[result["category"] == "async_basic"].iloc[0]
        assert async_row["risk_label"] == "HIGH_RISK"

    def test_simple_code_labeled_low_risk(self, sample_corpus_df):
        """Simple code should be labeled LOW_RISK."""
        if CorpusLabeler is None:
            pytest.skip("CorpusLabeler not implemented")
        labeler = CorpusLabeler()
        result = labeler.label_corpus(sample_corpus_df)
        simple_row = result[result["category"] == "math_ops"].iloc[0]
        assert simple_row["risk_label"] == "LOW_RISK"

    def test_confidence_between_0_and_1(self, sample_corpus_df):
        """All confidence values should be in [0, 1]."""
        if CorpusLabeler is None:
            pytest.skip("CorpusLabeler not implemented")
        labeler = CorpusLabeler()
        result = labeler.label_corpus(sample_corpus_df)
        assert all(0 <= c <= 1 for c in result["confidence"])


class TestLabelingStats:
    """Test labeling statistics."""

    def test_stats_has_label_distribution(self, sample_corpus_df):
        """Stats should include label distribution."""
        if CorpusLabeler is None:
            pytest.skip("CorpusLabeler not implemented")
        labeler = CorpusLabeler()
        labeler.label_corpus(sample_corpus_df)
        stats = labeler.get_stats()
        assert "label_distribution" in stats

    def test_stats_has_coverage(self, sample_corpus_df):
        """Stats should include coverage rate."""
        if CorpusLabeler is None:
            pytest.skip("CorpusLabeler not implemented")
        labeler = CorpusLabeler()
        labeler.label_corpus(sample_corpus_df)
        stats = labeler.get_stats()
        assert "coverage" in stats
        assert 0 <= stats["coverage"] <= 1

    def test_stats_has_risk_vs_success_correlation(self, sample_corpus_df):
        """Stats should show risk label vs transpilation success."""
        if CorpusLabeler is None:
            pytest.skip("CorpusLabeler not implemented")
        labeler = CorpusLabeler()
        labeled = labeler.label_corpus(sample_corpus_df)
        stats = labeler.get_stats()
        assert "risk_vs_success" in stats


class TestSaveCorpus:
    """Test saving labeled corpus."""

    def test_save_creates_parquet(self, sample_corpus_df):
        """save_labeled_corpus should create parquet file."""
        if save_labeled_corpus is None or CorpusLabeler is None:
            pytest.skip("Not implemented")
        labeler = CorpusLabeler()
        labeled = labeler.label_corpus(sample_corpus_df)
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            save_labeled_corpus(labeled, Path(f.name))
            assert Path(f.name).exists()
            # Verify it's readable
            loaded = pq.read_table(f.name).to_pandas()
            assert "risk_label" in loaded.columns
            Path(f.name).unlink()

    def test_lf_votes_serialized_as_json(self, sample_corpus_df):
        """lf_votes should be JSON-serialized string."""
        if CorpusLabeler is None:
            pytest.skip("CorpusLabeler not implemented")
        labeler = CorpusLabeler()
        result = labeler.label_corpus(sample_corpus_df)
        # Should be valid JSON
        for votes in result["lf_votes"]:
            parsed = json.loads(votes)
            assert isinstance(parsed, dict)
