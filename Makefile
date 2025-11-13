.PHONY: help test lint format clean quality validate build compile-all io-check dev bench bench-all bench-docker bench-docker-all build-docker-images bench-regression

help:
	@echo "reprorusted-python-cli - Argparse-to-Rust Transpilation Examples"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Setup development environment"
	@echo "  make build            - Build Rust workspace"
	@echo ""
	@echo "Examples:"
	@echo "  make validate         - Validate all Python examples (tests only)"
	@echo "  make compile-all      - Compile all examples to Rust"
	@echo "  make io-check         - Check Python vs Rust I/O equivalence"
	@echo ""
	@echo "Benchmarking:"
	@echo "  make bench            - Benchmark single example (EXAMPLE=example_simple)"
	@echo "  make bench-all        - Benchmark all examples (native binaries)"
	@echo "  make bench-docker     - Benchmark single example in Docker (EXAMPLE=example_simple)"
	@echo "  make bench-docker-all - Benchmark all examples in Docker"
	@echo "  make bench-regression - Check for performance regressions vs baseline"
	@echo "  make build-docker-images - Build all Docker images for benchmarking"
	@echo ""
	@echo "Quality Gates:"
	@echo "  make quality          - Run all quality gates (format → lint → test)"
	@echo "  make format           - Check code formatting (Python, Rust)"
	@echo "  make format-fix       - Fix code formatting"
	@echo "  make lint             - Run linters (ruff, clippy, bashrs)"
	@echo "  make lint-fix         - Auto-fix lint issues"
	@echo "  make test             - Run all tests (Python unit tests)"
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
	@bashrs lint scripts/*.sh
	@echo "Linting Makefile (bashrs)..."
	@bashrs make purify --report Makefile
	@echo "✅ Linting passed"

lint-fix:
	@echo "Auto-fixing Python issues..."
	@uv run ruff check --fix examples/
	@echo "Auto-fixing shell scripts..."
	@bashrs lint --fix scripts/*.sh
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
