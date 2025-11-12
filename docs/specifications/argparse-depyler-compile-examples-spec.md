# Argparse-Depyler Compile Examples Specification

**Version:** 1.0.0
**Status:** Draft
**Last Updated:** 2025-11-12

## Executive Summary

This repository provides a comprehensive validation framework for Python-to-Rust transpilation using `depyler`. It focuses on testing "single-shot" compilation of Python argparse-based CLI scripts into standalone Rust binaries, with rigorous input/output validation to ensure semantic equivalence.

## 1. Project Overview

### 1.1 Purpose

Create a systematic, example-by-example validation framework that:
- Validates `depyler`'s ability to transpile Python argparse CLI scripts
- Ensures compiled Rust binaries are functionally equivalent to original Python scripts
- Provides regression testing infrastructure for depyler development
- Demonstrates best practices for Python-to-Rust CLI migration

### 1.2 Core Dependencies

| Dependency | Path | Purpose |
|------------|------|---------|
| **depyler** | `../depyler` | Python-to-Rust transpiler (v3.20.0+) |
| **paiml-mcp-agent-toolkit** (pmat) | `../paiml-mcp-agent-toolkit` | Quality enforcement, roadmap management, TDD workflow |
| **bashrs** | `../bashrs` | Makefile generation, shell script validation |

### 1.3 Success Criteria

- ✅ 100% of examples transpile successfully via `depyler compile`
- ✅ 100% input/output equivalence between Python and Rust binaries
- ✅ 100% test coverage using uv/ruff/pytest
- ✅ All quality gates pass (pmat + custom)
- ✅ Zero manual Makefile maintenance (all programmatically generated)

## 2. Repository Structure

### 2.1 Directory Layout

```
reprorusted-python-cli/
├── Makefile                          # Root Makefile (bashrs-generated)
├── Makefile.rs                       # bashrs source for root Makefile
├── pyproject.toml                    # Python project configuration (uv)
├── README.md                         # Project documentation
├── LICENSE                           # MIT License
├── .gitignore
│
├── docs/
│   ├── specifications/
│   │   ├── argparse-depyler-compile-examples-spec.md  # This document
│   │   ├── makefile-generation-spec.md                # bashrs generation spec
│   │   └── io-testing-strategy.md                     # I/O testing methodology
│   └── examples/
│       └── tutorial.md                                 # Getting started guide
│
├── examples/                         # Example CLI scripts
│   ├── example_simple/
│   │   ├── trivial_cli.py           # Python source (uses argparse)
│   │   ├── trivial_cli.rs           # Transpiled Rust (generated)
│   │   ├── trivial_cli              # Compiled binary (generated)
│   │   ├── test_trivial_cli.py      # pytest test suite (100% coverage)
│   │   ├── Makefile                 # bashrs-generated Makefile
│   │   ├── Makefile.rs              # bashrs source for Makefile
│   │   └── README.md                # Example documentation
│   │
│   ├── example_flags/
│   │   ├── flag_parser.py           # Boolean flags example
│   │   ├── test_flag_parser.py
│   │   ├── Makefile.rs
│   │   └── README.md
│   │
│   ├── example_positional/
│   │   ├── positional_args.py       # Positional arguments
│   │   ├── test_positional_args.py
│   │   ├── Makefile.rs
│   │   └── README.md
│   │
│   ├── example_subcommands/
│   │   ├── git_clone.py             # Subcommand pattern (git-like CLI)
│   │   ├── test_git_clone.py
│   │   ├── Makefile.rs
│   │   └── README.md
│   │
│   ├── example_complex/
│   │   ├── complex_cli.py           # Advanced argparse features
│   │   ├── test_complex_cli.py
│   │   ├── Makefile.rs
│   │   └── README.md
│   │
│   └── example_stdlib/
│       ├── stdlib_integration.py    # Uses multiple stdlib modules
│       ├── test_stdlib_integration.py
│       ├── Makefile.rs
│       └── README.md
│
├── tests/                            # Integration tests
│   ├── test_io_equivalence.rs       # Rust-based I/O validation (assert_cmd)
│   ├── test_transpilation.py        # Python-based transpilation tests
│   └── fixtures/
│       └── test_cases.yaml          # Shared test case definitions
│
├── scripts/                          # Automation scripts
│   ├── generate_makefiles.sh        # Regenerate all Makefiles via bashrs
│   ├── validate_examples.sh         # Run all example validations
│   ├── check_io_equivalence.sh      # Cross-validate Python vs Rust I/O
│   └── setup_dev_env.sh             # Development environment setup
│
├── pmat-quality.toml                 # pmat quality configuration
├── pmat.toml                         # pmat general configuration
├── .pmat-gates.toml                  # pmat quality gates
├── roadmap.yaml                      # pmat roadmap (ticket management)
│
└── .github/
    └── workflows/
        ├── ci.yml                    # CI/CD pipeline
        ├── quality-gates.yml         # Quality enforcement
        └── nightly-validation.yml    # Nightly comprehensive tests
```

### 2.2 Naming Conventions

| Item | Pattern | Example |
|------|---------|---------|
| Example directories | `example_<category>/` | `example_simple/`, `example_flags/` |
| Python scripts | `<name>.py` | `trivial_cli.py`, `flag_parser.py` |
| Test files | `test_<name>.py` | `test_trivial_cli.py` |
| Makefile sources | `Makefile.rs` | All directories with Makefiles |
| Generated Makefiles | `Makefile` | Generated by bashrs from `Makefile.rs` |

## 3. Makefile Infrastructure

### 3.1 Root Makefile (bashrs-generated)

**Source:** `Makefile.rs` (bashrs DSL)
**Generated:** `Makefile` (GNU Make)

#### 3.1.1 Primary Targets

```makefile
# Style similar to ../paiml-mcp-agent-toolkit and ../bashrs

.PHONY: all validate test build clean help
.PHONY: test-fast test-comprehensive test-transpilation test-io-equivalence
.PHONY: quality-gate lint format coverage
.PHONY: generate-makefiles install-deps

# Default target
all: validate build

# Quick validation for development
quick-validate: format-check lint-check test-fast
	@echo "✅ Quick validation passed!"

# Full validation pipeline
validate: quality-gate test-comprehensive coverage
	@echo "✅ All validation passed!"

# Test targets
test: test-transpilation test-io-equivalence test-fast
	@echo "✅ All tests passed!"

test-fast: ## Fast tests with uv/pytest (< 5 min)
	@echo "⚡ Running fast tests..."
	@uv run pytest tests/ examples/ -n auto --maxfail=1

test-comprehensive: ## Comprehensive test suite
	@echo "🧪 Running comprehensive tests..."
	@uv run pytest tests/ examples/ -v --cov --cov-report=html

test-transpilation: ## Test depyler transpilation for all examples
	@echo "🔨 Testing transpilation..."
	@./scripts/validate_examples.sh --mode=transpile

test-io-equivalence: ## Validate Python vs Rust I/O equivalence
	@echo "🔍 Testing I/O equivalence..."
	@cargo test --test test_io_equivalence -- --test-threads=1

# Build targets
build: generate-makefiles ## Build all examples
	@echo "🔨 Building all examples..."
	@for dir in examples/*/; do \
		if [ -f "$$dir/Makefile" ]; then \
			echo "Building $$dir..."; \
			$(MAKE) -C "$$dir" build; \
		fi; \
	done

# Quality gates
quality-gate: ## Run pmat quality checks
	@echo "🔍 Running quality gate checks..."
	@if command -v pmat >/dev/null 2>&1; then \
		pmat analyze complexity --max-cyclomatic 10; \
		pmat tdg . --format table; \
		pmat validate-readme --targets README.md; \
	else \
		echo "⚠️  pmat not installed. Install: cargo install pmat"; \
		exit 1; \
	fi

# Makefile generation
generate-makefiles: ## Regenerate all Makefiles from Makefile.rs sources
	@echo "📝 Regenerating Makefiles via bashrs..."
	@./scripts/generate_makefiles.sh
	@echo "✅ All Makefiles regenerated!"

# Formatting
format: ## Format all code (Python + Rust)
	@echo "🎨 Formatting code..."
	@uv run ruff format .
	@cargo fmt --all
	@echo "✅ Formatting complete!"

lint: ## Lint all code (Python + Rust)
	@echo "🔍 Linting code..."
	@uv run ruff check . --fix
	@cargo clippy --all-targets --all-features -- -D warnings

# Coverage
coverage: ## Generate coverage report
	@echo "📊 Generating coverage report..."
	@uv run pytest --cov --cov-report=html --cov-report=term
	@cargo llvm-cov --html --open

# Development
install-deps: ## Install development dependencies
	@echo "📦 Installing dependencies..."
	@uv sync
	@cargo build
	@./scripts/setup_dev_env.sh

# Help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make <target>\n\n"} \
		/^[a-zA-Z_0-9-]+:.*?##/ { printf "  %-20s %s\n", $$1, $$2 } \
		/^##@/ { printf "\n%s\n", substr($$0, 5) }' $(MAKEFILE_LIST)
```

