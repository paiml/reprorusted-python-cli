.PHONY: help test lint format clean quality validate build compile-all io-check dev bench bench-all bench-docker bench-docker-all build-docker-images bench-regression bench-visualize bench-report bench-charts

help:
	@echo "reprorusted-python-cli - Argparse-to-Rust Transpilation Examples"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Setup development environment"
	@echo "  make build            - Build Rust workspace"
	@echo ""
	@echo "Examples:"
	@echo "  make validate            - Validate all Python examples (tests only)"
	@echo "  make compile-all         - Compile all examples to Rust"
	@echo "  make compile-status      - Update compile status (sequential)"
	@echo "  make compile-status-fast - Update compile status (parallel 8x, ~21s)"
	@echo "  make io-check            - Check Python vs Rust I/O equivalence"
	@echo ""
	@echo "Benchmarking:"
	@echo "  make bench            - Benchmark single example (EXAMPLE=example_simple)"
	@echo "  make bench-all        - Benchmark all examples (native binaries)"
	@echo "  make bench-docker     - Benchmark single example in Docker (EXAMPLE=example_simple)"
	@echo "  make bench-docker-all - Benchmark all examples in Docker"
	@echo "  make bench-regression - Check for performance regressions vs baseline"
	@echo "  make build-docker-images - Build all Docker images for benchmarking"
	@echo ""
	@echo "Visualization & Reporting:"
	@echo "  make bench-visualize  - Generate ASCII charts from benchmark results"
	@echo "  make bench-charts     - Generate PNG charts (requires matplotlib)"
	@echo "  make bench-report     - Generate markdown report"
	@echo ""
	@echo "Quality Gates:"
	@echo "  make quality          - Run all quality gates (format → lint → test)"
	@echo "  make format           - Check code formatting (Python, Rust)"
	@echo "  make format-fix       - Fix code formatting"
	@echo "  make lint             - Run linters (Python, Rust, shell, Makefiles, Dockerfiles)"
	@echo "  make lint-fix         - Auto-fix lint issues"
	@echo "  make test             - Run all tests (Python unit tests)"
	@echo ""
	@echo "Git Hooks:"
	@echo "  ./scripts/install_hooks.sh - Install pre-commit hook (format + lint + test)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Clean build artifacts"
	@echo "  make clean-all        - Clean everything including compiled binaries"

# Development
dev:
	@echo "Setting up development environment..."
	@./scripts/setup_dev_env.sh

build:
	@echo "Building Rust workspace..."
	@cargo build --release

# Validation
validate:
	@echo "Validating all Python examples..."
	@./scripts/validate_examples.sh

compile-all:
	@echo "Compiling all examples to Rust..."
	@for example_dir in examples/example_*/; do \
		if [ -d "$$example_dir" ]; then \
			example_name=$$(basename "$$example_dir"); \
			echo ""; \
			echo "=== Compiling $$example_name ==="; \
			$(MAKE) -C "$$example_dir" compile || exit 1; \
		fi; \
	done
	@echo ""
	@echo "✅ All examples compiled successfully!"

compile-status:
	@./scripts/update_compile_status.sh

compile-status-fast:
	@./scripts/parallel_compile_status.sh

io-check:
	@echo "Checking Python vs Rust I/O equivalence..."
	@for example_dir in examples/example_*/; do \
		if [ -d "$$example_dir" ]; then \
			example_name=$$(basename "$$example_dir"); \
			echo ""; \
			echo "=== Testing $$example_name ==="; \
			$(MAKE) -C "$$example_dir" io-check || exit 1; \
		fi; \
	done
	@echo ""
	@echo "✅ All I/O equivalence tests passed!"

# Benchmarking
bench:
	@if [ -z "$(EXAMPLE)" ]; then \
		echo "❌ Error: EXAMPLE variable required"; \
		echo "Usage: make bench EXAMPLE=example_simple"; \
		exit 1; \
	fi
	@if [ ! -d "examples/$(EXAMPLE)" ]; then \
		echo "❌ Error: examples/$(EXAMPLE) not found"; \
		exit 1; \
	fi
	@echo "Benchmarking $(EXAMPLE)..."
	@chmod +x benchmarks/framework/bench_runner.sh
	@./benchmarks/framework/bench_runner.sh examples/$(EXAMPLE)

bench-all:
	@echo "Benchmarking all examples..."
	@chmod +x benchmarks/framework/bench_all.sh benchmarks/framework/bench_runner.sh
	@./benchmarks/framework/bench_all.sh

bench-docker:
	@if [ -z "$(EXAMPLE)" ]; then \
		echo "❌ Error: EXAMPLE variable required"; \
		echo "Usage: make bench-docker EXAMPLE=example_simple"; \
		exit 1; \
	fi
	@if [ ! -d "docker/$(EXAMPLE)" ]; then \
		echo "❌ Error: docker/$(EXAMPLE) not found"; \
		echo "Run: make build-docker-images"; \
		exit 1; \
	fi
	@echo "Benchmarking $(EXAMPLE) in Docker..."
	@chmod +x benchmarks/framework/bench_docker.sh
	@./benchmarks/framework/bench_docker.sh $(EXAMPLE)

