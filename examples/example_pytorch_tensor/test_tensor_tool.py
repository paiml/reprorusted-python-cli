#!/usr/bin/env python3
"""EXTREME TDD: Tests for PyTorch tensor operations CLI.

Academic Reference: Paszke et al. (2019) PyTorch [2]
Tests tensor creation and basic operations.
"""

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "tensor_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestTensorCreate:
    """Test tensor creation."""

    def test_create_from_list(self):
        """Test creating tensor from list."""
        data = json.dumps({"data": [1.0, 2.0, 3.0]})
        stdout, stderr, code = run(["create"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "tensor" in result
        assert result["tensor"] == [1.0, 2.0, 3.0]
        assert result["shape"] == [3]

    def test_create_2d(self):
        """Test creating 2D tensor."""
        data = json.dumps({"data": [[1, 2], [3, 4]]})
        stdout, stderr, code = run(["create"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["shape"] == [2, 2]

    def test_zeros(self):
        """Test creating zeros tensor."""
        data = json.dumps({"shape": [2, 3]})
        stdout, stderr, code = run(["zeros"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["tensor"] == [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]

    def test_ones(self):
        """Test creating ones tensor."""
        data = json.dumps({"shape": [2, 2]})
        stdout, stderr, code = run(["ones"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["tensor"] == [[1.0, 1.0], [1.0, 1.0]]


class TestTensorOps:
    """Test tensor operations."""

    def test_add(self):
        """Test element-wise addition."""
        data = json.dumps({
            "a": [1.0, 2.0, 3.0],
            "b": [4.0, 5.0, 6.0]
        })
        stdout, stderr, code = run(["add"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["tensor"] == [5.0, 7.0, 9.0]

    def test_mul(self):
        """Test element-wise multiplication."""
        data = json.dumps({
            "a": [1.0, 2.0, 3.0],
            "b": [2.0, 3.0, 4.0]
        })
        stdout, stderr, code = run(["mul"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["tensor"] == [2.0, 6.0, 12.0]

    def test_matmul(self):
        """Test matrix multiplication."""
        data = json.dumps({
            "a": [[1, 2], [3, 4]],
            "b": [[5, 6], [7, 8]]
        })
        stdout, stderr, code = run(["matmul"], data)
        assert code == 0
        result = json.loads(stdout)
        # [[1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]]
        assert result["tensor"] == [[19, 22], [43, 50]]


class TestTensorReduce:
    """Test reduction operations."""

    def test_sum(self):
        """Test sum reduction."""
        data = json.dumps({"tensor": [1.0, 2.0, 3.0, 4.0]})
        stdout, stderr, code = run(["sum"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["value"] == 10.0

    def test_mean(self):
        """Test mean reduction."""
        data = json.dumps({"tensor": [1.0, 2.0, 3.0, 4.0]})
        stdout, stderr, code = run(["mean"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["value"] == 2.5


class TestTensorHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "tensor" in stdout.lower()

    def test_subcommand_help(self):
        """Test subcommand help."""
        stdout, stderr, code = run(["add", "--help"])
        assert code == 0


class TestTensorEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["create"], "not json")
        assert code == 1

    def test_shape_mismatch_fails(self):
        """Test shape mismatch in operations fails."""
        data = json.dumps({
            "a": [1.0, 2.0, 3.0],
            "b": [1.0, 2.0]
        })
        stdout, stderr, code = run(["add"], data)
        assert code == 1