### 3.2 Example-Level Makefiles (bashrs-generated)

**Source:** `examples/example_<name>/Makefile.rs`
**Generated:** `examples/example_<name>/Makefile`

#### 3.2.1 Standard Targets

Each example directory contains a Makefile with these targets:

```makefile
.PHONY: all clean test build transpile compile run-python run-rust validate

# Variables
PYTHON_SCRIPT := trivial_cli.py
RUST_SOURCE := trivial_cli.rs
RUST_BINARY := trivial_cli
TEST_FILE := test_trivial_cli.py

all: validate

# Single-shot transpilation and compilation
compile: $(RUST_BINARY)

$(RUST_BINARY): $(PYTHON_SCRIPT)
	@echo "🔨 Compiling $(PYTHON_SCRIPT) to Rust binary..."
	depyler compile $(PYTHON_SCRIPT) -o $(RUST_BINARY)
	@echo "✅ Binary compiled: $(RUST_BINARY)"

# Separate transpilation step (for debugging)
transpile: $(RUST_SOURCE)

$(RUST_SOURCE): $(PYTHON_SCRIPT)
	@echo "🔄 Transpiling $(PYTHON_SCRIPT) to Rust..."
	depyler transpile $(PYTHON_SCRIPT) -o $(RUST_SOURCE)

# Build from transpiled source
build: transpile
	@echo "🔨 Building Rust binary from transpiled source..."
	rustc $(RUST_SOURCE) -o $(RUST_BINARY)

# Testing
test: ## Run pytest tests (100% coverage)
	@echo "🧪 Running tests..."
	@uv run pytest $(TEST_FILE) -v --cov --cov-report=term

test-io-equivalence: compile ## Validate Python vs Rust I/O
	@echo "🔍 Testing I/O equivalence..."
	@../../scripts/check_io_equivalence.sh $(PYTHON_SCRIPT) $(RUST_BINARY)

# Execution
run-python: ## Run Python version
	@python3 $(PYTHON_SCRIPT) $(ARGS)

run-rust: compile ## Run Rust version
	@./$(RUST_BINARY) $(ARGS)

# Validation
validate: test test-io-equivalence ## Run all validations
	@echo "✅ All validations passed for $(PYTHON_SCRIPT)!"

# Cleanup
clean:
	@rm -f $(RUST_SOURCE) $(RUST_BINARY)
	@rm -rf __pycache__ .pytest_cache .coverage htmlcov
```

### 3.3 Makefile Generation with bashrs

All Makefiles are **programmatically generated** from `Makefile.rs` sources using `bashrs`.

#### 3.3.1 bashrs Generation Process

```bash
# Regenerate all Makefiles
./scripts/generate_makefiles.sh

# Or individually
bashrs build Makefile.rs -o Makefile
bashrs build examples/example_simple/Makefile.rs -o examples/example_simple/Makefile
```

#### 3.3.2 bashrs DSL Example

**File:** `examples/example_simple/Makefile.rs`

```rust
// bashrs Makefile DSL for example_simple

use bashrs::makefile::*;

fn main() {
    let mut makefile = Makefile::new();

    // Variables
    makefile.var("PYTHON_SCRIPT", "trivial_cli.py");
    makefile.var("RUST_BINARY", "trivial_cli");

    // Targets
    makefile.target("all")
        .phony()
        .depends(&["validate"])
        .recipe("@echo '✅ All tasks complete'");

    makefile.target("compile")
        .phony()
        .depends(&["$(RUST_BINARY)"])
        .recipe("@echo '✅ Compilation complete'");

    makefile.target("$(RUST_BINARY)")
        .depends(&["$(PYTHON_SCRIPT)"])
        .recipe("@echo '🔨 Compiling $(PYTHON_SCRIPT) to Rust binary...'")
        .recipe("depyler compile $(PYTHON_SCRIPT) -o $(RUST_BINARY)");

    // Write to stdout (redirected to Makefile by bashrs)
    println!("{}", makefile.render());
}
```

## 4. Testing Strategy

### 4.1 Multi-Layer Testing Approach

```
┌─────────────────────────────────────────────────────────┐
│              Layer 1: Python Unit Tests                 │
│         (pytest + 100% coverage requirement)            │
│  ✓ Test Python script behavior before transpilation    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│        Layer 2: Transpilation Validation Tests          │
│           (depyler compile success/failure)             │
│  ✓ Verify transpilation completes without errors       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│       Layer 3: I/O Equivalence Validation Tests         │
│    (Python output == Rust output for ALL inputs)        │
│  ✓ Use rexpect or rust assert_cmd for I/O testing      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│          Layer 4: Integration & Regression Tests        │
│        (Cross-example validation, performance)          │
│  ✓ Ensure no regressions across depyler updates        │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Layer 1: Python Unit Tests (pytest)

#### 4.2.1 Requirements

- **Coverage:** 100% line + branch coverage (enforced by pytest-cov)
- **Framework:** pytest + uv for dependency management
- **Location:** `examples/example_<name>/test_<name>.py`

#### 4.2.2 Example Test Suite

**File:** `examples/example_simple/test_trivial_cli.py`

```python
"""
Test suite for trivial_cli.py
Ensures 100% coverage before transpilation
"""

import subprocess
import pytest
from pathlib import Path

SCRIPT = Path(__file__).parent / "trivial_cli.py"

def run_cli(*args):
    """Helper to run CLI and capture output"""
    result = subprocess.run(
        ["python3", str(SCRIPT), *args],
        capture_output=True,
        text=True
    )
    return result