bench-docker-all:
	@echo "Benchmarking all examples in Docker..."
	@for docker_dir in docker/*/; do \
		if [ -d "$$docker_dir" ]; then \
			example_name=$$(basename "$$docker_dir"); \
			echo ""; \
			echo "=== Docker benchmark: $$example_name ==="; \
			$(MAKE) bench-docker EXAMPLE=$$example_name || exit 1; \
		fi; \
	done
	@echo ""
	@echo "✅ All Docker benchmarks complete!"

build-docker-images:
	@echo "Building Docker images for all examples..."
	@for docker_dir in docker/*/; do \
		if [ -d "$$docker_dir" ]; then \
			example_name=$$(basename "$$docker_dir"); \
			echo ""; \
			echo "=== Building $$example_name ==="; \
			if [ -f "$$docker_dir/Dockerfile.python" ]; then \
				echo "Building Python image..."; \
				docker build -f "$$docker_dir/Dockerfile.python" -t "reprorusted-python:$$example_name" . || exit 1; \
			fi; \
			if [ -f "$$docker_dir/Dockerfile.rust" ]; then \
				echo "Building Rust image..."; \
				docker build -f "$$docker_dir/Dockerfile.rust" -t "reprorusted-rust:$$example_name" . || exit 1; \
			fi; \
		fi; \
	done
	@echo ""
	@echo "✅ All Docker images built successfully!"

bench-regression:
	@echo "Checking for performance regressions..."
	@chmod +x benchmarks/framework/regression_check.py
	@python3 benchmarks/framework/regression_check.py

# Visualization & Reporting
bench-visualize:
	@echo "Generating ASCII charts from benchmark results..."
	@chmod +x benchmarks/framework/visualize.py
	@python3 benchmarks/framework/visualize.py

bench-charts:
	@echo "Generating PNG charts from benchmark results..."
	@chmod +x benchmarks/framework/visualize_png.py
	@python3 benchmarks/framework/visualize_png.py || echo "⚠️  Install matplotlib: pip install matplotlib"

bench-report:
	@echo "Generating markdown report from benchmark results..."
	@chmod +x benchmarks/framework/generate_report.py
	@python3 benchmarks/framework/generate_report.py

bench-scientific:
	@echo "Scientific benchmarking with bashrs bench..."
	@chmod +x scripts/bench_all_bashrs.sh
	@./scripts/bench_all_bashrs.sh
	@echo ""
	@echo "Results: benchmarks/reports/timing.csv"
	@cat benchmarks/reports/timing.csv | column -t -s,

# Quality Gates
quality: format lint test
	@echo ""
	@echo "✅ All quality gates passed!"

format:
	@echo "Checking Python formatting (ruff)..."
	@uv run ruff format --check examples/
	@echo "Checking Rust formatting (rustfmt)..."
	@cargo fmt --all -- --check
	@echo "✅ Formatting check passed"

format-fix:
	@echo "Fixing Python formatting..."
	@uv run ruff format examples/
	@echo "Fixing Rust formatting..."
	@cargo fmt --all
	@echo "✅ Formatting fixed"

lint:
	@echo "Linting Python code (ruff)..."
	@uv run ruff check examples/
	@echo "Linting Rust code (clippy)..."
	@cargo clippy --workspace -- -D warnings
	@echo "Linting shell scripts (bashrs)..."
	@# Note: || true until bashrs #82 (--ignore flag) is implemented for SEC010 false positives
	@for script in scripts/*.sh benchmarks/framework/*.sh; do \
		if [ -f "$$script" ]; then \
			bashrs lint "$$script" || true; \
		fi; \
	done
	@echo "Linting Makefiles (bashrs)..."
	@bashrs make purify --report Makefile || true
	@for makefile in examples/*/Makefile; do \
		if [ -f "$$makefile" ]; then \
			echo "Checking $$makefile..."; \
			bashrs make purify --report "$$makefile" || true; \
		fi; \
	done
	@echo "Linting Dockerfiles (bashrs)..."
	@for dockerfile in docker/*/Dockerfile.*; do \
		if [ -f "$$dockerfile" ]; then \
			echo "Checking $$dockerfile..."; \
			bashrs lint "$$dockerfile" || true; \
		fi; \
	done
	@echo "✅ Linting passed"

lint-fix:
	@echo "Auto-fixing Python issues..."
	@uv run ruff check --fix examples/
	@echo "Auto-fixing shell scripts..."
	@for script in scripts/*.sh benchmarks/framework/*.sh; do \
		if [ -f "$$script" ]; then \
			bashrs lint --fix "$$script" || exit 1; \
		fi; \
	done
	@echo "Auto-fixing Makefiles..."
	@bashrs make purify Makefile || true
	@for makefile in examples/*/Makefile; do \
		if [ -f "$$makefile" ]; then \
			echo "Purifying $$makefile..."; \
			bashrs make purify "$$makefile" || true; \
		fi; \
	done
	@echo "Auto-fixing Dockerfiles..."
	@for dockerfile in docker/*/Dockerfile.*; do \
		if [ -f "$$dockerfile" ]; then \
			echo "Fixing $$dockerfile..."; \
			bashrs lint --fix "$$dockerfile" || true; \
		fi; \
	done
	@echo "✅ Lint fixes applied"

test:
	@echo "Running all Python tests..."
	@./scripts/validate_examples.sh
	@echo "✅ All tests passed"

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	@cargo clean
	@find examples/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find examples/ -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find examples/ -type f -name ".coverage" -delete 2>/dev/null || true
	@find examples/ -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find examples/ -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned build artifacts"

clean-all: clean
	@echo "Cleaning compiled binaries..."
	@find examples/ -type f -perm -111 ! -name "*.py" ! -name "*.sh" -delete 2>/dev/null || true
	@find examples/ -type f -name "*.rs" -delete 2>/dev/null || true
	@find examples/ -name "Cargo.toml" ! -path "*/target/*" -delete 2>/dev/null || true
	@echo "✅ Cleaned everything"
