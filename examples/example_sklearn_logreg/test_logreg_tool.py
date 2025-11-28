#!/usr/bin/env python3
"""EXTREME TDD: Tests for sklearn LogisticRegression CLI.

Academic Reference: Pedregosa et al. (2011) sklearn API design [1]
Tests the fit/predict/score pattern for binary classification.
"""

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "logreg_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestLogregFit:
    """Test model fitting."""

    def test_fit_simple_binary(self):
        """Test fitting on linearly separable binary data."""
        # Class 0: x < 5, Class 1: x >= 5
        data = json.dumps({
            "X": [[1], [2], [3], [4], [6], [7], [8], [9]],
            "y": [0, 0, 0, 0, 1, 1, 1, 1]
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "coef" in result
        assert "intercept" in result
        assert len(result["coef"]) == 1

    def test_fit_multivariate(self):
        """Test fitting on multivariate binary data."""
        data = json.dumps({
            "X": [[0, 0], [0, 1], [1, 0], [1, 1], [5, 5], [5, 6], [6, 5], [6, 6]],
            "y": [0, 0, 0, 0, 1, 1, 1, 1]
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert len(result["coef"]) == 2

    def test_fit_empty_data_fails(self):
        """Test that fitting on empty data fails."""
        data = json.dumps({"X": [], "y": []})
        stdout, stderr, code = run(["fit"], data)
        assert code == 1
        assert "empty" in stderr.lower() or "error" in stderr.lower()


class TestLogregPredict:
    """Test model prediction."""

    def test_predict_binary(self):
        """Test prediction with provided coefficients."""
        # Sigmoid(coef * x + intercept) > 0.5 => class 1
        data = json.dumps({
            "X": [[1], [10]],
            "coef": [1.0],
            "intercept": -5.0  # Decision boundary at x=5
        })
        stdout, stderr, code = run(["predict"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "predictions" in result
        assert result["predictions"][0] == 0  # x=1 < 5
        assert result["predictions"][1] == 1  # x=10 > 5

    def test_predict_proba(self):
        """Test probability prediction."""
        data = json.dumps({
            "X": [[5]],  # At decision boundary
            "coef": [1.0],
            "intercept": -5.0
        })
        stdout, stderr, code = run(["predict-proba"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "probabilities" in result
        # At boundary, probability should be ~0.5
        assert abs(result["probabilities"][0] - 0.5) < 0.1


class TestLogregScore:
    """Test model scoring (accuracy)."""

    def test_score_perfect(self):
        """Test accuracy = 1.0 for perfect predictions."""
        data = json.dumps({
            "X": [[1], [2], [8], [9]],
            "y": [0, 0, 1, 1],
            "coef": [1.0],
            "intercept": -5.0
        })
        stdout, stderr, code = run(["score"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "accuracy" in result
        assert result["accuracy"] == 1.0

    def test_score_imperfect(self):
        """Test accuracy < 1.0 for imperfect predictions."""
        data = json.dumps({
            "X": [[1], [5], [9]],  # x=5 is at boundary
            "y": [0, 0, 1],
            "coef": [1.0],
            "intercept": -5.0
        })
        stdout, stderr, code = run(["score"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["accuracy"] < 1.0


class TestLogregFitPredict:
    """Test combined fit-predict pipeline."""

    def test_fit_predict_pipeline(self):
        """Test fitting and predicting in one command."""
        data = json.dumps({
            "X_train": [[1], [2], [3], [7], [8], [9]],
            "y_train": [0, 0, 0, 1, 1, 1],
            "X_test": [[0], [10]]
        })
        stdout, stderr, code = run(["fit-predict"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "predictions" in result
        assert result["predictions"][0] == 0  # x=0 -> class 0
        assert result["predictions"][1] == 1  # x=10 -> class 1


class TestLogregFitScore:
    """Test combined fit-score pipeline."""

    def test_fit_score_pipeline(self):
        """Test fitting and scoring in one command."""
        data = json.dumps({
            "X": [[1], [2], [3], [7], [8], [9]],
            "y": [0, 0, 0, 1, 1, 1]
        })
        stdout, stderr, code = run(["fit-score"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "accuracy" in result
        assert result["accuracy"] >= 0.8  # Should be high for separable data


class TestLogregHelp:
    """Test help and usage messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "LogisticRegression" in stdout or "logistic" in stdout.lower()
        assert "fit" in stdout
        assert "predict" in stdout

    def test_subcommand_help(self):
        """Test subcommand help."""
        stdout, stderr, code = run(["fit", "--help"])
        assert code == 0


class TestLogregEdgeCases:
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

    def test_non_binary_labels_handled(self):
        """Test that non-binary labels are rejected or handled."""
        data = json.dumps({
            "X": [[1], [2], [3]],
            "y": [0, 1, 2]  # 3 classes
        })
        stdout, stderr, code = run(["fit"], data)
        # Should either fail or handle multiclass
        # For simplicity, binary only is acceptable
        if code == 0:
            result = json.loads(stdout)
            assert "coef" in result


class TestLogregParameters:
    """Test learning parameters."""

    def test_learning_rate(self):
        """Test custom learning rate."""
        data = json.dumps({
            "X": [[1], [2], [8], [9]],
            "y": [0, 0, 1, 1],
            "learning_rate": 0.1,
            "max_iter": 100
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0

    def test_max_iterations(self):
        """Test custom max iterations."""
        data = json.dumps({
            "X": [[1], [2], [8], [9]],
            "y": [0, 0, 1, 1],
            "max_iter": 500
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
