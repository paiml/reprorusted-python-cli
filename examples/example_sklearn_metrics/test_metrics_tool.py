#!/usr/bin/env python3
"""EXTREME TDD: Tests for sklearn metrics CLI.

Academic Reference: Pedregosa et al. (2011) sklearn metrics [1]
Tests classification and regression metrics.
"""

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "metrics_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestAccuracy:
    """Test accuracy score."""

    def test_accuracy_perfect(self):
        """Test accuracy = 1.0 for perfect predictions."""
        data = json.dumps({
            "y_true": [0, 1, 1, 0],
            "y_pred": [0, 1, 1, 0]
        })
        stdout, stderr, code = run(["accuracy"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["accuracy"] == 1.0

    def test_accuracy_zero(self):
        """Test accuracy = 0.0 for all wrong."""
        data = json.dumps({
            "y_true": [0, 0, 0, 0],
            "y_pred": [1, 1, 1, 1]
        })
        stdout, stderr, code = run(["accuracy"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["accuracy"] == 0.0

    def test_accuracy_partial(self):
        """Test accuracy for partial correctness."""
        data = json.dumps({
            "y_true": [0, 1, 1, 0],
            "y_pred": [0, 1, 0, 0]  # 3/4 correct
        })
        stdout, stderr, code = run(["accuracy"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["accuracy"] - 0.75) < 0.01


class TestPrecision:
    """Test precision score."""

    def test_precision_perfect(self):
        """Test precision = 1.0 for no false positives."""
        data = json.dumps({
            "y_true": [1, 1, 0, 0],
            "y_pred": [1, 1, 0, 0]
        })
        stdout, stderr, code = run(["precision"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["precision"] == 1.0

    def test_precision_with_fp(self):
        """Test precision with false positives."""
        # TP=1, FP=1 -> precision = 1/2
        data = json.dumps({
            "y_true": [1, 0, 0, 0],
            "y_pred": [1, 1, 0, 0]
        })
        stdout, stderr, code = run(["precision"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["precision"] - 0.5) < 0.01


class TestRecall:
    """Test recall score."""

    def test_recall_perfect(self):
        """Test recall = 1.0 for no false negatives."""
        data = json.dumps({
            "y_true": [1, 1, 0, 0],
            "y_pred": [1, 1, 0, 0]
        })
        stdout, stderr, code = run(["recall"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["recall"] == 1.0

    def test_recall_with_fn(self):
        """Test recall with false negatives."""
        # TP=1, FN=1 -> recall = 1/2
        data = json.dumps({
            "y_true": [1, 1, 0, 0],
            "y_pred": [1, 0, 0, 0]
        })
        stdout, stderr, code = run(["recall"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["recall"] - 0.5) < 0.01


class TestF1:
    """Test F1 score."""

    def test_f1_perfect(self):
        """Test F1 = 1.0 for perfect predictions."""
        data = json.dumps({
            "y_true": [1, 1, 0, 0],
            "y_pred": [1, 1, 0, 0]
        })
        stdout, stderr, code = run(["f1"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["f1"] == 1.0

    def test_f1_harmonic_mean(self):
        """Test F1 is harmonic mean of precision and recall."""
        # P=0.5, R=1.0 -> F1 = 2 * 0.5 * 1.0 / (0.5 + 1.0) = 2/3
        data = json.dumps({
            "y_true": [1, 0, 0, 0],
            "y_pred": [1, 1, 0, 0]
        })
        stdout, stderr, code = run(["f1"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["f1"] - 0.667) < 0.01


class TestConfusionMatrix:
    """Test confusion matrix."""

    def test_confusion_matrix_binary(self):
        """Test binary confusion matrix."""
        data = json.dumps({
            "y_true": [0, 0, 1, 1],
            "y_pred": [0, 1, 0, 1]
        })
        stdout, stderr, code = run(["confusion-matrix"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "matrix" in result
        # [[TN, FP], [FN, TP]] = [[1, 1], [1, 1]]
        assert result["matrix"][0][0] == 1  # TN
        assert result["matrix"][0][1] == 1  # FP
        assert result["matrix"][1][0] == 1  # FN
        assert result["matrix"][1][1] == 1  # TP


class TestMSE:
    """Test mean squared error."""

    def test_mse_zero(self):
        """Test MSE = 0 for perfect predictions."""
        data = json.dumps({
            "y_true": [1.0, 2.0, 3.0],
            "y_pred": [1.0, 2.0, 3.0]
        })
        stdout, stderr, code = run(["mse"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["mse"] == 0.0

    def test_mse_nonzero(self):
        """Test MSE calculation."""
        # MSE = ((1-2)^2 + (2-3)^2 + (3-4)^2) / 3 = 3/3 = 1
        data = json.dumps({
            "y_true": [1.0, 2.0, 3.0],
            "y_pred": [2.0, 3.0, 4.0]
        })
        stdout, stderr, code = run(["mse"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["mse"] - 1.0) < 0.01


class TestR2:
    """Test R-squared score."""

    def test_r2_perfect(self):
        """Test R2 = 1.0 for perfect predictions."""
        data = json.dumps({
            "y_true": [1.0, 2.0, 3.0],
            "y_pred": [1.0, 2.0, 3.0]
        })
        stdout, stderr, code = run(["r2"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["r2"] - 1.0) < 0.01


class TestHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "accuracy" in stdout.lower()
        assert "precision" in stdout.lower()

    def test_subcommand_help(self):
        """Test subcommand help."""
        stdout, stderr, code = run(["accuracy", "--help"])
        assert code == 0


class TestEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["accuracy"], "not json")
        assert code == 1

    def test_length_mismatch_fails(self):
        """Test length mismatch fails."""
        data = json.dumps({
            "y_true": [0, 1, 1],
            "y_pred": [0, 1]
        })
        stdout, stderr, code = run(["accuracy"], data)
        assert code == 1