class TestTrivialCLI:
    """Test suite for trivial_cli.py"""

    def test_help_flag(self):
        """Test --help displays usage"""
        result = run_cli("--help")
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()

    def test_version_flag(self):
        """Test --version displays version"""
        result = run_cli("--version")
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_basic_execution(self):
        """Test basic CLI execution"""
        result = run_cli("--name", "Alice")
        assert result.returncode == 0
        assert "Hello, Alice!" in result.stdout

    def test_missing_required_arg(self):
        """Test error handling for missing arguments"""
        result = run_cli()
        assert result.returncode != 0
        assert "required" in result.stderr.lower()

    @pytest.mark.parametrize("name,expected", [
        ("Alice", "Hello, Alice!"),
        ("Bob", "Hello, Bob!"),
        ("Charlie", "Hello, Charlie!"),
    ])
    def test_parametrized_names(self, name, expected):
        """Test various input names"""
        result = run_cli("--name", name)
        assert result.returncode == 0
        assert expected in result.stdout
```

#### 4.2.3 Running Python Tests

```bash
# From example directory
make test

# Or directly via uv
uv run pytest test_trivial_cli.py -v --cov --cov-report=html
```

### 4.3 Layer 2: Transpilation Validation

#### 4.3.1 Validation Script

**File:** `scripts/validate_examples.sh`

```bash
#!/bin/bash
set -e

echo "🔨 Validating transpilation for all examples..."

for example_dir in examples/example_*/; do
    echo ""
    echo "📁 Processing: $example_dir"

    cd "$example_dir"

    # Find Python script
    python_script=$(ls *.py | grep -v test_ | head -1)

    if [ -z "$python_script" ]; then
        echo "⚠️  No Python script found, skipping..."
        cd ../..
        continue
    fi

    echo "  📝 Script: $python_script"

    # Transpile and compile
    echo "  🔄 Running: depyler compile $python_script"
    if depyler compile "$python_script" -o "${python_script%.py}"; then
        echo "  ✅ Transpilation successful!"
    else
        echo "  ❌ Transpilation failed!"
        exit 1
    fi

    cd ../..
done

echo ""
echo "✅ All examples transpiled successfully!"
```

### 4.4 Layer 3: I/O Equivalence Testing

#### 4.4.1 Strategy

For every Python script, we generate a comprehensive set of input test cases and verify that:

```
∀ input ∈ TestCases:
    output_python(input) == output_rust(input)
    exitcode_python(input) == exitcode_rust(input)
```

#### 4.4.2 Rust I/O Validation Tests

**File:** `tests/test_io_equivalence.rs`

```rust
//! I/O Equivalence Testing for Python vs Rust CLIs
//! Uses assert_cmd for robust CLI testing

use assert_cmd::Command;
use predicates::prelude::*;
use std::path::Path;

/// Helper to run Python script
fn run_python(script: &str, args: &[&str]) -> std::process::Output {
    let mut cmd = Command::new("python3");
    cmd.arg(script);
    cmd.args(args);
    cmd.output().expect("Failed to run Python script")
}

/// Helper to run Rust binary
fn run_rust(binary: &str, args: &[&str]) -> std::process::Output {
    let mut cmd = Command::new(binary);
    cmd.args(args);
    cmd.output().expect("Failed to run Rust binary")
}

/// Compare outputs for equivalence
fn assert_io_equivalence(script: &str, binary: &str, args: &[&str]) {
    let python_output = run_python(script, args);
    let rust_output = run_rust(binary, args);

    // Compare exit codes
    assert_eq!(
        python_output.status.code(),
        rust_output.status.code(),
        "Exit codes differ for args: {:?}",
        args
    );

    // Compare stdout
    assert_eq!(
        String::from_utf8_lossy(&python_output.stdout),
        String::from_utf8_lossy(&rust_output.stdout),
        "Stdout differs for args: {:?}",
        args
    );

    // Compare stderr (may differ in stack traces, so check semantically)
    let py_stderr = String::from_utf8_lossy(&python_output.stderr);
    let rust_stderr = String::from_utf8_lossy(&rust_output.stderr);

    if !py_stderr.is_empty() || !rust_stderr.is_empty() {
        // Both should have errors, or neither
        assert_eq!(
            py_stderr.is_empty(),
            rust_stderr.is_empty(),
            "Error presence differs for args: {:?}",
            args
        );
    }
}

#[test]
fn test_trivial_cli_equivalence() {
    let script = "examples/example_simple/trivial_cli.py";
    let binary = "examples/example_simple/trivial_cli";

    // Ensure binary exists
    assert!(Path::new(binary).exists(), "Rust binary not found. Run 'make compile' first.");

    // Test case 1: Help flag
    assert_io_equivalence(script, binary, &["--help"]);

    // Test case 2: Version flag
    assert_io_equivalence(script, binary, &["--version"]);

    // Test case 3: Valid input
    assert_io_equivalence(script, binary, &["--name", "Alice"]);

    // Test case 4: Missing required argument (error case)
    assert_io_equivalence(script, binary, &[]);
}

#[test]
fn test_flag_parser_equivalence() {
    let script = "examples/example_flags/flag_parser.py";
    let binary = "examples/example_flags/flag_parser";

    assert!(Path::new(binary).exists(), "Rust binary not found.");

    // Test various flag combinations
    assert_io_equivalence(script, binary, &["--verbose"]);
    assert_io_equivalence(script, binary, &["--debug"]);
    assert_io_equivalence(script, binary, &["--verbose", "--debug"]);
    assert_io_equivalence(script, binary, &[]);
}

// Add more tests for each example...
```

#### 4.4.3 Alternative: Shell-Based I/O Testing

**File:** `scripts/check_io_equivalence.sh`

```bash
#!/bin/bash
# Cross-validate Python vs Rust I/O for a single example

set -e

PYTHON_SCRIPT="$1"
RUST_BINARY="$2"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

if [ ! -x "$RUST_BINARY" ]; then
    echo "❌ Rust binary not found or not executable: $RUST_BINARY"
    exit 1
fi

echo "🔍 Testing I/O equivalence..."
echo "  Python: $PYTHON_SCRIPT"
echo "  Rust:   $RUST_BINARY"

# Test case function
test_case() {
    local description="$1"
    shift
    local args=("$@")

    echo ""
    echo "  📝 Test: $description"
    echo "     Args: ${args[*]}"

    # Run Python
    python_out=$(python3 "$PYTHON_SCRIPT" "${args[@]}" 2>&1 || true)
    python_exit=$?

    # Run Rust
    rust_out=$("$RUST_BINARY" "${args[@]}" 2>&1 || true)
    rust_exit=$?

    # Compare exit codes
    if [ "$python_exit" -ne "$rust_exit" ]; then
        echo "  ❌ Exit codes differ: Python=$python_exit, Rust=$rust_exit"
        return 1
    fi

    # Compare output
    if [ "$python_out" != "$rust_out" ]; then
        echo "  ❌ Output differs!"
        echo "     Python output: $python_out"
        echo "     Rust output:   $rust_out"
        return 1
    fi

    echo "  ✅ PASS"
    return 0
}

# Define test cases
test_case "Help flag" --help
test_case "Version flag" --version
test_case "Valid input" --name Alice
test_case "Missing argument"

echo ""
echo "✅ All I/O equivalence tests passed!"
```

### 4.5 Layer 4: Integration Tests

**File:** `tests/test_transpilation.py`

```python
"""
Integration tests for depyler transpilation workflow
"""

import subprocess
import pytest
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

def get_all_examples():
    """Find all example directories"""
    return [d for d in EXAMPLES_DIR.glob("example_*") if d.is_dir()]

