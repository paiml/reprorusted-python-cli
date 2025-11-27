#!/usr/bin/env python3
"""Sequential model CLI tool.

A CLI for PyTorch-style nn.Sequential layer chaining.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: Paszke et al. (2019) PyTorch [2]

Usage:
    echo '{"x": [1, -1], "layers": [{"type": "linear", "weight": [[1,0],[0,1]], "bias": [0,0]}, {"type": "relu"}]}' | python sequential_tool.py forward
"""

import argparse
import json
import math
import random
import sys
from typing import Any


def linear_forward(x: list[float], weight: list[list[float]], bias: list[float]) -> list[float]:
    """Linear layer forward."""
    out = []
    for i in range(len(weight)):
        val = bias[i]
        for j in range(len(x)):
            val += weight[i][j] * x[j]
        out.append(val)
    return out


def relu_forward(x: list[float]) -> list[float]:
    """ReLU activation."""
    return [max(0.0, xi) for xi in x]


def sigmoid_forward(x: list[float]) -> list[float]:
    """Sigmoid activation."""
    return [
        1.0 / (1.0 + math.exp(-xi)) if xi >= 0 else math.exp(xi) / (1.0 + math.exp(xi)) for xi in x
    ]


def tanh_forward(x: list[float]) -> list[float]:
    """Tanh activation."""
    return [math.tanh(xi) for xi in x]


def forward(x: list[float], layers: list[dict[str, Any]]) -> list[float]:
    """Forward pass through sequential layers."""
    output = x
    for layer in layers:
        layer_type = layer["type"]
        if layer_type == "linear":
            output = linear_forward(output, layer["weight"], layer["bias"])
        elif layer_type == "relu":
            output = relu_forward(output)
        elif layer_type == "sigmoid":
            output = sigmoid_forward(output)
        elif layer_type == "tanh":
            output = tanh_forward(output)
        else:
            raise ValueError(f"Unknown layer type: {layer_type}")
    return output


def init_linear(in_features: int, out_features: int) -> dict[str, Any]:
    """Initialize linear layer."""
    std = math.sqrt(2.0 / in_features)
    bound = math.sqrt(3.0) * std
    weight = [
        [random.uniform(-bound, bound) for _ in range(in_features)] for _ in range(out_features)
    ]
    bias_bound = 1.0 / math.sqrt(in_features)
    bias = [random.uniform(-bias_bound, bias_bound) for _ in range(out_features)]
    return {"type": "linear", "weight": weight, "bias": bias}


def build(architecture: list[dict[str, Any]], random_state: int = None) -> list[dict[str, Any]]:
    """Build sequential model from architecture spec."""
    if random_state is not None:
        random.seed(random_state)

    layers = []
    for spec in architecture:
        if spec["type"] == "linear":
            layers.append(init_linear(spec["in"], spec["out"]))
        else:
            layers.append({"type": spec["type"]})
    return layers


def cmd_forward(args: argparse.Namespace) -> None:
    """Handle forward subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "x" not in data or "layers" not in data:
        print("Error: Missing 'x' or 'layers'", file=sys.stderr)
        sys.exit(1)

    try:
        output = forward(data["x"], data["layers"])
        print(json.dumps({"output": output}))
    except (ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_build(args: argparse.Namespace) -> None:
    """Handle build subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "architecture" not in data:
        print("Error: Missing 'architecture'", file=sys.stderr)
        sys.exit(1)

    random_state = data.get("random_state", None)
    layers = build(data["architecture"], random_state)
    print(json.dumps({"layers": layers}))


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sequential CLI - nn.Sequential layer chaining (PyTorch-compatible)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("forward", help="Forward pass").set_defaults(func=cmd_forward)
    subparsers.add_parser("build", help="Build model from architecture").set_defaults(
        func=cmd_build
    )

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
