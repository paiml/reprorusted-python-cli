"""Extreme TDD tests for Weak Supervision Labeling (GH-8).

Book Reference: MLSE Ch. 9.2 - Weak Supervision for Code
Uses Tarantula fault localization scores as labeling function weights.
"""

import pytest

# Import will fail until implementation - TDD Red phase
try:
    from scripts.weak_supervision import (
        WeakSupervisionLabeler,
        LabelingFunction,
        Label,
        LabeledExample,
        TARANTULA_WEIGHTS,
    )
except ImportError:
    WeakSupervisionLabeler = None
    LabelingFunction = None
    Label = None
    LabeledExample = None
    TARANTULA_WEIGHTS = None


@pytest.fixture
def labeler():
    """Create labeler instance."""
    if WeakSupervisionLabeler is None:
        pytest.skip("WeakSupervisionLabeler not implemented yet")
    return WeakSupervisionLabeler()


@pytest.fixture
def async_code():
    """Sample async code (HIGH_RISK)."""
    return "async def fetch(): await asyncio.sleep(1)"


@pytest.fixture
def simple_code():
    """Simple code (LOW_RISK)."""
    return "def add(a, b): return a + b"


class TestTarantulaWeights:
    """Test Tarantula-derived LF weights."""

    def test_weights_exist(self):
        """Weights dictionary should exist."""
        if TARANTULA_WEIGHTS is None:
            pytest.skip("TARANTULA_WEIGHTS not implemented")
        assert isinstance(TARANTULA_WEIGHTS, dict)

    def test_async_weight_highest(self):
        """async_pattern should have highest weight."""
        if TARANTULA_WEIGHTS is None:
            pytest.skip("TARANTULA_WEIGHTS not implemented")
        assert TARANTULA_WEIGHTS["async_pattern"] == pytest.approx(0.946, rel=0.01)


class TestLabel:
    """Test Label enumeration."""

    def test_labels_defined(self):
        """All risk labels should be defined."""
        if Label is None:
            pytest.skip("Label not implemented")
        assert hasattr(Label, "HIGH_RISK")
        assert hasattr(Label, "MEDIUM_RISK")
        assert hasattr(Label, "LOW_RISK")
        assert hasattr(Label, "ABSTAIN")


class TestLabelingFunction:
    """Test LabelingFunction protocol."""

    def test_lf_has_name(self):
        """LF should have name attribute."""
        if LabelingFunction is None:
            pytest.skip("LabelingFunction not implemented")
        lf = LabelingFunction(name="test_lf", weight=0.5, pattern=r"test")
        assert lf.name == "test_lf"

    def test_lf_has_weight(self):
        """LF should have weight from Tarantula."""
        if LabelingFunction is None:
            pytest.skip("LabelingFunction not implemented")
        lf = LabelingFunction(name="async_pattern", weight=0.946, pattern=r"async def")
        assert lf.weight == 0.946


class TestWeakSupervisionLabeler:
    """Test WeakSupervisionLabeler core functionality."""

    def test_labeler_has_labeling_functions(self, labeler):
        """Labeler should have built-in LFs."""
        assert len(labeler.labeling_functions) > 0

    def test_label_returns_labeled_example(self, labeler, simple_code):
        """label() should return LabeledExample."""
        result = labeler.label(simple_code)
        assert isinstance(result, LabeledExample)

    def test_labeled_example_has_fields(self, labeler, simple_code):
        """LabeledExample should have required fields."""
        result = labeler.label(simple_code)
        assert hasattr(result, "code")
        assert hasattr(result, "label")
        assert hasattr(result, "confidence")
        assert hasattr(result, "lf_votes")

    def test_confidence_between_0_and_1(self, labeler, simple_code):
        """Confidence should be normalized."""
        result = labeler.label(simple_code)
        assert 0.0 <= result.confidence <= 1.0

    def test_async_code_labeled_high_risk(self, labeler, async_code):
        """Async code should be labeled HIGH_RISK."""
        result = labeler.label(async_code)
        assert result.label == Label.HIGH_RISK

    def test_simple_code_labeled_low_risk(self, labeler, simple_code):
        """Simple code should be labeled LOW_RISK."""
        result = labeler.label(simple_code)
        assert result.label == Label.LOW_RISK

    def test_get_stats(self, labeler):
        """get_stats should return LF statistics."""
        codes = ["async def f(): pass", "def g(): return 1", "yield x"]
        for c in codes:
            labeler.label(c)
        stats = labeler.get_stats()
        assert "coverage" in stats
        assert "conflicts" in stats