@pytest.mark.parametrize("example_dir", get_all_examples())
def test_transpile_all_examples(example_dir):
    """Test that all examples transpile successfully"""
    python_script = next((f for f in example_dir.glob("*.py") if not f.name.startswith("test_")), None)

    assert python_script is not None, f"No Python script found in {example_dir}"

    # Run depyler compile
    result = subprocess.run(
        ["depyler", "compile", str(python_script)],
        cwd=example_dir,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Transpilation failed: {result.stderr}"

    # Verify binary was created
    binary = example_dir / python_script.stem
    assert binary.exists(), f"Binary not created: {binary}"
```

## 5. Quality Enforcement

### 5.1 pmat Integration

#### 5.1.1 Configuration Files

**File:** `pmat.toml`

```toml
[project]
name = "reprorusted-python-cli"
version = "1.0.0"
description = "Argparse-to-Rust compilation validation examples"

[quality]
enforce_tdd = true
require_tests_before_code = true
min_coverage = 100

[roadmap]
file = "roadmap.yaml"
enforce_tickets = true
```

**File:** `pmat-quality.toml`

```toml
[thresholds]
complexity = 10
cognitive_complexity = 15
lines_per_function = 50
coverage_minimum = 100

[analysis]
enable_tdg = true
enable_satd = true
enable_complexity = true

[gates]
block_on_tdg_below = "B+"
block_on_coverage_below = 100
block_on_complexity_above = 10
```

**File:** `.pmat-gates.toml`

```toml
[gates.pre-commit]
run = ["format-check", "lint-check", "test-fast"]
block = true

[gates.pre-push]
run = ["validate", "quality-gate"]
block = true

[gates.ci]
run = ["test-comprehensive", "coverage", "quality-gate"]
block = true
```

#### 5.1.2 Quality Gate Workflow

```bash
# Manual quality gate check
pmat analyze complexity --max-cyclomatic 10
pmat tdg . --format table --fail-under B+
pmat validate-readme --targets README.md

# Automated via Makefile
make quality-gate
```

### 5.2 Roadmap-Driven Development

All work is tracked via pmat roadmap in `roadmap.yaml`.

**File:** `roadmap.yaml`

```yaml
version: "1.0"
project: "reprorusted-python-cli"

phases:
  - phase: 1
    name: "Foundation & Infrastructure"
    tickets:
      - id: "RC-001"
        title: "Setup repository structure and tooling"
        status: "todo"
        priority: "critical"
        tasks:
          - "Initialize git repository with .gitignore"
          - "Create directory structure (docs/, examples/, tests/, scripts/)"
          - "Setup pyproject.toml with uv"
          - "Setup Cargo.toml for Rust tests"
          - "Configure pmat with pmat.toml, pmat-quality.toml, .pmat-gates.toml"

      - id: "RC-002"
        title: "Implement Makefile generation with bashrs"
        status: "todo"
        priority: "critical"
        tasks:
          - "Write Makefile.rs for root Makefile"
          - "Write example template Makefile.rs"
          - "Create generate_makefiles.sh script"
          - "Test bashrs generation pipeline"
          - "Document Makefile generation process"

      - id: "RC-003"
        title: "Create example_simple with full TDD cycle"
        status: "todo"
        priority: "high"
        tasks:
          - "Write test_trivial_cli.py with 100% coverage goals"
          - "Implement trivial_cli.py to pass tests"
          - "Run depyler compile to generate binary"
          - "Write Rust I/O equivalence tests"
          - "Validate Python output == Rust output"

  - phase: 2
    name: "Core Examples Implementation"
    tickets:
      - id: "RC-004"
        title: "Implement example_flags with boolean flags"
        status: "todo"
        priority: "high"

      - id: "RC-005"
        title: "Implement example_positional with positional args"
        status: "todo"
        priority: "high"

      - id: "RC-006"
        title: "Implement example_subcommands with git-like CLI"
        status: "todo"
        priority: "medium"

  - phase: 3
    name: "Advanced Examples & Validation"
    tickets:
      - id: "RC-007"
        title: "Implement example_complex with advanced argparse features"
        status: "todo"
        priority: "medium"

      - id: "RC-008"
        title: "Implement example_stdlib with multiple stdlib modules"
        status: "todo"
        priority: "low"

      - id: "RC-009"
        title: "Create comprehensive I/O equivalence test suite in Rust"
        status: "todo"
        priority: "high"

  - phase: 4
    name: "CI/CD & Documentation"
    tickets:
      - id: "RC-010"
        title: "Setup GitHub Actions CI/CD pipeline"
        status: "todo"
        priority: "high"

      - id: "RC-011"
        title: "Write comprehensive README and tutorial"
        status: "todo"
        priority: "medium"

      - id: "RC-012"
        title: "Create video demonstration and blog post"
        status: "todo"
        priority: "low"
```

#### 5.2.1 TDD Workflow

```bash
# 1. Create ticket
pmat roadmap add-ticket --phase 1 --title "Implement feature X"

# 2. Write tests first (RED)
vi examples/example_x/test_feature_x.py

# 3. Run tests (should fail)
make test-fast

# 4. Implement code (GREEN)
vi examples/example_x/feature_x.py

# 5. Run tests (should pass)
make test-fast

# 6. Refactor and validate
make validate

# 7. Mark ticket complete
pmat roadmap complete-ticket RC-003
```

## 6. Example Specifications

### 6.1 Example: Simple CLI (example_simple)

**Complexity:** Trivial
**Argparse Features:** Basic argument parsing, help, version
**Python Script:** `trivial_cli.py`

#### 6.1.1 Python Implementation

```python
#!/usr/bin/env python3
"""
Trivial CLI - Simplest argparse example
"""

import argparse

def main():
    parser = argparse.ArgumentParser(
        description="A trivial CLI example"
    )
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Name to greet"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="1.0.0"
    )

    args = parser.parse_args()
    print(f"Hello, {args.name}!")

if __name__ == "__main__":
    main()
```

#### 6.1.2 Test Cases

```python
def test_help_flag():
    """Test --help displays usage"""

def test_version_flag():
    """Test --version displays version"""

def test_basic_execution():
    """Test --name Alice produces 'Hello, Alice!'"""

def test_missing_required_arg():
    """Test error when --name is missing"""
```

#### 6.1.3 Expected I/O

| Input | Expected Output | Exit Code |
|-------|-----------------|-----------|
| `--help` | Usage message with description and arguments | 0 |
| `--version` | `1.0.0` | 0 |
| `--name Alice` | `Hello, Alice!` | 0 |
| (no args) | Error: required argument missing | 2 |

### 6.2 Example: Flag Parser (example_flags)

**Complexity:** Simple
**Argparse Features:** Boolean flags, flag combinations
**Python Script:** `flag_parser.py`

#### 6.2.1 Features

- `--verbose`: Enable verbose output
- `--debug`: Enable debug mode
- `--quiet`: Suppress output
- Flag combinations should work correctly

### 6.3 Example: Positional Arguments (example_positional)

**Complexity:** Simple
**Argparse Features:** Positional args, nargs, choices
**Python Script:** `positional_args.py`

#### 6.3.1 Features

- Positional argument: `command` (choices: `start`, `stop`, `restart`)
- Optional positional: `target` (default: `all`)
- `nargs='+'` for multiple targets

### 6.4 Example: Subcommands (example_subcommands)

**Complexity:** Medium
**Argparse Features:** Subparsers, nested commands
**Python Script:** `git_clone.py`

#### 6.4.1 Features

- Subcommand: `clone <url>`
- Subcommand: `push <remote>`
- Subcommand: `pull <remote>`
- Global flags: `--verbose`

### 6.5 Example: Complex CLI (example_complex)

**Complexity:** High
**Argparse Features:** All argparse features combined
**Python Script:** `complex_cli.py`

#### 6.5.1 Features

- Mutually exclusive groups
- Argument groups
- Custom types and validation
- File I/O arguments
- Environment variable fallback

### 6.6 Example: Stdlib Integration (example_stdlib)

**Complexity:** High
**Argparse Features:** Integration with depyler-validated stdlib modules
**Python Script:** `stdlib_integration.py`

#### 6.6.1 Features

- Uses `json` module for output formatting
- Uses `pathlib` for file path handling
- Uses `datetime` for timestamps
- Uses `hashlib` for checksums

## 7. Development Workflow

### 7.1 Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/paiml/reprorusted-python-cli.git
cd reprorusted-python-cli

# 2. Install dependencies
make install-deps

# 3. Verify setup
make quick-validate
```

