#!/usr/bin/env python3
"""EXTREME TDD: Tests for PyTorch nn.Linear CLI.

Academic Reference: He et al. (2015) Weight initialization [5]
Tests dense/linear layer forward pass.
"""

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "linear_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestLinearForward:
    """Test forward pass."""

    def test_forward_simple(self):
        """Test y = Wx + b."""
        data = json.dumps({
            "x": [1.0, 2.0],
            "weight": [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]],  # 3x2
            "bias": [0.0, 0.0, 0.0]
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "output" in result
        # W @ x = [1, 2, 3]
        assert result["output"] == [1.0, 2.0, 3.0]

    def test_forward_with_bias(self):
        """Test with non-zero bias."""
        data = json.dumps({
            "x": [1.0, 1.0],
            "weight": [[1.0, 1.0]],
            "bias": [1.0]
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        # 1*1 + 1*1 + 1 = 3
        assert result["output"] == [3.0]

    def test_forward_batch(self):
        """Test batch input."""
        data = json.dumps({
            "x": [[1.0, 0.0], [0.0, 1.0]],  # 2 samples
            "weight": [[1.0, 2.0]],  # 1x2
            "bias": [0.0]
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        # [1*1+0*2, 0*1+1*2] = [1, 2]
        assert result["output"] == [[1.0], [2.0]]


class TestLinearInit:
    """Test weight initialization."""

    def test_init_creates_weights(self):
        """Test that init creates weight and bias."""
        data = json.dumps({
            "in_features": 3,
            "out_features": 2
        })
        stdout, stderr, code = run(["init"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "weight" in result
        assert "bias" in result
        assert len(result["weight"]) == 2
        assert len(result["weight"][0]) == 3
        assert len(result["bias"]) == 2


class TestLinearHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "Linear" in stdout or "linear" in stdout.lower()


class TestLinearEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["forward"], "not json")
        assert code == 1

    def test_shape_mismatch_fails(self):
        """Test shape mismatch fails."""
        data = json.dumps({
            "x": [1.0, 2.0, 3.0],  # 3 features
            "weight": [[1.0, 1.0]],  # expects 2 features
            "bias": [0.0]
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 1
