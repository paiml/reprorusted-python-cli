"""Extreme TDD tests for Category Diff Tracking (GH-16).

Shows which categories changed status after depyler fixes.
"""

import json

import pandas as pd
import pytest

# TDD Red phase - imports will fail until implementation
try:
    from scripts.category_diff import (
        CategoryChanges,
        compare_category_success,
    )
except ImportError:
    compare_category_success = None
    CategoryChanges = None


@pytest.fixture
def baseline_df():
    """Baseline corpus with some failing categories."""
    return pd.DataFrame({
        "category": ["math", "async", "lambda", "pathlib", "walrus"],
        "has_rust": [True, False, False, False, False],
    })


@pytest.fixture
def improved_df():
    """Improved corpus after depyler fix."""
    return pd.DataFrame({
        "category": ["math", "async", "lambda", "pathlib", "walrus"],
        "has_rust": [True, False, True, True, True],  # lambda, pathlib, walrus now pass
    })


@pytest.fixture
def regressed_df():
    """Corpus with regression."""
    return pd.DataFrame({
        "category": ["math", "async", "lambda", "pathlib", "walrus"],
        "has_rust": [False, False, False, False, False],  # math regressed
    })


class TestCategoryChanges:
    """Test CategoryChanges data class."""

    def test_has_now_passing(self):
        """Should have now_passing list."""
        if CategoryChanges is None:
            pytest.skip("CategoryChanges not implemented")
        changes = CategoryChanges(now_passing=["a"], regressed=[], unchanged=[])
        assert "a" in changes.now_passing

    def test_has_regressed(self):
        """Should have regressed list."""
        if CategoryChanges is None:
            pytest.skip("CategoryChanges not implemented")
        changes = CategoryChanges(now_passing=[], regressed=["b"], unchanged=[])
        assert "b" in changes.regressed


class TestCompareCategorySuccess:
    """Test compare_category_success function."""

    def test_returns_category_changes(self, baseline_df, improved_df):
        """Should return CategoryChanges object."""
        if compare_category_success is None:
            pytest.skip("compare_category_success not implemented")
        changes = compare_category_success(baseline_df, improved_df)
        assert isinstance(changes, CategoryChanges)

    def test_detects_now_passing(self, baseline_df, improved_df):
        """Should detect categories that went failing → passing."""
        if compare_category_success is None:
            pytest.skip("compare_category_success not implemented")
        changes = compare_category_success(baseline_df, improved_df)
        assert "lambda" in changes.now_passing
        assert "pathlib" in changes.now_passing
        assert "walrus" in changes.now_passing

    def test_detects_regression(self, baseline_df, regressed_df):
        """Should detect categories that regressed."""
        if compare_category_success is None:
            pytest.skip("compare_category_success not implemented")
        changes = compare_category_success(baseline_df, regressed_df)
        assert "math" in changes.regressed

    def test_unchanged_not_in_changes(self, baseline_df, improved_df):
        """Categories that stayed same should be in unchanged."""
        if compare_category_success is None:
            pytest.skip("compare_category_success not implemented")
        changes = compare_category_success(baseline_df, improved_df)
        assert "math" in changes.unchanged  # stayed passing
        assert "async" in changes.unchanged  # stayed failing

    def test_to_json(self, baseline_df, improved_df):
        """Should serialize to JSON."""
        if compare_category_success is None:
            pytest.skip("compare_category_success not implemented")
        changes = compare_category_success(baseline_df, improved_df)
        j = changes.to_json()
        parsed = json.loads(j)
        assert "now_passing" in parsed
        assert "regressed" in parsed

    def test_net_change(self, baseline_df, improved_df):
        """Should calculate net change."""
        if compare_category_success is None:
            pytest.skip("compare_category_success not implemented")
        changes = compare_category_success(baseline_df, improved_df)
        assert changes.net_change == 3  # 3 new passing, 0 regressed
