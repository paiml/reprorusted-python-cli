#!/usr/bin/env python3
"""EXTREME TDD: Tests for PyTorch nn.Sequential CLI.

Academic Reference: Paszke et al. (2019) PyTorch [2]
Tests sequential layer chaining.
"""

import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "sequential_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestSequentialForward:
    """Test sequential forward pass."""

    def test_forward_linear_relu(self):
        """Test Linear -> ReLU chain."""
        data = json.dumps({
            "x": [1.0, -1.0],
            "layers": [
                {"type": "linear", "weight": [[1.0, 0.0], [0.0, 1.0]], "bias": [0.0, 0.0]},
                {"type": "relu"}
            ]
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        # Linear: [1, -1], ReLU: [1, 0]
        assert result["output"] == [1.0, 0.0]

    def test_forward_mlp(self):
        """Test MLP: Linear -> ReLU -> Linear."""
        data = json.dumps({
            "x": [1.0, 1.0],
            "layers": [
                {"type": "linear", "weight": [[1.0, 1.0]], "bias": [0.0]},  # 2->1
                {"type": "relu"},
                {"type": "linear", "weight": [[2.0]], "bias": [1.0]}  # 1->1
            ]
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        # Linear: [2], ReLU: [2], Linear: [2*2+1] = [5]
        assert result["output"] == [5.0]


class TestSequentialBuild:
    """Test building sequential model."""

    def test_build_mlp(self):
        """Test building MLP architecture."""
        data = json.dumps({
            "architecture": [
                {"type": "linear", "in": 4, "out": 2},
                {"type": "relu"},
                {"type": "linear", "in": 2, "out": 1}
            ],
            "random_state": 42
        })
        stdout, stderr, code = run(["build"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "layers" in result
        assert len(result["layers"]) == 3


class TestHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "Sequential" in stdout or "sequential" in stdout.lower()


class TestEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["forward"], "not json")
        assert code == 1

    def test_empty_layers(self):
        """Test empty layers list."""
        data = json.dumps({"x": [1.0], "layers": []})
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["output"] == [1.0]
