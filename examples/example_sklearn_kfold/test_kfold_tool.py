#!/usr/bin/env python3
"""EXTREME TDD: Tests for sklearn KFold cross-validation CLI.

Academic Reference: Pedregosa et al. (2011) sklearn model selection [1]
Tests K-fold cross-validation splitting and scoring.
"""

import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "kfold_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestKfoldSplit:
    """Test K-fold splitting."""

    def test_split_5fold(self):
        """Test 5-fold split."""
        data = json.dumps({
            "n_samples": 10,
            "n_splits": 5
        })
        stdout, stderr, code = run(["split"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "folds" in result
        assert len(result["folds"]) == 5
        # Each fold should have 2 test samples
        for fold in result["folds"]:
            assert len(fold["test"]) == 2
            assert len(fold["train"]) == 8

    def test_split_default_5fold(self):
        """Test default n_splits=5."""
        data = json.dumps({"n_samples": 10})
        stdout, stderr, code = run(["split"], data)
        assert code == 0
        result = json.loads(stdout)
        assert len(result["folds"]) == 5

    def test_split_no_overlap(self):
        """Test that folds don't overlap."""
        data = json.dumps({
            "n_samples": 6,
            "n_splits": 3
        })
        stdout, stderr, code = run(["split"], data)
        assert code == 0
        result = json.loads(stdout)
        all_test = []
        for fold in result["folds"]:
            all_test.extend(fold["test"])
        # All indices should appear exactly once in test sets
        assert sorted(all_test) == list(range(6))


class TestKfoldCrossValScore:
    """Test cross_val_score equivalent."""

    def test_cross_val_score_linreg(self):
        """Test cross-validation with linear data."""
        data = json.dumps({
            "X": [[1], [2], [3], [4], [5], [6], [7], [8], [9], [10]],
            "y": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
            "model": "linear_regression",
            "n_splits": 5
        })
        stdout, stderr, code = run(["cross-val-score"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "scores" in result
        assert len(result["scores"]) == 5
        # Perfect linear data should have high R²
        assert result["mean_score"] > 0.9

    def test_cross_val_score_returns_mean_std(self):
        """Test that mean and std are returned."""
        data = json.dumps({
            "X": [[1], [2], [3], [4], [5], [6]],
            "y": [1, 2, 3, 4, 5, 6],
            "model": "linear_regression",
            "n_splits": 3
        })
        stdout, stderr, code = run(["cross-val-score"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "mean_score" in result
        assert "std_score" in result


class TestKfoldHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "KFold" in stdout or "fold" in stdout.lower()

    def test_subcommand_help(self):
        """Test subcommand help."""
        stdout, stderr, code = run(["split", "--help"])
        assert code == 0


class TestKfoldEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["split"], "not json")
        assert code == 1

    def test_k_greater_than_n_fails(self):
        """Test k > n_samples fails."""
        data = json.dumps({
            "n_samples": 3,
            "n_splits": 5
        })
        stdout, stderr, code = run(["split"], data)
        assert code == 1
