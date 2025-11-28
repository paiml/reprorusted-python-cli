#!/usr/bin/env python3
"""EXTREME TDD: Tests for PyTorch MSELoss CLI.

Academic Reference: Paszke et al. (2019) PyTorch [2]
Tests mean squared error loss function.
"""

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "mseloss_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestMSEForward:
    """Test MSE loss forward pass."""

    def test_mse_zero_loss(self):
        """Test MSE = 0 when pred == target."""
        data = json.dumps({
            "pred": [1.0, 2.0, 3.0],
            "target": [1.0, 2.0, 3.0]
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["loss"] == 0.0

    def test_mse_nonzero_loss(self):
        """Test MSE calculation."""
        # MSE = ((1-2)^2 + (2-3)^2) / 2 = 2/2 = 1
        data = json.dumps({
            "pred": [1.0, 2.0],
            "target": [2.0, 3.0]
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["loss"] - 1.0) < 0.01

    def test_mse_sum_reduction(self):
        """Test MSE with sum reduction."""
        # Sum = (1-2)^2 + (2-3)^2 = 2
        data = json.dumps({
            "pred": [1.0, 2.0],
            "target": [2.0, 3.0],
            "reduction": "sum"
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["loss"] - 2.0) < 0.01


class TestMSEBackward:
    """Test MSE loss backward pass."""

    def test_mse_gradient(self):
        """Test MSE gradient computation."""
        # d/dpred MSE = 2(pred - target) / n
        data = json.dumps({
            "pred": [2.0, 4.0],
            "target": [1.0, 2.0]
        })
        stdout, stderr, code = run(["backward"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "grad" in result
        # grad = 2 * (pred - target) / n = [2*(2-1)/2, 2*(4-2)/2] = [1, 2]
        assert abs(result["grad"][0] - 1.0) < 0.01
        assert abs(result["grad"][1] - 2.0) < 0.01


class TestL1Loss:
    """Test L1 loss (MAE)."""

    def test_l1_forward(self):
        """Test L1 loss forward."""
        # MAE = (|1-2| + |2-4|) / 2 = 3/2 = 1.5
        data = json.dumps({
            "pred": [1.0, 2.0],
            "target": [2.0, 4.0]
        })
        stdout, stderr, code = run(["l1-forward"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["loss"] - 1.5) < 0.01


class TestCrossEntropy:
    """Test cross-entropy loss."""

    def test_cross_entropy(self):
        """Test cross-entropy loss."""
        data = json.dumps({
            "logits": [2.0, 1.0, 0.1],  # Raw scores
            "target": 0  # Class index
        })
        stdout, stderr, code = run(["cross-entropy"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "loss" in result
        assert result["loss"] > 0


class TestHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "MSE" in stdout or "loss" in stdout.lower()


class TestEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["forward"], "not json")
        assert code == 1

    def test_shape_mismatch_fails(self):
        """Test shape mismatch fails."""
        data = json.dumps({
            "pred": [1.0, 2.0],
            "target": [1.0]
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 1
