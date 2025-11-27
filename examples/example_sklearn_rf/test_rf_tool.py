#!/usr/bin/env python3
"""EXTREME TDD: Tests for sklearn RandomForestClassifier CLI.

Academic Reference: Breiman (2001) Random Forests [8]
Tests ensemble classification with bootstrap aggregation.
"""

import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "rf_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestRfFit:
    """Test forest fitting."""

    def test_fit_simple(self):
        """Test fitting on simple data."""
        data = json.dumps({
            "X": [[0], [1], [2], [3]],
            "y": [0, 0, 1, 1],
            "n_estimators": 3
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "trees" in result
        assert len(result["trees"]) == 3

    def test_fit_default_estimators(self):
        """Test default n_estimators=10."""
        data = json.dumps({
            "X": [[0], [1], [2], [3]],
            "y": [0, 0, 1, 1]
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert len(result["trees"]) == 10

    def test_fit_empty_fails(self):
        """Test that fitting on empty data fails."""
        data = json.dumps({"X": [], "y": []})
        stdout, stderr, code = run(["fit"], data)
        assert code == 1


class TestRfPredict:
    """Test forest prediction."""

    def test_predict_majority_vote(self):
        """Test that prediction uses majority voting."""
        # Trees that all agree
        data = json.dumps({
            "X": [[0], [3]],
            "trees": [
                {"feature": 0, "threshold": 1.5, "left": {"class": 0}, "right": {"class": 1}},
                {"feature": 0, "threshold": 1.5, "left": {"class": 0}, "right": {"class": 1}},
                {"feature": 0, "threshold": 1.5, "left": {"class": 0}, "right": {"class": 1}},
            ]
        })
        stdout, stderr, code = run(["predict"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["predictions"] == [0, 1]


class TestRfFitPredict:
    """Test combined fit-predict."""

    def test_fit_predict(self):
        """Test fit-predict pipeline."""
        data = json.dumps({
            "X_train": [[0], [1], [2], [3]],
            "y_train": [0, 0, 1, 1],
            "X_test": [[0.5], [2.5]],
            "n_estimators": 5
        })
        stdout, stderr, code = run(["fit-predict"], data)
        assert code == 0
        result = json.loads(stdout)
        # With enough trees, should get correct predictions
        assert result["predictions"][0] == 0
        assert result["predictions"][1] == 1


class TestRfScore:
    """Test forest scoring."""

    def test_score_high_accuracy(self):
        """Test scoring on separable data."""
        data = json.dumps({
            "X": [[0], [1], [8], [9]],
            "y": [0, 0, 1, 1],
            "trees": [
                {"feature": 0, "threshold": 4.5, "left": {"class": 0}, "right": {"class": 1}},
            ]
        })
        stdout, stderr, code = run(["score"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["accuracy"] == 1.0


class TestRfHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "RandomForest" in stdout or "forest" in stdout.lower()


class TestRfEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["fit"], "not json")
        assert code == 1
