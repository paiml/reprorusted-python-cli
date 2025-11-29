# reprorusted-python-cli

**CITL Training Corpus for Depyler**

[![CI](https://github.com/paiml/reprorusted-python-cli/workflows/CI/badge.svg)](https://github.com/paiml/reprorusted-python-cli/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-6745%20passing-brightgreen)](https://github.com/paiml/reprorusted-python-cli/actions)
[![Examples](https://img.shields.io/badge/examples-298-blue)](https://github.com/paiml/reprorusted-python-cli/tree/main/examples)

## Overview

This repository provides a **Compiler-in-the-Loop (CITL) training corpus** for the [depyler](https://github.com/paiml/depyler) Python-to-Rust transpiler. It contains 298 Python CLI examples with comprehensive test coverage, designed to train depyler's oracle model through iterative compiler feedback.

**Purpose:**
- Train depyler's CITL oracle model
- Provide diverse Python patterns for transpilation learning
- Generate compiler diagnostics for error→fix prediction
- Export training data for downstream ML systems (OIP)

## Transpilation Status Matrix

> **Last Updated:** 2025-11-29 (depyler commit ba5becce)

### Summary

| Metric | Count | Rate |
|--------|-------|------|
| Total Examples | 298 | - |
| Transpilation Pass | 194 | **65%** |
| Transpilation Fail | 104 | 35% |
| Compilation Pass | 0 | **0%** |
| Compilation Fail | 194 | 100% |
| Total rustc Errors | 4,583 | ~24 errors/example |

### Error Distribution (Top 10)

| Error Code | Count | Description | Root Cause |
|------------|-------|-------------|------------|
| E0308 | 1,050 | Type mismatch | Type inference gaps |
| E0433 | 706 | Failed to resolve | Missing module mappings |
| E0599 | 543 | Method not found | Incomplete stdlib mapping |
| E0425 | 392 | Cannot find value | Missing variable declarations |
| E0277 | 380 | Trait bound not satisfied | Type coercion issues |
| E0432 | 365 | Unresolved import | Missing crate dependencies |
| E0282 | 289 | Type annotations needed | Generic type inference |
| E0061 | 188 | Wrong number of args | Function signature mismatch |
| E0609 | 146 | No field found | Struct field mapping |
| E0412 | 124 | Cannot find type | Missing type definitions |

### Categories Failing Transpilation (104 examples)

| Category | Examples | Blocker |
|----------|----------|---------|
| Async Patterns | `async_context`, `async_gather`, `async_iterator`, `async_queue` | `async`/`await` not implemented |
| Decorators | `decorator_pattern`, `retry_decorator` | Decorator transformation |
| Dataclasses | `dataclass`, `dataclass_*` | `@dataclass` not supported |
| Comprehensions | `dict_comprehension`, `nested_comprehension` | Complex comprehension forms |
| Context Managers | `contextlib`, `context_error` | `with` statement transforms |
| Event Patterns | `event_emitter`, `event_observable`, `event_saga` | Complex callback patterns |
| Advanced Closures | `func_curry`, `func_either` | Higher-order function handling |
| Calendar/Time | `calendar`, `datetime_basic` | Complex datetime patterns |

### Blocking Issues (GitHub Tickets)

| Issue | Description | Impact |
|-------|-------------|--------|
| [#168](https://github.com/paiml/depyler/issues/168) | pytest module mapping | Test file transpilation |
| [#169](https://github.com/paiml/depyler/issues/169) | os module expansion | File/path operations |
| [#170](https://github.com/paiml/depyler/issues/170) | Type inference improvement | 1,050+ E0308 errors |
| [#171](https://github.com/paiml/depyler/issues/171) | subprocess module mapping | Process management |

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
| Python Examples | 298 |
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
│   └── ...                      # 298 total examples
├── scripts/                     # Automation scripts
├── docs/                        # Documentation
│   └── specifications/          # CITL spec, module mappings
└── Makefile                     # CITL training commands
```

## Example Categories

| Category | Examples | Transpiles | Compiles | Description |
|----------|----------|------------|----------|-------------|
| **Core CLI** | 20+ | 18 | 0 | argparse, flags, positional, subcommands |
| **String Ops** | 15+ | 15 | 0 | split, join, format, replace, strip |
| **Math** | 20+ | 20 | 0 | abs, pow, round, divmod, minmax |
| **NumPy** | 18 | 18 | 0 | array ops, linear algebra, statistics |
| **Sklearn** | 10 | 10 | 0 | regression, clustering, preprocessing |
| **PyTorch** | 10 | 10 | 0 | tensors, autograd, neural layers |
| **Async** | 5 | 1 | 0 | async/await, gather, queues |
| **DateTime** | 6 | 3 | 0 | parsing, formatting, timezones |
| **File I/O** | 10+ | 8 | 0 | pathlib, shutil, tempfile, csv |
| **Other** | 100+ | 90+ | 0 | regex, json, hashlib, itertools, etc. |

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

### Transpilation Testing

```bash
# Test single example
depyler transpile examples/example_simple/trivial_cli.py --verify

# Batch transpile all examples
for d in examples/example_*/; do
  py_file=$(find "$d" -maxdepth 1 -name "*.py" ! -name "test_*" | head -1)
  [ -n "$py_file" ] && depyler transpile "$py_file" -o /tmp/out.rs
done

# Count compilation errors
rustc --crate-type lib --deny warnings /tmp/out.rs 2>&1 | grep -c "^error\[E"
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

## Roadmap to 100% Compilation

### Phase 1: Critical Infrastructure (Target: 50% compilation)
1. Fix type inference for collections (E0308)
2. Complete os module mapping (E0433, E0432)
3. Implement subprocess module (E0433)
4. Add missing pytest patterns

### Phase 2: Extended Coverage (Target: 80% compilation)
1. Implement async/await transformation
2. Add decorator support
3. Complete datetime module mapping
4. Handle dataclasses

### Phase 3: Full Coverage (Target: 100% compilation)
1. Advanced comprehension forms
2. Context manager transforms
3. Complex closure patterns
4. Event-driven patterns

## Related Projects

- [depyler](https://github.com/paiml/depyler) - Python-to-Rust transpiler (CITL consumer)
- [aprender](https://github.com/paiml/aprender) - ML library with CITL support
- [alimentar](https://github.com/paiml/alimentar) - Data loading for CITL corpus

## LLM-Native Development: A New Paradigm

> *"The model is the prompt. The training is session history. The deployment is copy-paste."*

This project demonstrates a paradigm shift from traditional MLOps to **LLM-native development**:

### Traditional MLOps vs LLM Autonomous Sessions

| Aspect | Traditional MLOps | LLM Overnight Sessions |
|--------|------------------|------------------------|
| **Training loop** | Epochs over static dataset | Continuous fix→compile→commit |
| **Feedback signal** | Loss function | Compiler error codes (rustc) |
| **Data collection** | Batch ETL pipelines | Real-time decision traces |
| **Model update** | Retrain + deploy (hours) | Prompt refinement (seconds) |
| **Human-in-loop** | Label data | Review commits in morning |
| **Cold start** | GPU training (hours) | Paste prompt (seconds) |

### Results: Overnight Autonomous Session (2025-11-29)

We ran Claude Code unattended for 13 hours with a carefully crafted prompt:

| Metric | Target | Actual |
|--------|--------|--------|
| Commits | 5 | **12** (240%) |
| Duration | 6 hrs | **13 hrs** |
| Commit rate | - | ~1/hour |
| Tickets closed | - | DEPYLER-0616→0627 |

**Key insight:** The LLM didn't just find bugs—it fixed them, wrote tests, passed clippy, and committed. No human intervention for 13 hours.

### The CITL Hybrid: Self-Improving LLM Sessions

```
┌─────────────────────────────────────────────────────────────────┐
│                    CITL + LLM Feedback Loop                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   LLM generates fix ──► rustc validates ──► trace stored        │
│         ▲                                        │              │
│         │                                        ▼              │
│         └────────── retrieval augments ◄── pattern indexed      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

The decision traces we capture during transpilation become training signal for future sessions. Each overnight run makes the next one smarter—without retraining any model.

### LLM Bootstrap → Traditional ML Oracle

The end goal isn't LLM dependency—it's **LLM obsolescence**:

![LLM Bootstrap to ML Oracle](docs/llm-bootstrap-oracle.svg)

| Phase | Model | Cost | Duration |
|-------|-------|------|----------|
| **Bootstrap** | LLM (Claude/GPT) | $$/hour | N sessions |
| **Capture** | Decision traces → `.apr` | One-time | Automatic |
| **Steady-state** | HNSW + Tarantula | ~$0 | Forever |

After enough overnight sessions, the `.apr` file contains sufficient (error, fix) patterns that the local ML oracle handles common cases without calling external LLMs.

```
LLM session → patterns.apr → local inference (no API calls)
```

**The LLM teaches itself out of a job.**

### Implications for MLOps

1. **Prompt engineering is the new hyperparameter tuning**
2. **Session logs are the new training data**
3. **Compiler output is the new loss function**
4. **Git commits are the new model checkpoints**
5. **LLM is bootstrap, not runtime dependency**

This isn't replacing traditional ML—it's using LLMs to *bootstrap* traditional ML. The expensive LLM handles the long tail during development; the cheap local oracle handles production.

### Try It Yourself

```bash
# The overnight prompt that achieved 240% of target:
cat ../depyler/docs/processes/overnight-autonomous.md

# Run your own autonomous session:
claude --prompt "$(cat overnight_prompt.txt)"

# Check results in the morning:
git log --oneline --since="yesterday"
```

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
