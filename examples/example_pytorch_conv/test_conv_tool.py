#!/usr/bin/env python3
"""EXTREME TDD: Tests for PyTorch Conv2d CLI."""

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "conv_tool.py"


def run(args, input_data=None):
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestConv2dForward:
    def test_forward_simple(self):
        """Test 2D convolution."""
        data = json.dumps({
            "x": [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]],  # 1x3x3
            "kernel": [[[[1, 0], [0, 1]]]],  # 1x1x2x2
            "bias": [0]
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "output" in result


class TestHelp:
    def test_help(self):
        stdout, stderr, code = run(["--help"])
        assert code == 0
        assert "Conv" in stdout or "conv" in stdout.lower()


class TestEdgeCases:
    def test_invalid_json_fails(self):
        stdout, stderr, code = run(["forward"], "not json")
        assert code == 1
