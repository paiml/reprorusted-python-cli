#!/usr/bin/env python3
"""EXTREME TDD: Tests for sklearn StandardScaler CLI.

Academic Reference: Pedregosa et al. (2011) sklearn preprocessing [1]
Tests StandardScaler for zero mean, unit variance normalization.
"""

import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "scaler_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestScalerFit:
    """Test scaler fitting."""

    def test_fit_computes_mean_std(self):
        """Test that fit computes mean and std."""
        data = json.dumps({
            "X": [[1, 10], [2, 20], [3, 30], [4, 40], [5, 50]]
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "mean" in result
        assert "std" in result
        assert len(result["mean"]) == 2
        assert len(result["std"]) == 2
        # Mean of [1,2,3,4,5] = 3, [10,20,30,40,50] = 30
        assert abs(result["mean"][0] - 3.0) < 0.01
        assert abs(result["mean"][1] - 30.0) < 0.01

    def test_fit_empty_fails(self):
        """Test that fitting on empty data fails."""
        data = json.dumps({"X": []})
        stdout, stderr, code = run(["fit"], data)
        assert code == 1


class TestScalerTransform:
    """Test scaler transformation."""

    def test_transform_normalizes(self):
        """Test that transform normalizes data."""
        data = json.dumps({
            "X": [[1], [2], [3], [4], [5]],
            "mean": [3.0],
            "std": [1.4142]  # sqrt(2)
        })
        stdout, stderr, code = run(["transform"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "X_scaled" in result
        # x=3 should become 0 (zero mean)
        assert abs(result["X_scaled"][2][0]) < 0.01

    def test_transform_preserves_shape(self):
        """Test that transform preserves data shape."""
        data = json.dumps({
            "X": [[1, 10], [2, 20]],
            "mean": [1.5, 15],
            "std": [0.5, 5]
        })
        stdout, stderr, code = run(["transform"], data)
        assert code == 0
        result = json.loads(stdout)
        assert len(result["X_scaled"]) == 2
        assert len(result["X_scaled"][0]) == 2


class TestScalerFitTransform:
    """Test combined fit-transform."""

    def test_fit_transform(self):
        """Test fit_transform in one step."""
        data = json.dumps({
            "X": [[0, 0], [0, 0], [1, 1], [1, 1]]
        })
        stdout, stderr, code = run(["fit-transform"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "X_scaled" in result
        assert "mean" in result
        assert "std" in result

    def test_fit_transform_zero_mean(self):
        """Test that fit_transform produces zero mean."""
        data = json.dumps({
            "X": [[1], [2], [3], [4], [5]]
        })
        stdout, stderr, code = run(["fit-transform"], data)
        assert code == 0
        result = json.loads(stdout)
        # Mean of transformed data should be ~0
        scaled_mean = sum(row[0] for row in result["X_scaled"]) / len(result["X_scaled"])
        assert abs(scaled_mean) < 0.01


class TestScalerInverseTransform:
    """Test inverse transformation."""

    def test_inverse_transform(self):
        """Test inverse_transform recovers original."""
        data = json.dumps({
            "X_scaled": [[-1.0], [0.0], [1.0]],
            "mean": [5.0],
            "std": [2.0]
        })
        stdout, stderr, code = run(["inverse-transform"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "X" in result
        # -1*2 + 5 = 3, 0*2 + 5 = 5, 1*2 + 5 = 7
        assert abs(result["X"][0][0] - 3.0) < 0.01
        assert abs(result["X"][1][0] - 5.0) < 0.01
        assert abs(result["X"][2][0] - 7.0) < 0.01


class TestScalerHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "StandardScaler" in stdout or "scaler" in stdout.lower()

    def test_subcommand_help(self):
        """Test subcommand help."""
        stdout, stderr, code = run(["fit", "--help"])
        assert code == 0


class TestScalerEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["fit"], "not json")
        assert code == 1

    def test_zero_std_handled(self):
        """Test that zero std (constant feature) is handled."""
        data = json.dumps({
            "X": [[1, 5], [1, 10], [1, 15]]  # First column is constant
        })
        stdout, stderr, code = run(["fit"], data)
        assert code == 0
        result = json.loads(stdout)
        # Std of constant column should be 0 or small
        assert result["std"][0] < 0.01
