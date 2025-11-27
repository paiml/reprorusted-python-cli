#!/usr/bin/env python3
"""EXTREME TDD: Tests for sklearn LinearRegression CLI.

Academic Reference: Pedregosa et al. (2011) sklearn API design [1]
Tests the fit/predict/score pattern for linear regression.
"""

import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "linreg_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestLinregFit:
    """Test model fitting."""

    def test_fit_simple_data(self):
        """Test fitting on simple linear data: y = 2x + 1."""
        data = json.dumps({
            "X": [[1], [2], [3], [4], [5]],
            "y": [3, 5, 7, 9, 11]
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "coef" in result
        assert "intercept" in result
        # y = 2x + 1, so coef ~= 2, intercept ~= 1
        assert abs(result["coef"][0] - 2.0) < 0.01
        assert abs(result["intercept"] - 1.0) < 0.01

    def test_fit_multivariate(self):
        """Test fitting on multivariate data: y = 1*x1 + 2*x2 + 3."""
        # Non-collinear data: x1 and x2 are independent
        data = json.dumps({
            "X": [[1, 2], [2, 1], [3, 4], [4, 3], [5, 6]],
            "y": [8, 7, 14, 13, 20]  # y = 1*x1 + 2*x2 + 3
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert len(result["coef"]) == 2
        # Coefficients should be approximately [1, 2]
        assert abs(result["coef"][0] - 1.0) < 0.1
        assert abs(result["coef"][1] - 2.0) < 0.1

    def test_fit_empty_data_fails(self):
        """Test that fitting on empty data fails."""
        data = json.dumps({"X": [], "y": []})
        stdout, stderr, code = run(["fit"], data)
        assert code == 1
        assert "empty" in stderr.lower() or "error" in stderr.lower()


class TestLinregPredict:
    """Test model prediction."""

    def test_predict_simple(self):
        """Test prediction with provided coefficients."""
        data = json.dumps({
            "X": [[6], [7], [8]],
            "coef": [2.0],
            "intercept": 1.0
        })
        stdout, stderr, code = run(["predict"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "predictions" in result
        # y = 2x + 1: [13, 15, 17]
        assert abs(result["predictions"][0] - 13.0) < 0.01
        assert abs(result["predictions"][1] - 15.0) < 0.01
        assert abs(result["predictions"][2] - 17.0) < 0.01

    def test_predict_multivariate(self):
        """Test prediction with multivariate coefficients."""
        data = json.dumps({
            "X": [[1, 2], [3, 4]],
            "coef": [1.0, 2.0],
            "intercept": 0.5
        })
        stdout, stderr, code = run(["predict"], data)
        assert code == 0
        result = json.loads(stdout)
        # y = 1*x1 + 2*x2 + 0.5: [5.5, 11.5]
        assert abs(result["predictions"][0] - 5.5) < 0.01
        assert abs(result["predictions"][1] - 11.5) < 0.01


class TestLinregScore:
    """Test model scoring (R-squared)."""

    def test_score_perfect_fit(self):
        """Test R-squared = 1.0 for perfect fit."""
        data = json.dumps({
            "X": [[1], [2], [3], [4], [5]],
            "y": [3, 5, 7, 9, 11],
            "coef": [2.0],
            "intercept": 1.0
        })
        stdout, stderr, code = run(["score"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "r2" in result
        assert abs(result["r2"] - 1.0) < 0.01

    def test_score_imperfect_fit(self):
        """Test R-squared < 1.0 for imperfect fit."""
        data = json.dumps({
            "X": [[1], [2], [3], [4], [5]],
            "y": [3, 5, 8, 9, 11],  # Not perfectly linear
            "coef": [2.0],
            "intercept": 1.0
        })
        stdout, stderr, code = run(["score"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["r2"] < 1.0
        assert result["r2"] > 0.8  # Should still be reasonable


class TestLinregFitPredict:
    """Test combined fit-predict pipeline."""

    def test_fit_predict_pipeline(self):
        """Test fitting and predicting in one command."""
        data = json.dumps({
            "X_train": [[1], [2], [3], [4], [5]],
            "y_train": [3, 5, 7, 9, 11],
            "X_test": [[6], [7], [8]]
        })
        stdout, stderr, code = run(["fit-predict"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "predictions" in result
        assert "coef" in result
        assert "intercept" in result
        # Predictions for [6], [7], [8] with y = 2x + 1
        assert abs(result["predictions"][0] - 13.0) < 0.01


class TestLinregFitScore:
    """Test combined fit-score pipeline."""

    def test_fit_score_pipeline(self):
        """Test fitting and scoring in one command."""
        data = json.dumps({
            "X": [[1], [2], [3], [4], [5]],
            "y": [3, 5, 7, 9, 11]
        })
        stdout, stderr, code = run(["fit-score"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "r2" in result
        assert "coef" in result
        assert abs(result["r2"] - 1.0) < 0.01


class TestLinregHelp:
    """Test help and usage messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "LinearRegression" in stdout or "linear" in stdout.lower()
        assert "fit" in stdout
        assert "predict" in stdout
        assert "score" in stdout

    def test_subcommand_help(self):
        """Test subcommand help."""
        stdout, stderr, code = run(["fit", "--help"])
        assert code == 0
        assert "fit" in stdout.lower()


class TestLinregEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_json_fails(self):
        """Test that invalid JSON input fails gracefully."""
        stdout, stderr, code = run(["fit"], "not valid json")
        assert code == 1
        assert "json" in stderr.lower() or "error" in stderr.lower()

    def test_missing_required_field_fails(self):
        """Test that missing required fields fail gracefully."""
        data = json.dumps({"X": [[1], [2], [3]]})  # Missing y
        stdout, stderr, code = run(["fit"], data)
        assert code == 1

    def test_dimension_mismatch_fails(self):
        """Test that dimension mismatch fails gracefully."""
        data = json.dumps({
            "X": [[1], [2], [3]],
            "y": [1, 2]  # Wrong length
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 1


class TestLinregNumericalStability:
    """Test numerical stability with edge cases."""

    def test_large_values(self):
        """Test with large values."""
        data = json.dumps({
            "X": [[1e6], [2e6], [3e6]],
            "y": [2e6, 4e6, 6e6]
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["coef"][0] - 2.0) < 0.01

    def test_small_values(self):
        """Test with small values."""
        data = json.dumps({
            "X": [[1e-6], [2e-6], [3e-6]],
            "y": [2e-6, 4e-6, 6e-6]
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["coef"][0] - 2.0) < 0.01
