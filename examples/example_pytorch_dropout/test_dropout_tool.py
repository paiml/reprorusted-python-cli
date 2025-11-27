#!/usr/bin/env python3
"""EXTREME TDD: Tests for PyTorch Dropout CLI."""

import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "dropout_tool.py"


def run(args, input_data=None):
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestDropoutForward:
    def test_forward_train_drops_some(self):
        """Test that dropout zeros some values in training."""
        data = json.dumps({
            "x": [1.0] * 100,
            "p": 0.5,
            "training": True,
            "random_state": 42
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        # Some values should be zero
        zeros = sum(1 for v in result["output"] if v == 0)
        assert zeros > 20  # Roughly 50% should be zero

    def test_forward_eval_no_drop(self):
        """Test that dropout doesn't drop in eval mode."""
        data = json.dumps({
            "x": [1.0, 2.0, 3.0],
            "p": 0.5,
            "training": False
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        assert result["output"] == [1.0, 2.0, 3.0]


class TestHelp:
    def test_help(self):
        stdout, stderr, code = run(["--help"])
        assert code == 0


class TestEdgeCases:
    def test_invalid_json_fails(self):
        stdout, stderr, code = run(["forward"], "not json")
        assert code == 1
