#!/usr/bin/env python3
"""EXTREME TDD: Tests for PyTorch autograd CLI.

Academic Reference: Baydin et al. (2018) Automatic Differentiation [3]
Tests backward pass and gradient computation.
"""

import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "autograd_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestBackward:
    """Test backward pass."""

    def test_backward_simple(self):
        """Test gradient of y = x^2."""
        # y = x^2, dy/dx = 2x
        data = json.dumps({
            "expression": "x**2",
            "x": 3.0
        })
        stdout, stderr, code = run(["backward"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "grad" in result
        assert abs(result["grad"] - 6.0) < 0.01  # 2*3 = 6

    def test_backward_chain(self):
        """Test chain rule: y = (x^2)^2 = x^4."""
        data = json.dumps({
            "expression": "x**4",
            "x": 2.0
        })
        stdout, stderr, code = run(["backward"], data)
        assert code == 0
        result = json.loads(stdout)
        # dy/dx = 4x^3 = 4*8 = 32
        assert abs(result["grad"] - 32.0) < 0.01

    def test_backward_sum(self):
        """Test gradient of sum."""
        data = json.dumps({
            "expression": "sum",
            "x": [1.0, 2.0, 3.0]
        })
        stdout, stderr, code = run(["backward"], data)
        assert code == 0
        result = json.loads(stdout)
        # Gradient of sum is all ones
        assert result["grad"] == [1.0, 1.0, 1.0]


class TestGradient:
    """Test gradient computation."""

    def test_gradient_linear(self):
        """Test gradient of linear function y = 2x + 1."""
        data = json.dumps({
            "expression": "2*x + 1",
            "x": 5.0
        })
        stdout, stderr, code = run(["backward"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["grad"] - 2.0) < 0.01

    def test_gradient_product(self):
        """Test gradient of product y = x * w."""
        data = json.dumps({
            "expression": "x * w",
            "x": 3.0,
            "w": 4.0
        })
        stdout, stderr, code = run(["backward"], data)
        assert code == 0
        result = json.loads(stdout)
        # dy/dx = w = 4, dy/dw = x = 3
        assert abs(result["grad_x"] - 4.0) < 0.01
        assert abs(result["grad_w"] - 3.0) < 0.01


class TestHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "autograd" in stdout.lower() or "gradient" in stdout.lower()


class TestEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["backward"], "not json")
        assert code == 1
