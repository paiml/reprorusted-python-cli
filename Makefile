.PHONY: help install test coverage lint format clean quality citl-train citl-improve citl-export extract-cpython-doctests

help:
	@echo "reprorusted-python-cli - CITL Training Corpus for Depyler"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install dependencies with uv"
	@echo ""
	@echo "Corpus Pipeline (GH-7 through GH-22):"
	@echo "  make corpus-pipeline  - Run full pipeline (label → augment → report)"
	@echo "  make corpus-label     - Apply weak supervision labels"
	@echo "  make corpus-augment   - Generate augmented corpus"
	@echo "  make corpus-report    - Generate quality report"
	@echo "  make corpus-analyze   - Analyze zero-success categories"
	@echo "  make corpus-baseline  - Save current report as baseline"
	@echo "  make corpus-diff      - Compare current vs baseline"
	@echo "  make corpus-retranspile - Run depyler on all examples"
	@echo "  make corpus-refresh   - Full refresh: baseline → retranspile → pipeline → diff"
	@echo "  make corpus-category-diff - Show which categories changed status"
	@echo "  make corpus-verify-rust - Verify transpiled Rust compiles"
	@echo "  make corpus-compile-report - Generate Rust compilation JSON report"
	@echo "  make corpus-error-analysis - Categorize compilation errors"
	@echo "  make corpus-record-progress - Record current success rate"
	@echo "  make corpus-progress-history - Show progress over time"
	@echo "  make corpus-recommendations - Generate fix recommendations"
	@echo "  make corpus-dashboard - Show unified status dashboard"
	@echo "  make corpus-ci - Run CI validation (fails on regression)"
	@echo "  make corpus-ci-baseline - Save current as CI baseline"
	@echo "  make corpus-e2e-rate - Measure single-shot compile rate"
	@echo ""
	@echo "CITL Training:"
	@echo "  make citl-train       - Train depyler oracle from corpus"
	@echo "  make citl-improve     - Run CITL improvement loop on all examples"
	@echo "  make citl-export      - Export training corpus for OIP"
	@echo ""
	@echo "Quality Gates:"
	@echo "  make quality          - Run all quality gates (format → lint → test)"
	@echo "  make format           - Check Python code formatting"
	@echo "  make lint             - Lint Python code"
	@echo "  make test             - Run all Python tests"
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
			bashrs lint --ignore SEC010,DET002,DET003,SC2031,SC2035,SC2046,SC2062,SC2064,SC2086,SC2091,SC2092,SC2117,SC2125,SC2128,SC2140,SC2145,SC2154,SC2161,SC2164,SC2183,SC2201,SC2204,SC2231,SC2266,SC2281,SC2317 "$$script"; \
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

# ============================================================================
# Corpus Pipeline (GH-13) - Tarantula/Weak Supervision/Augmentation
# ============================================================================
.PHONY: corpus-label corpus-augment corpus-report corpus-analyze corpus-pipeline

CORPUS_INPUT ?= data/depyler_citl_corpus_v2.parquet
LABELED_CORPUS = data/labeled_corpus.parquet
AUGMENTED_CORPUS = data/augmented_corpus.parquet

corpus-label: $(CORPUS_INPUT)
	@echo "Applying weak supervision labels..."
	@uv run python scripts/label_corpus.py $(CORPUS_INPUT) -o $(LABELED_CORPUS)
	@echo "✅ Labels applied → $(LABELED_CORPUS)"

corpus-augment: $(LABELED_CORPUS)
	@echo "Generating augmented corpus..."
	@uv run python scripts/augment_corpus.py $(LABELED_CORPUS) -o $(AUGMENTED_CORPUS) -m 2
	@echo "✅ Augmented → $(AUGMENTED_CORPUS)"

corpus-report: $(LABELED_CORPUS)
	@echo "Generating quality report..."
	@mkdir -p reports
	@uv run python scripts/corpus_quality_report.py $(LABELED_CORPUS) -o reports/quality_report.json
	@echo "✅ Report → reports/quality_report.json"

corpus-analyze: $(LABELED_CORPUS)
	@echo "Analyzing zero-success categories..."
	@mkdir -p reports
	@uv run python scripts/zero_success_analyzer.py $(LABELED_CORPUS) -o reports/zero_success_analysis.json
	@echo "✅ Analysis → reports/zero_success_analysis.json"

corpus-pipeline: corpus-label corpus-augment corpus-report corpus-analyze
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "✅ Corpus Pipeline Complete!"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "Outputs:"
	@echo "  - $(LABELED_CORPUS)"
	@echo "  - $(AUGMENTED_CORPUS)"
	@echo "  - reports/quality_report.json"
	@echo "  - reports/zero_success_analysis.json"
	@echo ""
	@uv run python scripts/corpus_quality_report.py $(LABELED_CORPUS) --markdown | head -20

# Corpus Diff (GH-14) - Track progress after depyler fixes
.PHONY: corpus-baseline corpus-diff

corpus-baseline: reports/quality_report.json
	@echo "Saving baseline report..."
	@cp reports/quality_report.json reports/baseline.json
	@echo "✅ Baseline saved → reports/baseline.json"