### 7.2 Adding a New Example

```bash
# 1. Create ticket in roadmap.yaml
pmat roadmap add-ticket --title "Implement example_X"

# 2. Create example directory
mkdir -p examples/example_X

# 3. Write Makefile.rs
vi examples/example_X/Makefile.rs

# 4. Generate Makefile
bashrs build examples/example_X/Makefile.rs -o examples/example_X/Makefile

# 5. Write tests first (TDD)
vi examples/example_X/test_X.py

# 6. Implement Python script
vi examples/example_X/X.py

# 7. Run tests
cd examples/example_X
make test

# 8. Transpile and validate
make compile
make test-io-equivalence

# 9. Update root tests
vi tests/test_io_equivalence.rs  # Add new test function

# 10. Validate everything
cd ../..
make validate
```

### 7.3 Regenerating Makefiles

```bash
# Regenerate all Makefiles from Makefile.rs sources
make generate-makefiles

# Or individually
bashrs build Makefile.rs -o Makefile
```

### 7.4 CI/CD Pipeline

**File:** `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Setup Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install depyler
        run: cargo install --path ../depyler

      - name: Install bashrs
        run: cargo install --path ../bashrs

      - name: Install pmat
        run: cargo install pmat

      - name: Install dependencies
        run: make install-deps

      - name: Run quality gates
        run: make quality-gate

      - name: Run comprehensive tests
        run: make test-comprehensive

      - name: Generate coverage
        run: make coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 8. Acceptance Criteria

### 8.1 Per-Example Criteria

For each example to be considered complete:

- [ ] Python script implements specified argparse features
- [ ] pytest test suite achieves 100% coverage
- [ ] All pytest tests pass
- [ ] `depyler compile` succeeds without errors
- [ ] Rust binary executes successfully
- [ ] I/O equivalence tests pass (Python output == Rust output)
- [ ] Makefile is generated from Makefile.rs via bashrs
- [ ] README.md documents the example
- [ ] pmat quality gates pass

### 8.2 Repository-Level Criteria

For the repository to be considered complete:

- [ ] All planned examples (6+) are implemented
- [ ] Root Makefile is generated via bashrs
- [ ] CI/CD pipeline passes all checks
- [ ] pmat TDG grade: B+ or higher
- [ ] pmat complexity: ≤10 cyclomatic complexity per function
- [ ] 100% test coverage across all examples
- [ ] All I/O equivalence tests pass
- [ ] Documentation is comprehensive and validated
- [ ] All tickets in roadmap.yaml are completed
- [ ] Benchmarking infrastructure implemented and validated
- [ ] Performance reports demonstrate Rust advantages

## 9. Scientific Benchmarking Infrastructure

### 9.1 Overview & Purpose

The benchmarking infrastructure provides **scientifically rigorous** performance measurement to demonstrate the power of depyler/Rust compilation. Following methodologies from ruchy-docker and ruchy-lambda, we implement comprehensive performance analysis with academic rigor.

**Goals:**
1. Prove Rust binaries are significantly faster than Python equivalents
2. Measure memory usage, binary size, and startup time advantages
3. Track performance improvements over time
4. Provide transparent, reproducible results
5. Demonstrate real-world CLI performance gains

### 9.2 Metrics Collected

#### 9.2.1 Primary Performance Metrics

| Metric | Description | Measurement Method |
|--------|-------------|-------------------|
| **Execution Time** | Wall-clock time for complete operation | `bashrs bench` (10 iterations, 3 warmup) |
| **Startup Time** | Time from launch to first instruction | Instrumented timing in code |
| **Compute Time** | Pure algorithm execution time | Instrumented timing (startup excluded) |
| **Memory Usage** | Peak RSS memory consumption | `/usr/bin/time -v` or `psutil` |
| **Binary Size** | Size of compiled executable | `stat` or `du -h` |
| **I/O Throughput** | File operations per second | Custom I/O benchmark |

#### 9.2.2 Statistical Metrics

Following academic best practices (DLS 2016, PLDI 2013):

- **Arithmetic Mean**: Total work / CPU time
- **Geometric Mean**: Proper method for ratios (prevents single-benchmark dominance)
- **Harmonic Mean**: Average speedup metric
- **Median (P50)**: 50th percentile (robust to outliers)
- **P99**: 99th percentile (tail latency)
- **Standard Deviation**: Variance analysis
- **MAD**: Median Absolute Deviation (outlier detection)
- **Min/Max**: Performance bounds

#### 9.2.3 Quality Metrics

- **Determinism Score**: Output consistency across runs (0.0-1.0)
- **Success Rate**: Percentage of successful executions
- **Speedup Ratio**: Rust time / Python time (e.g., 50x faster)
- **Memory Efficiency**: Python memory / Rust memory
- **Size Efficiency**: Python interpreter size / Rust binary size

### 9.3 Benchmark Suite Structure

```
benchmarks/
├── framework/
│   ├── benchmark.sh              # bashrs integration (scientific rigor)
│   ├── measure_python.sh         # Python measurement harness
│   ├── measure_rust.sh           # Rust measurement harness
│   └── compare.py                # Statistical comparison & visualization
│
├── micro/                        # Microbenchmarks (isolated features)
│   ├── argparse_overhead/        # Argument parsing performance
│   │   ├── parse_flags.py
│   │   ├── parse_flags          # Rust binary
│   │   ├── benchmark.yaml        # Test cases definition
│   │   └── results.json          # Latest results
│   │
│   ├── startup_time/             # Cold start measurement
│   │   ├── hello_world.py
│   │   ├── hello_world
│   │   └── results.json
│   │
│   ├── string_operations/        # String parsing/manipulation
│   ├── file_io/                  # File read/write performance
│   └── computation/              # CPU-bound tasks (fibonacci, primes)
│
├── macro/                        # Real-world CLI scenarios
│   ├── grep_replacement/         # Search tool benchmark
│   │   ├── grep_tool.py
│   │   ├── grep_tool
│   │   ├── test_data/           # 1MB, 10MB, 100MB files
│   │   └── results.json
│   │
│   ├── json_processor/           # Parse and transform JSON
│   ├── log_analyzer/             # Parse logs, extract stats
│   └── data_pipeline/            # Multi-stage data processing
│
├── reports/                      # Version-controlled results
│   ├── 2025-11-12-v1.0.0.json
│   ├── 2025-11-13-v1.0.1.json
│   └── history.md                # Performance over time
│
├── visualizations/               # Generated charts
│   ├── speedup_comparison.png
│   ├── memory_usage.png
│   ├── binary_size.png
│   └── execution_time_ascii.txt
│
└── README.md                     # Benchmarking documentation
```

### 9.4 Benchmark Implementation

#### 9.4.1 Instrumented Timing (High Precision)

**Python Version** (`benchmarks/micro/computation/fibonacci.py`):

```python
#!/usr/bin/env python3
"""
Fibonacci benchmark with instrumented timing
"""

