#!/usr/bin/env python3
"""Adam optimizer CLI tool.

A CLI for PyTorch-style Adam optimizer.
Designed for Python-to-Rust transpilation via depyler → aprender.

Academic Reference: Kingma & Ba (2015) Adam optimizer [4]

Usage:
    echo '{"params": [1.0], "grads": [0.1], "lr": 0.001}' | python adam_tool.py step
"""

import argparse
import json
import math
import sys


def adam_step(
    params: list[float],
    grads: list[float],
    m: list[float],
    v: list[float],
    t: int,
    lr: float = 0.001,
    beta1: float = 0.9,
    beta2: float = 0.999,
    eps: float = 1e-8,
) -> tuple:
    """Adam optimizer step.

    Updates parameters and returns new params, m, v.
    """
    new_params = []
    new_m = []
    new_v = []

    for i in range(len(params)):
        # Update biased first moment estimate
        m_i = beta1 * m[i] + (1 - beta1) * grads[i]
        # Update biased second moment estimate
        v_i = beta2 * v[i] + (1 - beta2) * (grads[i] ** 2)

        # Bias correction
        m_hat = m_i / (1 - beta1**t)
        v_hat = v_i / (1 - beta2**t)

        # Update parameter
        param_i = params[i] - lr * m_hat / (math.sqrt(v_hat) + eps)

        new_params.append(param_i)
        new_m.append(m_i)
        new_v.append(v_i)

    return new_params, new_m, new_v


def init_adam(n_params: int) -> dict:
    """Initialize Adam optimizer state."""
    return {
        "m": [0.0] * n_params,
        "v": [0.0] * n_params,
        "t": 0,
    }


def cmd_step(args: argparse.Namespace) -> None:
    """Handle step subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if "params" not in data or "grads" not in data:
        print("Error: Missing 'params' or 'grads'", file=sys.stderr)
        sys.exit(1)

    params = data["params"]
    grads = data["grads"]
    lr = data.get("lr", 0.001)
    beta1 = data.get("beta1", 0.9)
    beta2 = data.get("beta2", 0.999)
    eps = data.get("eps", 1e-8)
    m = data.get("m", [0.0] * len(params))
    v = data.get("v", [0.0] * len(params))
    t = data.get("t", 1)

    if lr == 0:
        print(json.dumps({"params": params, "m": m, "v": v, "t": t}))
        return

    new_params, new_m, new_v = adam_step(params, grads, m, v, t, lr, beta1, beta2, eps)
    print(json.dumps({"params": new_params, "m": new_m, "v": new_v, "t": t + 1}))


def cmd_init(args: argparse.Namespace) -> None:
    """Handle init subcommand."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    n_params = data.get("n_params", 1)
    lr = data.get("lr", 0.001)

    state = init_adam(n_params)
    state["lr"] = lr
    print(json.dumps(state))


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Adam CLI - Adam optimizer (PyTorch-compatible)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("step", help="Optimizer step").set_defaults(func=cmd_step)
    subparsers.add_parser("init", help="Initialize optimizer state").set_defaults(func=cmd_init)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
