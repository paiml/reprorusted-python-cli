# reprorusted-python-cli

**CITL Training Corpus for Depyler**

[![CI](https://github.com/paiml/reprorusted-python-cli/workflows/CI/badge.svg)](https://github.com/paiml/reprorusted-python-cli/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-6745%20passing-brightgreen)](https://github.com/paiml/reprorusted-python-cli/actions)
[![Examples](https://img.shields.io/badge/examples-300+-blue)](https://github.com/paiml/reprorusted-python-cli/tree/main/examples)

## Overview

This repository provides a **Compiler-in-the-Loop (CITL) training corpus** for the [depyler](https://github.com/paiml/depyler) Python-to-Rust transpiler. It contains 300+ Python CLI examples with comprehensive test coverage, designed to train depyler's oracle model through iterative compiler feedback.

**Purpose:**
- Train depyler's CITL oracle model
- Provide diverse Python patterns for transpilation learning
- Generate compiler diagnostics for error→fix prediction
- Export training data for downstream ML systems (OIP)

## CITL Training Loop

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Python     │────►│   Depyler    │────►│   Rust       │
│   Corpus     │     │  Transpiler  │     │   Code       │
│  (this repo) │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                ▼
                                          ┌──────────────┐
                                          │   rustc      │
                                          │  Compiler    │
                                          └──────────────┘
                                                │
                                                ▼
                                          ┌──────────────┐
                                          │  Diagnostic  │───► Oracle Training
                                          │   Capture    │
                                          └──────────────┘
```

## Quick Start

```bash
# Clone repository
git clone https://github.com/paiml/reprorusted-python-cli.git
cd reprorusted-python-cli

# Install dependencies
make install

# Validate Python examples (6745 tests)
make test

# Run CITL training loop
make citl-improve

# Train oracle model
make citl-train

# Export corpus for OIP
make citl-export
```

## Corpus Statistics

| Metric | Count |
|--------|-------|
| Python Examples | 300+ |
| Python Source Files | 607 |
| Test Files | 296 |
| Passing Tests | 6,745 |
| Example Categories | 15+ |

## Project Structure

```
reprorusted-python-cli/
├── examples/                    # CITL Training Corpus
│   ├── example_simple/          # Basic argparse patterns
│   ├── example_flags/           # Boolean flags
│   ├── example_positional/      # Positional arguments
│   ├── example_subcommands/     # Git-like subcommands
│   ├── example_complex/         # Advanced argparse
│   ├── example_numpy_*/         # NumPy operations (18 examples)
│   ├── example_sklearn_*/       # Scikit-learn patterns (10 examples)
│   ├── example_pytorch_*/       # PyTorch patterns (10 examples)
│   ├── example_async_*/         # Async/await patterns
│   ├── example_datetime_*/      # Date/time handling
│   └── ...                      # 300+ total examples
├── scripts/                     # Automation scripts
├── docs/                        # Documentation
│   └── specifications/          # CITL spec, module mappings
└── Makefile                     # CITL training commands
```

## Example Categories

| Category | Examples | Description |
|----------|----------|-------------|
| **Core CLI** | 20+ | argparse, flags, positional, subcommands |
| **String Ops** | 15+ | split, join, format, replace, strip |
| **Math** | 20+ | abs, pow, round, divmod, minmax |
| **NumPy** | 18 | array ops, linear algebra, statistics |
| **Sklearn** | 10 | regression, clustering, preprocessing |
| **PyTorch** | 10 | tensors, autograd, neural layers |
| **Async** | 5 | async/await, gather, queues |
| **DateTime** | 6 | parsing, formatting, timezones |
| **File I/O** | 10+ | pathlib, shutil, tempfile, csv |
| **Other** | 100+ | regex, json, hashlib, itertools, etc. |

## Usage

### Validate Corpus

```bash
# Run all Python tests (validates training data quality)
make test

# Run with coverage
make coverage

# Check formatting
make format

# Run linter
make lint
```

### CITL Training

```bash
# Run CITL improvement loop on all examples
# (transpiles each .py file with compiler feedback)
make citl-improve

# Train depyler oracle from accumulated diagnostics
make citl-train

# Export training corpus as JSONL for OIP integration
make citl-export
```

### Cleanup

```bash
# Clean Python build artifacts
make clean

# Clean everything including generated Rust
make clean-all
```

## Integration with Depyler

This corpus integrates with depyler's CITL subsystem:

```bash
# Single example transpilation with CITL
depyler compile examples/example_simple/trivial_cli.py --citl-iterations 3

# Batch training from corpus
depyler oracle train --corpus ./examples --min-samples 50

# Export diagnostics for OIP
depyler oracle export-oip --input-dir ./examples --output ./training_corpus/citl.jsonl
```

## Adding New Examples

1. Create example directory:
   ```bash
   mkdir -p examples/example_new
   ```

2. Write test first (TDD):
   ```bash
   # examples/example_new/test_new_tool.py
   ```

3. Implement Python script:
   ```bash
   # examples/example_new/new_tool.py
   ```

4. Validate:
   ```bash
   make test
   ```

## Related Projects

- [depyler](https://github.com/paiml/depyler) - Python-to-Rust transpiler (CITL consumer)
- [aprender](https://github.com/paiml/aprender) - ML library with CITL support
- [alimentar](https://github.com/paiml/alimentar) - Data loading for CITL corpus

## Scientific References

This corpus supports research in Compiler-in-the-Loop learning:

1. Wang et al. (2022). *Compilable Neural Code Generation with Compiler Feedback.* ACL.
2. Yasunaga & Liang (2020). *Graph-based, Self-Supervised Program Repair from Diagnostic Feedback.* ICML.
3. Dou et al. (2024). *StepCoder: Improve Code Generation with Reinforcement Learning from Compiler Feedback.* arXiv.

## License

MIT License - see [LICENSE](LICENSE) for details

## Citation

```bibtex
@software{reprorusted_python_cli,
  title = {CITL Training Corpus for Depyler},
  author = {PAIML},
  year = {2025},
  url = {https://github.com/paiml/reprorusted-python-cli}
}
```
