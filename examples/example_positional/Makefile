.PHONY: help test compile io-check clean validate

PYTHON_SCRIPT := positional_args.py
RUST_BINARY := positional_args
TEST_SCRIPT := test_positional_args.py

help:
	@echo "example_positional - Positional Arguments Example"
	@echo ""
	@echo "Commands:"
	@echo "  make test       - Run Python unit tests"
	@echo "  make compile    - Compile to Rust binary"
	@echo "  make io-check   - Verify Python/Rust I/O equivalence"
	@echo "  make validate   - Run all validation (test + compile + io-check)"
	@echo "  make clean      - Clean build artifacts"

test:
	@echo "Running Python unit tests..."
	@uv run pytest $(TEST_SCRIPT) -v --cov=$(PYTHON_SCRIPT) --cov-report=term-missing
	@echo "✅ Tests passed"

compile: $(RUST_BINARY)

$(RUST_BINARY): $(PYTHON_SCRIPT)
	@echo "Compiling $(PYTHON_SCRIPT) to Rust binary..."
	@depyler compile $(PYTHON_SCRIPT) -o $(RUST_BINARY)
	@chmod +x $(RUST_BINARY)
	@echo "✅ Compilation complete: $(RUST_BINARY)"

io-check: $(RUST_BINARY)
	@echo "Checking Python vs Rust I/O equivalence..."
	@../../scripts/check_io_equivalence.sh $(PYTHON_SCRIPT) $(RUST_BINARY)
	@echo "✅ I/O equivalence verified"

validate: test compile io-check
	@echo "✅ All validation passed for example_positional"

clean:
	@rm -f $(RUST_BINARY) $(RUST_BINARY).rs
	@rm -f Cargo.toml
	@rm -rf __pycache__ .pytest_cache .coverage htmlcov .ruff_cache
	@echo "✅ Cleaned example_positional"
