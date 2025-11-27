#!/usr/bin/env python3
"""EXTREME TDD: Tests for sklearn DecisionTreeClassifier CLI.

Academic Reference: Breiman (2001) Random Forests [8] - GINI criterion
Tests decision tree classification with fit/predict/score pattern.
"""

import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "dtree_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestDtreeFit:
    """Test tree fitting."""

    def test_fit_simple_binary(self):
        """Test fitting on simple binary classification."""
        # XOR-like pattern
        data = json.dumps({
            "X": [[0, 0], [0, 1], [1, 0], [1, 1]],
            "y": [0, 1, 1, 0]
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "tree" in result

    def test_fit_with_max_depth(self):
        """Test fitting with max_depth parameter."""
        data = json.dumps({
            "X": [[0], [1], [2], [3]],
            "y": [0, 0, 1, 1],
            "max_depth": 2
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "tree" in result

    def test_fit_empty_fails(self):
        """Test that fitting on empty data fails."""
        data = json.dumps({"X": [], "y": []})
        stdout, stderr, code = run(["fit"], data)
        assert code == 1


class TestDtreePredict:
    """Test tree prediction."""

    def test_predict_simple(self):
        """Test prediction on simple data."""
        # Precomputed tree for x > 1.5 -> 1, else 0
        data = json.dumps({
            "X": [[0], [3]],
            "tree": {
                "feature": 0,
                "threshold": 1.5,
                "left": {"class": 0},
                "right": {"class": 1}
            }
        })
        stdout, stderr, code = run(["predict"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "predictions" in result
        assert result["predictions"] == [0, 1]


class TestDtreeFitPredict:
    """Test combined fit-predict."""

    def test_fit_predict_linearly_separable(self):
        """Test fit-predict on linearly separable data."""
        data = json.dumps({
            "X_train": [[0], [1], [2], [3]],
            "y_train": [0, 0, 1, 1],
            "X_test": [[0.5], [2.5]]
        })
        stdout, stderr, code = run(["fit-predict"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["predictions"][0] == 0
        assert result["predictions"][1] == 1


class TestDtreeScore:
    """Test tree scoring."""

    def test_score_perfect(self):
        """Test score = 1.0 for perfect predictions."""
        data = json.dumps({
            "X": [[0], [1], [2], [3]],
            "y": [0, 0, 1, 1],
            "tree": {
                "feature": 0,
                "threshold": 1.5,
                "left": {"class": 0},
                "right": {"class": 1}
            }
        })
        stdout, stderr, code = run(["score"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["accuracy"] == 1.0


class TestDtreeHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "DecisionTree" in stdout or "tree" in stdout.lower()

    def test_subcommand_help(self):
        """Test subcommand help."""
        stdout, stderr, code = run(["fit", "--help"])
        assert code == 0


class TestDtreeEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["fit"], "not json")
        assert code == 1

    def test_single_class(self):
        """Test fitting with single class."""
        data = json.dumps({
            "X": [[0], [1], [2]],
            "y": [0, 0, 0]
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
