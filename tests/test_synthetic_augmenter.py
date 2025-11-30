"""Extreme TDD tests for Synthetic Error Augmentation (GH-7).

Book Reference: MLSE Ch. 8.3 - Data Augmentation for Code
Uses Tarantula fault localization scores for targeted mutations.
"""

import pytest
from dataclasses import dataclass

# Import will fail until we implement - this is TDD Red phase
try:
    from scripts.synthetic_augmenter import (
        SyntheticAugmenter,
        MutationStrategy,
        AugmentedExample,
        TARANTULA_SCORES,
    )
except ImportError:
    SyntheticAugmenter = None
    MutationStrategy = None
    AugmentedExample = None
    TARANTULA_SCORES = None


@pytest.fixture
def augmenter():
    """Create augmenter instance."""
    if SyntheticAugmenter is None:
        pytest.skip("SyntheticAugmenter not implemented yet")
    return SyntheticAugmenter()


@pytest.fixture
def sample_python_code():
    """Sample Python code for mutation testing."""
    return '''
def process_data(items: list[int]) -> int:
    """Process a list of integers."""
    total = 0
    for item in items:
        total += item
    return total
'''


class TestTarantulaScores:
    """Test Tarantula suspiciousness scores are correctly defined."""

    def test_tarantula_scores_exist(self):
        """Scores dictionary should exist."""
        if TARANTULA_SCORES is None:
            pytest.skip("TARANTULA_SCORES not implemented")
        assert isinstance(TARANTULA_SCORES, dict)

    def test_high_priority_features(self):
        """HIGH priority features should have scores > 0.7."""
        if TARANTULA_SCORES is None:
            pytest.skip("TARANTULA_SCORES not implemented")
        high_priority = ["async_await", "generator", "walrus_operator", "lambda"]
        for feat in high_priority:
            assert feat in TARANTULA_SCORES
            assert TARANTULA_SCORES[feat] > 0.7, f"{feat} should be HIGH priority"

    def test_async_await_highest(self):
        """async_await should have highest score (0.946)."""
        if TARANTULA_SCORES is None:
            pytest.skip("TARANTULA_SCORES not implemented")
        assert TARANTULA_SCORES["async_await"] == pytest.approx(0.946, rel=0.01)


class TestMutationStrategy:
    """Test mutation strategy enumeration."""

    def test_strategies_defined(self):
        """All mutation strategies should be defined."""
        if MutationStrategy is None:
            pytest.skip("MutationStrategy not implemented")
        assert hasattr(MutationStrategy, "TARANTULA")
        assert hasattr(MutationStrategy, "RANDOM")
        assert hasattr(MutationStrategy, "TARGETED")


class TestSyntheticAugmenter:
    """Test SyntheticAugmenter core functionality."""

    def test_augmenter_initialization(self, augmenter):
        """Augmenter should initialize with default strategy."""
        assert augmenter.strategy == MutationStrategy.TARANTULA

    def test_augmenter_custom_strategy(self):
        """Augmenter should accept custom strategy."""
        if SyntheticAugmenter is None:
            pytest.skip("SyntheticAugmenter not implemented")
        aug = SyntheticAugmenter(strategy=MutationStrategy.RANDOM)
        assert aug.strategy == MutationStrategy.RANDOM

    def test_mutate_returns_augmented_example(self, augmenter, sample_python_code):
        """mutate() should return AugmentedExample."""
        result = augmenter.mutate(sample_python_code)
        assert isinstance(result, AugmentedExample)

    def test_augmented_example_has_required_fields(self, augmenter, sample_python_code):
        """AugmentedExample should have all required fields."""
        result = augmenter.mutate(sample_python_code)
        assert hasattr(result, "original_code")
        assert hasattr(result, "mutated_code")
        assert hasattr(result, "mutation_type")
        assert hasattr(result, "is_synthetic")
        assert result.is_synthetic is True

    def test_mutate_changes_code(self, augmenter, sample_python_code):
        """Mutation should change the code."""
        result = augmenter.mutate(sample_python_code)
        assert result.mutated_code != result.original_code

    def test_generate_batch(self, augmenter, sample_python_code):
        """generate_batch should produce multiple mutations."""
        results = augmenter.generate_batch(sample_python_code, count=3)
        assert len(results) == 3
        for r in results:
            assert isinstance(r, AugmentedExample)


class TestAsyncAwaitMutations:
    """Test async/await mutations (highest Tarantula score: 0.946)."""

    def test_inject_async_pattern(self, augmenter):
        """Should inject async/await pattern into sync code."""
        sync_code = "def fetch(): return data"
        result = augmenter.inject_async_pattern(sync_code)
        assert "async def" in result.mutated_code or "await" in result.mutated_code
        assert result.mutation_type == "async_await"

    def test_async_mutation_preserves_function_name(self, augmenter):
        """Async injection should preserve function name."""
        sync_code = "def my_function(): pass"
        result = augmenter.inject_async_pattern(sync_code)
        assert "my_function" in result.mutated_code


class TestGeneratorMutations:
    """Test generator mutations (Tarantula score: 0.927)."""

    def test_inject_generator_pattern(self, augmenter):
        """Should inject yield into return functions."""
        code = "def get_items(): return [1, 2, 3]"
        result = augmenter.inject_generator_pattern(code)
        assert "yield" in result.mutated_code
        assert result.mutation_type == "generator"
