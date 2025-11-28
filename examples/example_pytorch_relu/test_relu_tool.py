#!/usr/bin/env python3
"""EXTREME TDD: Tests for PyTorch activation functions CLI.

Academic Reference: He et al. (2015) Deep Rectifiers [5]
Tests ReLU, Sigmoid, Tanh activation functions.
"""

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "relu_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestRelu:
    """Test ReLU activation."""

    def test_relu_positive(self):
        """Test ReLU on positive values."""
        data = json.dumps({"x": [1.0, 2.0, 3.0]})
        stdout, stderr, code = run(["relu"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["output"] == [1.0, 2.0, 3.0]

    def test_relu_negative(self):
        """Test ReLU on negative values."""
        data = json.dumps({"x": [-1.0, -2.0, -3.0]})
        stdout, stderr, code = run(["relu"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["output"] == [0.0, 0.0, 0.0]

    def test_relu_mixed(self):
        """Test ReLU on mixed values."""
        data = json.dumps({"x": [-1.0, 0.0, 1.0]})
        stdout, stderr, code = run(["relu"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["output"] == [0.0, 0.0, 1.0]


class TestSigmoid:
    """Test Sigmoid activation."""

    def test_sigmoid_zero(self):
        """Test sigmoid(0) = 0.5."""
        data = json.dumps({"x": [0.0]})
        stdout, stderr, code = run(["sigmoid"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["output"][0] - 0.5) < 0.01

    def test_sigmoid_bounds(self):
        """Test sigmoid output is in (0, 1)."""
        data = json.dumps({"x": [-10.0, 0.0, 10.0]})
        stdout, stderr, code = run(["sigmoid"], data)
        assert code == 0
        result = json.loads(stdout)
        for val in result["output"]:
            assert 0 < val < 1


class TestTanh:
    """Test Tanh activation."""

    def test_tanh_zero(self):
        """Test tanh(0) = 0."""
        data = json.dumps({"x": [0.0]})
        stdout, stderr, code = run(["tanh"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(result["output"][0]) < 0.01

    def test_tanh_bounds(self):
        """Test tanh output is in (-1, 1)."""
        data = json.dumps({"x": [-10.0, 0.0, 10.0]})
        stdout, stderr, code = run(["tanh"], data)
        assert code == 0
        result = json.loads(stdout)
        for val in result["output"]:
            assert -1 < val < 1


class TestSoftmax:
    """Test Softmax activation."""

    def test_softmax_sums_to_one(self):
        """Test softmax sums to 1."""
        data = json.dumps({"x": [1.0, 2.0, 3.0]})
        stdout, stderr, code = run(["softmax"], data)
        assert code == 0
        result = json.loads(stdout)
        assert abs(sum(result["output"]) - 1.0) < 0.01

    def test_softmax_all_positive(self):
        """Test softmax outputs are all positive."""
        data = json.dumps({"x": [-1.0, 0.0, 1.0]})
        stdout, stderr, code = run(["softmax"], data)
        assert code == 0
        result = json.loads(stdout)
        for val in result["output"]:
            assert val > 0


class TestHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "relu" in stdout.lower()


class TestEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["relu"], "not json")
        assert code == 1