corpus-diff: reports/baseline.json reports/quality_report.json
	@./scripts/corpus_diff.sh reports/baseline.json reports/quality_report.json

# Category Diff (GH-16) - Show which categories changed
.PHONY: corpus-category-diff

corpus-category-diff: data/baseline_corpus.parquet $(LABELED_CORPUS)
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "CATEGORY CHANGES"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@uv run python scripts/category_diff.py data/baseline_corpus.parquet $(LABELED_CORPUS) | \
		while IFS=: read -r key val; do \
			case "$$key" in \
				NOW_PASSING) \
					if [ -n "$$val" ]; then \
						printf "\033[0;32m✅ NOW PASSING:\033[0m\n"; \
						echo "$$val" | tr ',' '\n' | sed 's/^/   - /'; \
					else \
						printf "\033[0;32m✅ NOW PASSING: (none)\033[0m\n"; \
					fi ;; \
				REGRESSED) \
					if [ -n "$$val" ]; then \
						printf "\033[0;31m❌ REGRESSED:\033[0m\n"; \
						echo "$$val" | tr ',' '\n' | sed 's/^/   - /'; \
					else \
						printf "\033[0;32m❌ REGRESSED: (none)\033[0m\n"; \
					fi ;; \
				NET_CHANGE) \
					echo ""; \
					echo "Net: $$val categories" ;; \
			esac; \
		done
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

data/baseline_corpus.parquet: $(LABELED_CORPUS)
	@echo "Saving baseline corpus..."
	@cp $(LABELED_CORPUS) data/baseline_corpus.parquet
	@echo "✅ Baseline corpus saved → data/baseline_corpus.parquet"

# Retranspile & Refresh (GH-15) - Run latest depyler on corpus
.PHONY: corpus-retranspile corpus-refresh

corpus-retranspile:
	@echo "Retranspiling corpus with depyler $(shell depyler --version 2>/dev/null | head -1)..."
	@uv run python scripts/retranspile_corpus.py
	@echo "✅ Retranspile complete"

corpus-refresh: corpus-baseline corpus-retranspile corpus-pipeline corpus-diff
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "✅ Corpus Refresh Complete!"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "Depyler: $(shell depyler --version 2>/dev/null | head -1)"
	@echo "See diff above for improvement metrics."

# ============================================================================
# Rust Verification (GH-17) - Verify transpiled Rust compiles
# ============================================================================
.PHONY: corpus-verify-rust corpus-compile-report

corpus-verify-rust:
	@echo "Verifying transpiled Rust compiles..."
	@./scripts/verify_rust_compilation.sh --verbose

corpus-compile-report:
	@echo "Generating Rust compilation report..."
	@mkdir -p reports
	@./scripts/verify_rust_compilation.sh --json > reports/rust_compile_report.json
	@echo "✅ Report → reports/rust_compile_report.json"

# ============================================================================
# Error Analysis (GH-18) - Categorize compilation errors
# ============================================================================
.PHONY: corpus-error-analysis

corpus-error-analysis:
	@echo "Analyzing Rust compilation errors..."
	@./scripts/analyze_rust_errors.sh --summary

# ============================================================================
# Progress Tracking (GH-19) - Track success rate over time
# ============================================================================
.PHONY: corpus-record-progress corpus-progress-history

corpus-record-progress:
	@./scripts/progress_tracker.sh --record

corpus-progress-history:
	@./scripts/progress_tracker.sh --history

# ============================================================================
# Recommendations (GH-20) - Generate fix recommendations for depyler
# ============================================================================
.PHONY: corpus-recommendations

corpus-recommendations:
	@./scripts/generate_recommendations.sh

# ============================================================================
# Dashboard (GH-21) - Unified corpus status view
# ============================================================================
.PHONY: corpus-dashboard

corpus-dashboard:
	@./scripts/corpus_dashboard.sh

# ============================================================================
# CI Integration (GH-22) - Automated corpus validation
# ============================================================================
.PHONY: corpus-ci corpus-ci-baseline

corpus-ci:
	@./scripts/ci_runner.sh

corpus-ci-baseline:
	@echo "Saving CI baseline..."
	@./scripts/ci_runner.sh --no-fail > /dev/null
	@uv run python3 -c "import json, pyarrow.parquet as pq; df=pq.read_table('data/labeled_corpus.parquet').to_pandas(); print(json.dumps({'total':len(df),'success':int(df['has_rust'].sum()),'failing':len(df)-int(df['has_rust'].sum()),'rate':round(df['has_rust'].sum()*100/len(df),1)}))" > data/ci_baseline.json
	@echo "✅ Baseline saved → data/ci_baseline.json"

# Single-shot compile rate (Refs depyler#193)
# Measures both [[bin]] and [lib] crates that compile with cargo check
corpus-e2e-rate:
	@uv run python scripts/measure_compile_rate.py

corpus-e2e-rate-json:
	@uv run python scripts/measure_compile_rate.py --json

corpus-e2e-rate-verbose:
	@uv run python scripts/measure_compile_rate.py --verbose
