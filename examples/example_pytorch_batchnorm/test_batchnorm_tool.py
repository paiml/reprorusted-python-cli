#!/usr/bin/env python3
"""EXTREME TDD: Tests for PyTorch BatchNorm1d CLI."""

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent / "batchnorm_tool.py"


def run(args, input_data=None):
    result = subprocess.run(
        ["python3", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        input=input_data,
    )
    return result.stdout, result.stderr, result.returncode


class TestBatchNormForward:
    def test_forward_normalizes(self):
        """Test that batch norm normalizes."""
        data = json.dumps({
            "x": [[1, 2], [3, 4], [5, 6]],  # 3 samples, 2 features
            "gamma": [1, 1],
            "beta": [0, 0]
        })
        stdout, stderr, code = run(["forward"], data)
        assert code == 0
        result = json.loads(stdout)
        assert "output" in result
        # Normalized output should have ~zero mean
        output = result["output"]
        mean0 = sum(row[0] for row in output) / len(output)
        assert abs(mean0) < 0.1


class TestHelp:
    def test_help(self):
        stdout, stderr, code = run(["--help"])
        assert code == 0


class TestEdgeCases:
    def test_invalid_json_fails(self):
        stdout, stderr, code = run(["forward"], "not json")
        assert code == 1