import argparse
import time

def fibonacci(n: int) -> int:
    """Recursive fibonacci"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=35)
    args = parser.parse_args()

    # Measure startup time
    startup_start = time.perf_counter_ns()
    # Warmup (imports, allocations)
    warmup = sum(range(100000))
    startup_end = time.perf_counter_ns()

    # Measure compute time
    compute_start = time.perf_counter_ns()
    result = fibonacci(args.n)
    compute_end = time.perf_counter_ns()

    startup_us = (startup_end - startup_start) // 1000
    compute_us = (compute_end - compute_start) // 1000

    print(f"STARTUP_TIME_US: {startup_us}")
    print(f"COMPUTE_TIME_US: {compute_us}")
    print(f"RESULT: {result}")

if __name__ == "__main__":
    main()
```

**Rust Version** (Generated by depyler, same instrumentation):

```rust
// Generated by depyler from fibonacci.py
use std::time::Instant;

fn fibonacci(n: i32) -> i64 {
    if n <= 1 {
        return n as i64;
    }
    fibonacci(n - 1) + fibonacci(n - 2)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let n = 35; // Parse from args in real version

    // Measure startup time
    let startup_start = Instant::now();
    let warmup: i64 = (0..100000).sum();
    let startup_us = startup_start.elapsed().as_micros();

    // Measure compute time
    let compute_start = Instant::now();
    let result = fibonacci(n);
    let compute_us = compute_start.elapsed().as_micros();

    println!("STARTUP_TIME_US: {}", startup_us);
    println!("COMPUTE_TIME_US: {}", compute_us);
    println!("RESULT: {}", result);
}
```

#### 9.4.2 bashrs Benchmark Framework

**File:** `benchmarks/framework/benchmark.sh`

```bash
#!/bin/bash
# Scientific benchmarking framework using bashrs v6.32.0
# Follows DLS 2016 / PLDI 2013 methodologies

set -e

BENCHMARK_NAME="$1"
PYTHON_SCRIPT="$2"
RUST_BINARY="$3"
ITERATIONS=${4:-10}
WARMUP=${5:-3}

echo "=========================================="
echo "Scientific Benchmark: $BENCHMARK_NAME"
echo "=========================================="
echo ""

# Ensure binaries exist
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

if [ ! -x "$RUST_BINARY" ]; then
    echo "❌ Rust binary not found or not executable: $RUST_BINARY"
    exit 1
fi

# Create results directory
RESULTS_DIR="$(dirname "$PYTHON_SCRIPT")"
mkdir -p "$RESULTS_DIR"

echo "📊 Benchmarking Python version..."
echo ""

# Benchmark Python with bashrs
bashrs bench run \
    --script "python3 $PYTHON_SCRIPT" \
    --warmup $WARMUP \
    --iterations $ITERATIONS \
    --output "$RESULTS_DIR/python_results.json" \
    --format json \
    --memory

echo ""
echo "📊 Benchmarking Rust version..."
echo ""

# Benchmark Rust with bashrs
bashrs bench run \
    --script "$RUST_BINARY" \
    --warmup $WARMUP \
    --iterations $ITERATIONS \
    --output "$RESULTS_DIR/rust_results.json" \
    --format json \
    --memory

echo ""
echo "📈 Comparing results..."
echo ""

# Statistical comparison
python3 benchmarks/framework/compare.py \
    "$RESULTS_DIR/python_results.json" \
    "$RESULTS_DIR/rust_results.json" \
    --output "$RESULTS_DIR/comparison.json" \
    --visualize

echo ""
echo "✅ Benchmark complete!"
echo "   Results: $RESULTS_DIR/comparison.json"
echo "   Charts: $RESULTS_DIR/comparison_*.png"
```

#### 9.4.3 Statistical Comparison Script

**File:** `benchmarks/framework/compare.py`

```python
#!/usr/bin/env python3
"""
Statistical comparison of Python vs Rust benchmarks
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
import statistics

def geometric_mean(values):
    """Compute geometric mean (proper method for ratios)"""
    product = 1
    for v in values:
        product *= v
    return product ** (1 / len(values))

def compute_speedup(python_ms, rust_ms):
    """Compute speedup ratio"""
    return python_ms / rust_ms

def analyze_results(python_path: Path, rust_path: Path) -> Dict[str, Any]:
    """Perform statistical analysis"""

    with open(python_path) as f:
        python_data = json.load(f)

    with open(rust_path) as f:
        rust_data = json.load(f)

    # Extract timing data
    py_times = python_data['raw_results_ms']
    rust_times = rust_data['raw_results_ms']

    # Compute statistics
    py_mean = statistics.mean(py_times)
    rust_mean = statistics.mean(rust_times)
    py_median = statistics.median(py_times)
    rust_median = statistics.median(rust_times)
    py_stddev = statistics.stdev(py_times)
    rust_stddev = statistics.stdev(rust_times)

    # Compute speedup
    speedup_mean = compute_speedup(py_mean, rust_mean)
    speedup_median = compute_speedup(py_median, rust_median)
    speedup_geo = geometric_mean([compute_speedup(p, r) for p, r in zip(py_times, rust_times)])

    # Memory comparison
    py_memory = python_data.get('memory', {}).get('peak_mb', 0)
    rust_memory = rust_data.get('memory', {}).get('peak_mb', 0)
    memory_reduction = (1 - rust_memory / py_memory) * 100 if py_memory > 0 else 0

    return {
        'benchmark': python_data.get('name', 'Unknown'),
        'python': {
            'mean_ms': py_mean,
            'median_ms': py_median,
            'stddev_ms': py_stddev,
            'min_ms': min(py_times),
            'max_ms': max(py_times),
            'memory_mb': py_memory
        },
        'rust': {
            'mean_ms': rust_mean,
            'median_ms': rust_median,
            'stddev_ms': rust_stddev,
            'min_ms': min(rust_times),
            'max_ms': max(rust_times),
            'memory_mb': rust_memory
        },
        'comparison': {
            'speedup_mean': speedup_mean,
            'speedup_median': speedup_median,
            'speedup_geometric': speedup_geo,
            'memory_reduction_pct': memory_reduction
        },
        'raw_data': {
            'python_times_ms': py_times,
            'rust_times_ms': rust_times
        }
    }

def generate_ascii_chart(comparison: Dict[str, Any]) -> str:
    """Generate ASCII bar chart for visualization"""
    py_time = comparison['python']['mean_ms']
    rust_time = comparison['rust']['mean_ms']
    speedup = comparison['comparison']['speedup_mean']

    # Normalize to 50 characters max
    max_time = max(py_time, rust_time)
    py_bar = '█' * int((py_time / max_time) * 50)
    rust_bar = '█' * int((rust_time / max_time) * 50)

    chart = f"""
Performance Comparison: {comparison['benchmark']}
{'=' * 60}

Python    {py_bar} {py_time:.2f}ms
Rust      {rust_bar} {rust_time:.2f}ms

Speedup: {speedup:.2f}x faster with Rust
Memory Reduction: {comparison['comparison']['memory_reduction_pct']:.1f}%
"""
    return chart

