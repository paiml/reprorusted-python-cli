<p align="center">
  <img src="docs/llm-bootstrap-oracle.svg" alt="LLM Bootstrap to ML Oracle" width="800">
</p>

<h1 align="center">reprorusted-python-cli</h1>

<p align="center">
  <strong>Compiler-in-the-Loop Training Corpus for Python→Rust Transpilation</strong>
</p>

<p align="center">
  <a href="https://github.com/paiml/reprorusted-python-cli/actions"><img src="https://github.com/paiml/reprorusted-python-cli/workflows/CI/badge.svg" alt="CI"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://github.com/paiml/reprorusted-python-cli/actions"><img src="https://img.shields.io/badge/tests-6745%20passing-brightgreen" alt="Tests"></a>
  <a href="https://github.com/paiml/reprorusted-python-cli/tree/main/examples"><img src="https://img.shields.io/badge/examples-298-blue" alt="Examples"></a>
  <a href="https://huggingface.co/datasets/paiml/depyler-citl"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-depyler--citl-yellow" alt="HuggingFace Dataset"></a>
</p>

---

## The Core Idea

**Use LLMs to bootstrap traditional ML, not as a runtime dependency.**

This corpus captures decision traces from autonomous LLM sessions, persists them to `.apr` format, and trains a local ML oracle. After N sessions, the oracle handles common cases without API calls.

| Phase | Model | Cost |
|-------|-------|------|
| Bootstrap | LLM (Claude/GPT) | $$/hour |
| Capture | Decision traces → `.apr` | One-time |
| Steady-state | HNSW + Tarantula | ~$0 |

## What This Repository Contains

298 Python CLI examples with 6,745 tests, designed for [depyler](https://github.com/paiml/depyler) transpiler training:

| Metric | Value |
|--------|-------|
| Python Examples | 298 |
| Test Coverage | 6,745 passing |
| Transpilation Rate | 65% |
| Compilation Rate | 0% (4,583 rustc errors) |

The compilation failures are the training signal—each error becomes an (error, fix) pattern for the oracle.

## Quick Start

```bash
git clone https://github.com/paiml/reprorusted-python-cli.git
cd reprorusted-python-cli

make install    # Install dependencies
make test       # Validate corpus (6745 tests)
make citl-train # Train oracle from diagnostics
```

## Corpus Extraction

Extract additional training data from CPython stdlib doctests:

```bash
make extract-cpython-doctests  # Requires alimentar
```

This extracts ~1,700 doctests to `data/corpora/cpython-doctests.parquet`. See [docs/corpus-extraction.md](docs/corpus-extraction.md) for full reproducibility details.

## CITL Training Loop

```
Python Corpus → Depyler → Rust Code → rustc → Diagnostics → Oracle
     ↑                                              │
     └──────────── patterns.apr ◄──────────────────┘
```

Each transpilation attempt generates compiler diagnostics. These accumulate in `.apr` format, training the oracle to suggest fixes for future errors.

## Example Categories

| Category | Count | Description |
|----------|-------|-------------|
| Core CLI | 20+ | argparse, flags, subcommands |
| String Ops | 15+ | split, join, format, strip |
| Math | 20+ | arithmetic, statistics |
| NumPy | 18 | array ops, linear algebra |
| Sklearn | 10 | regression, clustering |
| PyTorch | 10 | tensors, autograd |
| Async | 5 | async/await patterns |
| File I/O | 10+ | pathlib, csv, json |

## Autonomous Session Results

We ran Claude Code unattended for 13 hours:

| Metric | Target | Actual |
|--------|--------|--------|
| Commits | 5 | **12** (240%) |
| Duration | 6 hrs | **13 hrs** |
| Tickets | - | DEPYLER-0616→0627 |

The LLM fixed bugs, wrote tests, passed clippy, and committed—no human intervention.

## Error Distribution

Top rustc errors from transpilation attempts:

| Code | Count | Issue |
|------|-------|-------|
| E0308 | 1,050 | Type mismatch |
| E0433 | 706 | Failed to resolve |
| E0599 | 543 | Method not found |
| E0425 | 392 | Cannot find value |
| E0277 | 380 | Trait bound not satisfied |

Each error type becomes training data for the oracle.

## Project Structure

```
reprorusted-python-cli/
├── examples/           # 298 Python CLI examples
│   ├── example_*/      # Individual examples with tests
├── docs/               # Specifications and diagrams
├── scripts/            # Automation
└── Makefile            # CITL commands
```

## Integration

```bash
# Transpile single example
depyler transpile examples/example_simple/trivial_cli.py

# Train oracle from corpus
depyler oracle train --corpus ./examples

# Export for downstream ML
depyler oracle export-oip --output ./citl.jsonl
```

## Related Projects

| Project | Role |
|---------|------|
| [depyler](https://github.com/paiml/depyler) | Python→Rust transpiler |
| [aprender](https://github.com/paiml/aprender) | ML library, `.apr` format |
| [entrenar](https://github.com/paiml/entrenar) | CITL pattern storage |
| [alimentar](https://github.com/paiml/alimentar) | Dataset loading & publishing |
| [renacer](https://github.com/paiml/renacer) | Decision trace ingestion |

## HuggingFace Dataset

This corpus is available on HuggingFace for ML training:

```python
from datasets import load_dataset

ds = load_dataset("paiml/depyler-citl")

# 606 Python→Rust pairs, 436 with successful transpilation
for row in ds["train"]:
    print(f"{row['python_file']}: {row['python_lines']} → {row['rust_lines']} lines")
```

📦 **Dataset:** [huggingface.co/datasets/paiml/depyler-citl](https://huggingface.co/datasets/paiml/depyler-citl)

## References

1. Wang et al. (2022). *Compilable Neural Code Generation with Compiler Feedback.* ACL.
2. Yasunaga & Liang (2020). *Graph-based, Self-Supervised Program Repair from Diagnostic Feedback.* ICML.
3. Dou et al. (2024). *StepCoder: Improve Code Generation with Reinforcement Learning from Compiler Feedback.* arXiv.

## License

MIT License - see [LICENSE](LICENSE)

```bibtex
@software{reprorusted_python_cli,
  title = {CITL Training Corpus for Depyler},
  author = {PAIML},
  year = {2025},
  url = {https://github.com/paiml/reprorusted-python-cli}
}
```
