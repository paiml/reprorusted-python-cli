"""Extreme TDD tests for Zero-Success Category Analyzer (GH-12).

Analyzes failing categories to help depyler team prioritize.
"""

import json
import pandas as pd
import pytest

# TDD Red phase - imports will fail until implementation
try:
    from scripts.zero_success_analyzer import (
        ZeroSuccessAnalyzer,
        CategoryAnalysis,
        group_categories,
        generate_depyler_recommendations,
    )
except ImportError:
    ZeroSuccessAnalyzer = None
    CategoryAnalysis = None
    group_categories = None
    generate_depyler_recommendations = None


@pytest.fixture
def sample_corpus_df():
    """Create sample corpus with zero-success categories."""
    return pd.DataFrame({
        "python_code": [
            "async def fetch(): await sleep(1)",
            "async with ctx: pass",
            "def curry(f): return lambda x: f(x)",
            "class FSM: pass",
            "def add(a, b): return a + b",  # successful
        ],
        "rust_code": [
            None,
            None,
            None,
            None,
            "fn add(a: i32, b: i32) -> i32 { a + b }",
        ],
        "has_rust": [False, False, False, False, True],
        "category": ["async_iterator", "async_context", "func_curry", "state_fsm", "math_ops"],
        "risk_label": ["HIGH_RISK", "HIGH_RISK", "HIGH_RISK", "HIGH_RISK", "LOW_RISK"],
    })


class TestCategoryAnalysis:
    """Test CategoryAnalysis data class."""

    def test_analysis_has_category(self):
        """Analysis should have category name."""
        if CategoryAnalysis is None:
            pytest.skip("CategoryAnalysis not implemented")
        analysis = CategoryAnalysis(
            category="async_iterator",
            blocking_features=[],
            sample_code="",
            recommendation="",
        )
        assert analysis.category == "async_iterator"

    def test_analysis_has_blocking_features(self):
        """Analysis should list blocking features."""
        if CategoryAnalysis is None:
            pytest.skip("CategoryAnalysis not implemented")
        analysis = CategoryAnalysis(
            category="async_iterator",
            blocking_features=["async_await", "generator"],
            sample_code="",
            recommendation="",
        )
        assert "async_await" in analysis.blocking_features


class TestGroupCategories:
    """Test category grouping."""

    def test_groups_async_categories(self):
        """Should group async_* categories together."""
        if group_categories is None:
            pytest.skip("group_categories not implemented")
        categories = ["async_context", "async_iterator", "func_curry"]
        groups = group_categories(categories)
        assert "async" in groups
        assert "async_context" in groups["async"]

    def test_groups_func_categories(self):
        """Should group func_* categories together."""
        if group_categories is None:
            pytest.skip("group_categories not implemented")
        categories = ["func_curry", "func_pipeline", "async_context"]
        groups = group_categories(categories)
        assert "func" in groups


class TestZeroSuccessAnalyzer:
    """Test ZeroSuccessAnalyzer class."""

    def test_analyzer_initialization(self):
        """Analyzer should initialize."""
        if ZeroSuccessAnalyzer is None:
            pytest.skip("ZeroSuccessAnalyzer not implemented")
        analyzer = ZeroSuccessAnalyzer()
        assert analyzer is not None

    def test_find_zero_success_categories(self, sample_corpus_df):
        """Should identify zero-success categories."""
        if ZeroSuccessAnalyzer is None:
            pytest.skip("ZeroSuccessAnalyzer not implemented")
        analyzer = ZeroSuccessAnalyzer()
        zero_cats = analyzer.find_zero_success(sample_corpus_df)
        assert "async_iterator" in zero_cats
        assert "math_ops" not in zero_cats  # has success

    def test_analyze_returns_list(self, sample_corpus_df):
        """analyze() should return list of CategoryAnalysis."""
        if ZeroSuccessAnalyzer is None:
            pytest.skip("ZeroSuccessAnalyzer not implemented")
        analyzer = ZeroSuccessAnalyzer()
        results = analyzer.analyze(sample_corpus_df)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_analysis_identifies_blocking_features(self, sample_corpus_df):
        """Analysis should identify blocking features."""
        if ZeroSuccessAnalyzer is None:
            pytest.skip("ZeroSuccessAnalyzer not implemented")
        analyzer = ZeroSuccessAnalyzer()
        results = analyzer.analyze(sample_corpus_df)
        async_analysis = next((r for r in results if r.category == "async_iterator"), None)
        assert async_analysis is not None
        assert len(async_analysis.blocking_features) > 0


class TestDepylerRecommendations:
    """Test recommendation generation for depyler."""

    def test_generates_recommendations(self, sample_corpus_df):
        """Should generate prioritized recommendations."""
        if generate_depyler_recommendations is None:
            pytest.skip("generate_depyler_recommendations not implemented")
        recs = generate_depyler_recommendations(sample_corpus_df)
        assert isinstance(recs, list)
        assert len(recs) > 0

    def test_recommendations_have_priority(self, sample_corpus_df):
        """Recommendations should have priority ranking."""
        if generate_depyler_recommendations is None:
            pytest.skip("generate_depyler_recommendations not implemented")
        recs = generate_depyler_recommendations(sample_corpus_df)
        for rec in recs:
            assert "priority" in rec
            assert "feature" in rec

    def test_recommendations_sorted_by_impact(self, sample_corpus_df):
        """Recommendations should be sorted by impact."""
        if generate_depyler_recommendations is None:
            pytest.skip("generate_depyler_recommendations not implemented")
        recs = generate_depyler_recommendations(sample_corpus_df)
        if len(recs) >= 2:
            assert recs[0].get("impact", 0) >= recs[1].get("impact", 0)