def main():
    if len(sys.argv) < 3:
        print("Usage: compare.py <python_results.json> <rust_results.json>")
        sys.exit(1)

    python_path = Path(sys.argv[1])
    rust_path = Path(sys.argv[2])

    # Analyze results
    comparison = analyze_results(python_path, rust_path)

    # Save comparison
    output_path = python_path.parent / "comparison.json"
    with open(output_path, 'w') as f:
        json.dump(comparison, f, indent=2)

    print(f"✅ Comparison saved to: {output_path}")

    # Generate ASCII chart
    chart = generate_ascii_chart(comparison)
    print(chart)

    # Save chart
    chart_path = python_path.parent / "comparison_chart.txt"
    with open(chart_path, 'w') as f:
        f.write(chart)

if __name__ == '__main__':
    main()
```

### 9.5 Makefile Integration

Add these targets to the root Makefile:

```makefile
##@ Benchmarking

bench: ## Run all benchmarks (Python vs Rust)
	@echo "🔥 Running comprehensive benchmark suite..."
	@./scripts/run_all_benchmarks.sh

bench-micro: ## Run microbenchmarks only
	@echo "⚡ Running microbenchmarks..."
	@for dir in benchmarks/micro/*/; do \
		$(MAKE) -C "$$dir" benchmark; \
	done

bench-macro: ## Run macro (real-world) benchmarks
	@echo "🌍 Running macro benchmarks..."
	@for dir in benchmarks/macro/*/; do \
		$(MAKE) -C "$$dir" benchmark; \
	done

bench-report: ## Generate comprehensive performance report
	@echo "📊 Generating benchmark report..."
	@python3 benchmarks/framework/generate_report.py \
		--output benchmarks/reports/performance-report-$(shell date +%Y-%m-%d).md

bench-history: ## Show performance trends over time
	@echo "📈 Performance history..."
	@python3 benchmarks/framework/history_analysis.py

bench-regression: ## Check for performance regressions
	@echo "🔍 Checking for performance regressions..."
	@python3 benchmarks/framework/regression_check.py \
		--threshold 5.0 \
		--fail-on-regression

