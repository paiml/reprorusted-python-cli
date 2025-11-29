.PHONY: help install test coverage lint format clean quality citl-train citl-improve citl-export extract-cpython-doctests

help:
	@echo "reprorusted-python-cli - CITL Training Corpus for Depyler"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install dependencies with uv"
	@echo ""
	@echo "Corpus Extraction:"
	@echo "  make extract-cpython-doctests - Extract doctests from CPython stdlib"
	@echo ""
	@echo "CITL Training:"
	@echo "  make citl-train       - Train depyler oracle from corpus"
	@echo "  make citl-improve     - Run CITL improvement loop on all examples"
	@echo "  make citl-export      - Export training corpus for OIP"
	@echo ""
	@echo "Quality Gates:"
	@echo "  make quality          - Run all quality gates (format → lint → test)"
	@echo "  make format           - Check Python code formatting"
	@echo "  make format-fix       - Fix Python code formatting"
	@echo "  make lint             - Lint Python code"
	@echo "  make test             - Run all Python tests"
	@echo "  make coverage         - Run tests with coverage report"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Clean Python build artifacts"
	@echo "  make clean-all        - Clean everything including generated Rust"

# Setup
install:
	@echo "Installing dependencies with uv..."
	@uv sync
	@echo "✅ Dependencies installed"

# CITL Training (depyler integration)
citl-train:
	@echo "Training depyler oracle from corpus..."
	@depyler oracle train --min-samples 50
	@echo "✅ Oracle training complete"

citl-improve:
	@echo "Running CITL improvement loop..."
	@for example_dir in examples/example_*/; do \
		if [ -d "$$example_dir" ]; then \
			for py_file in "$$example_dir"/*.py; do \
				if [ -f "$$py_file" ] && ! echo "$$py_file" | grep -q "test_"; then \
					echo "Processing $$py_file..."; \
					depyler compile "$$py_file" --citl-iterations 3 2>/dev/null || true; \
				fi; \
			done; \
		fi; \
	done
	@echo "✅ CITL improvement complete"

citl-export:
	@echo "Exporting training corpus for OIP..."
	@mkdir -p training_corpus
	@depyler oracle export-oip \
		--input-dir ./examples \
		--output ./training_corpus/citl_corpus.jsonl \
		--min-confidence 0.80 \
		--include-clippy
	@echo "✅ Corpus exported to training_corpus/citl_corpus.jsonl"

# Corpus Extraction - Reproducible doctest extraction from CPython stdlib
# Prerequisites: alimentar (https://github.com/paiml/alimentar)
# Output: data/corpora/cpython-doctests.parquet
CPYTHON_TMP := /tmp/cpython
CPYTHON_LIB_CLEAN := /tmp/cpython-lib-clean

extract-cpython-doctests:
	@echo "Extracting CPython stdlib doctests (reproducible)..."
	@echo "Prerequisites: alimentar must be installed and in PATH"
	@echo ""
	@# Clone CPython if not present
	@if [ ! -d "$(CPYTHON_TMP)" ]; then \
		echo "Cloning CPython stdlib..."; \
		git clone --depth 1 https://github.com/python/cpython $(CPYTHON_TMP); \
	else \
		echo "Using cached CPython at $(CPYTHON_TMP)"; \
		cd $(CPYTHON_TMP) && git pull --ff-only 2>/dev/null || true; \
	fi
	@# Filter out test directories with non-UTF-8 files
	@echo "Filtering stdlib (excluding test/idlelib/turtledemo)..."
	@rm -rf $(CPYTHON_LIB_CLEAN)
	@rsync -a --exclude='test' --exclude='idlelib' --exclude='turtledemo' \
		$(CPYTHON_TMP)/Lib/ $(CPYTHON_LIB_CLEAN)/
	@# Extract doctests using alimentar
	@mkdir -p data/corpora
	@CPYTHON_SHA=$$(cd $(CPYTHON_TMP) && git rev-parse --short HEAD); \
	echo "CPython commit: $$CPYTHON_SHA"; \
	alimentar doctest extract $(CPYTHON_LIB_CLEAN) \
		-o data/corpora/cpython-doctests.parquet \
		--source cpython \
		--version "$$CPYTHON_SHA"
	@echo ""
	@echo "✅ Extracted to data/corpora/cpython-doctests.parquet"
	@echo "   (This file is gitignored - not committed to repository)"
	@ls -lh data/corpora/cpython-doctests.parquet

# Quality Gates
quality: format lint test
	@echo ""
	@echo "✅ All quality gates passed!"

format:
	@echo "Checking Python formatting (ruff)..."
	@uv run ruff format --check examples/
	@echo "✅ Formatting check passed"

format-fix:
	@echo "Fixing Python formatting..."
	@uv run ruff format examples/
	@echo "✅ Formatting fixed"

lint:
	@echo "Linting Python code (ruff)..."
	@uv run ruff check examples/
	@echo "Linting shell scripts (bashrs)..."
	@for script in scripts/*.sh; do \
		if [ -f "$$script" ]; then \
			bashrs lint --ignore SEC010,DET002,DET003,SC2031,SC2035,SC2046,SC2062,SC2064,SC2086,SC2092,SC2117,SC2128,SC2140,SC2145,SC2154,SC2161,SC2164,SC2183,SC2201,SC2204,SC2231,SC2266,SC2281,SC2317 "$$script"; \
		fi; \
	done
	@echo "✅ Linting passed"

lint-fix:
	@echo "Auto-fixing Python issues..."
	@uv run ruff check --fix examples/
	@echo "✅ Lint fixes applied"

test:
	@echo "Running all Python tests..."
	@uv run pytest examples/ --tb=short --no-cov -n 4 --maxfail=10 --timeout=30 -q
	@echo "✅ All tests passed"

coverage:
	@echo "Running tests with coverage..."
	@uv run pytest examples/ --tb=short --cov=examples --cov-report=term-missing -n 4 --maxfail=10 --timeout=30 -q
	@echo "✅ Coverage report generated"

# Cleanup
clean:
	@echo "Cleaning Python build artifacts..."
	@find examples/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find examples/ -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find examples/ -type f -name ".coverage" -delete 2>/dev/null || true
	@find examples/ -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find examples/ -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned Python artifacts"

clean-all: clean
	@echo "Cleaning generated Rust artifacts..."
	@find examples/ -type f -name "*.rs" -delete 2>/dev/null || true
	@find examples/ -name "Cargo.toml" -delete 2>/dev/null || true
	@find examples/ -name "Cargo.lock" -delete 2>/dev/null || true
	@find examples/ -type d -name "target" -exec rm -rf {} + 2>/dev/null || true
	@find examples/ -type d -name "src" -exec rm -rf {} + 2>/dev/null || true
	@find examples/ -type f -executable ! -name "*.py" ! -name "*.sh" -delete 2>/dev/null || true
	@rm -rf training_corpus/
	@echo "✅ Cleaned everything"
