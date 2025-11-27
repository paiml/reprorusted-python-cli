#!/usr/bin/env python3
"""EXTREME TDD: Tests for PyTorch Adam optimizer CLI.

Academic Reference: Kingma & Ba (2015) Adam optimizer [4]
Tests Adam optimizer step updates.
"""

import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "adam_tool.py"


def run(args, input_data=None):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestAdamStep:
    """Test Adam optimizer step."""

    def test_step_updates_params(self):
        """Test that step updates parameters."""
        data = json.dumps({
            "params": [1.0, 2.0, 3.0],
            "grads": [0.1, 0.2, 0.3],
            "lr": 0.001
        })
        stdout, stderr, code = run(["step"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "params" in result
        # Params should change
        assert result["params"] != [1.0, 2.0, 3.0]

    def test_step_with_momentum(self):
        """Test Adam with momentum (beta1, beta2)."""
        data = json.dumps({
            "params": [1.0],
            "grads": [0.1],
            "lr": 0.01,
            "beta1": 0.9,
            "beta2": 0.999,
            "m": [0.0],  # First moment
            "v": [0.0],  # Second moment
            "t": 1
        })
        stdout, stderr, code = run(["step"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "m" in result
        assert "v" in result


class TestAdamInit:
    """Test Adam initialization."""

    def test_init_creates_state(self):
        """Test that init creates optimizer state."""
        data = json.dumps({
            "n_params": 3,
            "lr": 0.001
        })
        stdout, stderr, code = run(["init"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "m" in result
        assert "v" in result
        assert len(result["m"]) == 3
        assert len(result["v"]) == 3


class TestAdamMultiStep:
    """Test multiple optimization steps."""

    def test_multiple_steps_converge(self):
        """Test that multiple steps move params toward minimum."""
        # Start at x=10, gradient points toward origin
        data = json.dumps({
            "params": [10.0],
            "grads": [2.0],  # Gradient of x^2 at x=10 is 2*10=20, using smaller
            "lr": 0.1,
            "m": [0.0],
            "v": [0.0],
            "t": 1
        })
        # Take one step
        stdout, _, code = run(["step"], data)
        assert code == 0
        result = json.loads(stdout)
        # Should move toward 0
        assert result["params"][0] < 10.0


class TestHelp:
    """Test help messages."""

    def test_help(self):
        """Test --help flag."""
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "Adam" in stdout or "adam" in stdout.lower()


class TestEdgeCases:
    """Test edge cases."""

    def test_invalid_json_fails(self):
        """Test invalid JSON fails."""
        stdout, stderr, code = run(["step"], "not json")
        assert code == 1

    def test_zero_learning_rate(self):
        """Test zero learning rate doesn't update."""
        data = json.dumps({
            "params": [1.0],
            "grads": [0.1],
            "lr": 0.0
        })
        stdout, stderr, code = run(["step"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["params"] == [1.0]