bench-clean: ## Clean benchmark artifacts
	@rm -rf benchmarks/*/results.json
	@rm -rf benchmarks/visualizations/*
	@echo "✅ Benchmark artifacts cleaned"
```

### 9.6 Visualization & Reporting

#### 9.6.1 ASCII Charts (Terminal-Friendly)

**Example Output:**

```
Performance Comparison: Fibonacci(35) Benchmark
============================================================

Python    ████████████████████████████████████████████████ 687.23ms
Rust      █ 13.45ms

Speedup: 51.1x faster with Rust
Memory Reduction: 94.3% (Python: 45MB → Rust: 2.5MB)

Statistical Summary:
  Geometric Mean Speedup: 49.8x
  P50 Speedup: 50.9x
  P99 Speedup: 52.3x
  Determinism Score: 1.0 (perfectly consistent)
```

#### 9.6.2 JSON Reports

**File:** `benchmarks/reports/2025-11-12-v1.0.0.json`

```json
{
  "report_version": "1.0.0",
  "date": "2025-11-12T17:00:00Z",
  "repository": "reprorusted-python-cli",
  "depyler_version": "3.20.0",
  "environment": {
    "cpu": "Intel Core i7-9750H @ 2.60GHz",
    "ram_gb": 16,
    "os": "Linux 6.8.0-87-generic",
    "python_version": "3.11.6",
    "rustc_version": "1.83.0"
  },
  "benchmarks": [
    {
      "name": "fibonacci_35",
      "category": "micro/computation",
      "python": {
        "mean_ms": 687.23,
        "median_ms": 686.50,
        "stddev_ms": 12.45,
        "memory_mb": 45.2
      },
      "rust": {
        "mean_ms": 13.45,
        "median_ms": 13.42,
        "stddev_ms": 0.23,
        "memory_mb": 2.5
      },
      "speedup": {
        "mean": 51.1,
        "geometric": 49.8,
        "median": 50.9
      },
      "memory_reduction_pct": 94.3
    }
  ],
  "summary": {
    "total_benchmarks": 12,
    "geometric_mean_speedup": 47.3,
    "average_memory_reduction_pct": 91.2,
    "binary_size_comparison": {
      "python_interpreter_mb": 4.8,
      "average_rust_binary_kb": 352
    }
  }
}
```

#### 9.6.3 Markdown Performance Report

**File:** `benchmarks/reports/PERFORMANCE_REPORT.md`

Auto-generated report with:

1. **Executive Summary**: Key findings, speedup highlights
2. **Methodology**: Statistical approach, warmup, iterations
3. **Results Table**: All benchmarks with speedup ratios
4. **Visualizations**: Embedded ASCII charts
5. **Historical Comparison**: Performance trends
6. **Reproducibility**: Environment details, exact commands
7. **Academic Citations**: References to methodology papers

### 9.7 Performance Regression Detection

**File:** `benchmarks/framework/regression_check.py`

```python
#!/usr/bin/env python3
"""
Performance regression detection
Fails CI if performance degrades >5% from baseline
"""

import json
import sys
from pathlib import Path

def check_regression(current_path: Path, baseline_path: Path, threshold_pct: float = 5.0):
    """
    Compare current results to baseline
    Fail if performance degraded more than threshold
    """
    with open(current_path) as f:
        current = json.load(f)

    with open(baseline_path) as f:
        baseline = json.load(f)

    regressions = []

    for curr_bench in current['benchmarks']:
        name = curr_bench['name']

        # Find matching baseline
        baseline_bench = next((b for b in baseline['benchmarks'] if b['name'] == name), None)
        if not baseline_bench:
            continue

        # Compare Rust performance
        curr_time = curr_bench['rust']['mean_ms']
        base_time = baseline_bench['rust']['mean_ms']

        regression_pct = ((curr_time - base_time) / base_time) * 100

        if regression_pct > threshold_pct:
            regressions.append({
                'benchmark': name,
                'baseline_ms': base_time,
                'current_ms': curr_time,
                'regression_pct': regression_pct
            })

    if regressions:
        print("❌ Performance Regressions Detected!")
        print(f"   Threshold: {threshold_pct}%")
        print("")
        for reg in regressions:
            print(f"  {reg['benchmark']}:")
            print(f"    Baseline: {reg['baseline_ms']:.2f}ms")
            print(f"    Current:  {reg['current_ms']:.2f}ms")
            print(f"    Regression: +{reg['regression_pct']:.1f}%")
        sys.exit(1)
    else:
        print("✅ No performance regressions detected")
        sys.exit(0)

if __name__ == '__main__':
    current = Path('benchmarks/reports/current.json')
    baseline = Path('benchmarks/reports/baseline.json')
    check_regression(current, baseline)
```

### 9.8 CI/CD Integration

**File:** `.github/workflows/benchmarks.yml`

```yaml
name: Performance Benchmarks

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Setup Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable

      - name: Install dependencies
        run: |
          pip install -r requirements-bench.txt
          cargo install --path ../depyler
          cargo install --path ../bashrs

      - name: Build all examples
        run: make build

      - name: Run benchmarks
        run: make bench

      - name: Check for regressions
        run: make bench-regression

      - name: Generate report
        run: make bench-report

      - name: Upload benchmark results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: benchmarks/reports/

      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('benchmarks/reports/performance-report-latest.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

### 9.9 Academic Rigor & Methodology

Following peer-reviewed research:

#### 9.9.1 Citations

1. **DLS 2016** (Marr et al.): "Are We Fast Yet?" - Cross-language benchmarking methodology
2. **USENIX ATC 2015** (Felter et al.): Container performance analysis
3. **OOPSLA 2007** (Blackburn et al.): Benchmark evaluation methodology
4. **PLDI 2013** (Kalibera & Jones): Rigorous benchmarking best practices
5. **IEEE Computer 2018** (Eyerman & Eeckhout): Geometric mean in performance analysis

#### 9.9.2 Statistical Practices

- **Warmup Iterations**: 3 runs to eliminate cold-start effects
- **Measurement Iterations**: 10 runs for statistical significance
- **Outlier Detection**: MAD-based (Median Absolute Deviation)
- **Aggregation**: Report arithmetic, geometric, and harmonic means
- **Transparency**: All raw data included, not just summary statistics

#### 9.9.3 Reproducibility Checklist

- [ ] Exact tool versions documented (Python, Rust, depyler)
- [ ] Hardware specifications recorded (CPU, RAM, OS)
- [ ] Compilation flags documented (optimization levels)
- [ ] Environment variables captured
- [ ] Raw measurement data saved
- [ ] Statistical methodology documented
- [ ] Benchmark source code available
- [ ] Random seed fixed (for non-deterministic workloads)
- [ ] Multiple machines tested (validate consistency)
- [ ] Timestamps recorded for all measurements

### 9.10 Example Benchmark Results

#### 9.10.1 Expected Performance Gains

Based on depyler v3.20.0 and ruchy-docker findings:

| Benchmark | Python (ms) | Rust (ms) | Speedup | Memory Reduction |
|-----------|-------------|-----------|---------|------------------|
| Fibonacci(35) | 687.23 | 13.45 | **51.1x** | 94.3% |
| Prime Sieve (10K) | 234.56 | 8.92 | **26.3x** | 89.7% |
| Argparse Overhead | 12.34 | 0.23 | **53.7x** | 98.2% |
| File I/O (100MB) | 456.78 | 89.12 | **5.1x** | 67.4% |
| JSON Processing | 123.45 | 34.56 | **3.6x** | 71.2% |
| String Operations | 345.67 | 12.34 | **28.0x** | 92.5% |
| **Geometric Mean** | - | - | **25.8x** | **85.5%** |

#### 9.10.2 Binary Size Comparison

| Language | Binary Size | Deployment Size | Notes |
|----------|-------------|-----------------|-------|
| Python | N/A (interpreter) | ~5MB (interpreter + script) | Requires Python runtime |
| Rust (debug) | 2.3MB | 2.3MB | Unoptimized |
| Rust (release) | 352KB | 352KB | opt-level=3 |
| Rust (min-size) | 287KB | 287KB | opt-level='z' + strip |

### 9.11 Roadmap Tickets for Benchmarking

Add to `roadmap.yaml`:

```yaml
  - phase: 5
    name: "Scientific Benchmarking Infrastructure"
    tickets:
      - id: "RC-013"
        title: "Setup benchmarking framework with bashrs integration"
        status: "todo"
        priority: "high"
        tasks:
          - "Create benchmarks/ directory structure"
          - "Implement benchmark.sh with bashrs"
          - "Implement compare.py statistical analysis"
          - "Add Makefile targets for benchmarking"
          - "Document benchmarking methodology"

      - id: "RC-014"
        title: "Implement microbenchmarks (6 categories)"
        status: "todo"
        priority: "high"
        tasks:
          - "Argparse overhead benchmark"
          - "Startup time benchmark"
          - "String operations benchmark"
          - "File I/O benchmark"
          - "Computation benchmark (fibonacci, primes)"
          - "Memory usage benchmark"

      - id: "RC-015"
        title: "Implement macro benchmarks (real-world scenarios)"
        status: "todo"
        priority: "medium"
        tasks:
          - "grep replacement tool benchmark"
          - "JSON processor benchmark"
          - "Log analyzer benchmark"
          - "Data pipeline benchmark"

      - id: "RC-016"
        title: "Create visualization and reporting infrastructure"
        status: "todo"
        priority: "medium"
        tasks:
          - "Generate ASCII charts"
          - "Generate PNG charts (matplotlib)"
          - "Create markdown report generator"
          - "Version-control historical results"

      - id: "RC-017"
        title: "Implement performance regression detection"
        status: "todo"
        priority: "high"
        tasks:
          - "Write regression_check.py"
          - "Integrate with CI/CD"
          - "Setup baseline results"
          - "Document regression thresholds"

      - id: "RC-018"
        title: "Write academic-quality benchmarking documentation"
        status: "todo"
        priority: "medium"
        tasks:
          - "Document methodology with citations"
          - "Create reproducibility checklist"
          - "Write BENCHMARKS.md report"
          - "Publish results to repository"
```

### 9.12 Quality Gates for Benchmarking

Add to `.pmat-gates.toml`:

```toml
[gates.benchmarking]
run = [
    "bench-micro",
    "bench-macro",
    "bench-regression"
]
block = true

[thresholds.performance]
minimum_speedup = 10.0              # Rust must be ≥10x faster than Python
memory_reduction_minimum_pct = 75.0 # Rust must use ≤25% of Python memory
binary_size_maximum_kb = 500        # Rust binary must be ≤500KB
regression_threshold_pct = 5.0      # No >5% performance regressions
```

## 10. Appendices

### 10.1 Tool Versions

| Tool | Version | Installation |
|------|---------|--------------|
| depyler | ≥3.20.0 | `cargo install --path ../depyler` |
| bashrs | ≥1.0.0 | `cargo install --path ../bashrs` |
| pmat | ≥1.0.0 | `cargo install pmat` |
| uv | ≥0.1.0 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| pytest | ≥7.0 | `uv add pytest pytest-cov` |
| assert_cmd | ≥2.0 | Add to `Cargo.toml` |
| bashrs | ≥6.32.0 | Scientific benchmarking support |
| hyperfine | latest | Alternative benchmarking tool |

### 10.2 References

- **depyler documentation:** `../depyler/README.md`
- **bashrs documentation:** `../bashrs/README.md`
- **pmat documentation:** `../paiml-mcp-agent-toolkit/README.md`
- **Python argparse:** https://docs.python.org/3/library/argparse.html
- **pytest documentation:** https://docs.pytest.org/
- **assert_cmd crate:** https://docs.rs/assert_cmd/
- **ruchy-docker benchmarks:** `../ruchy-docker/benchmarks/`
- **ruchy-lambda benchmarks:** `../ruchy-lambda/benchmarks/`
- **DLS 2016 paper:** "Are We Fast Yet?" (Marr et al.)
- **PLDI 2013 paper:** "Rigorous Benchmarking in Reasonable Time" (Kalibera & Jones)

### 10.3 Glossary

- **Single-shot compilation:** Using `depyler compile` to transpile and compile in one command
- **I/O equivalence:** Guarantee that Python and Rust versions produce identical output for identical input
- **Quality gate:** Automated check that blocks merging if quality standards are not met
- **TDD:** Test-Driven Development - write tests before implementation
- **pmat:** PAIML MCP Agent Toolkit - quality enforcement and roadmap management tool
- **bashrs:** Rust-based shell transpiler and Makefile generator
- **Geometric mean:** Proper statistical method for comparing performance ratios
- **Speedup:** Performance improvement ratio (e.g., 50x = Rust is 50 times faster)
- **MAD:** Median Absolute Deviation - robust outlier detection method
- **Instrumented timing:** Embedded measurement code for high-precision performance data

---

**Status:** Ready for implementation
**Next Steps:** Begin Phase 1, Ticket RC-001 - Setup repository structure

**Questions or Feedback:** Create an issue in the repository or contact the team.
