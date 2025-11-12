# Makefile Generation and Management

## Overview

This project uses **manually written Makefiles** that are validated for determinism using `bashrs make purify`.

## Architecture

Unlike a code-generation approach, we maintain Makefiles as source files and use bashrs for:
1. **Validation**: Ensure Makefiles follow best practices
2. **Purification**: Detect and fix non-deterministic patterns (e.g., unsorted wildcards)
3. **Linting**: Check for common Makefile anti-patterns

## Makefile Structure

### Root Makefile

**Location:** `/Makefile`

**Purpose:** Orchestrate all examples and provide top-level commands

**Key Targets:**
- `make help` - Show all available commands
- `make test` - Run all Python tests
- `make compile-all` - Compile all examples to Rust
- `make io-check` - Verify Python/Rust I/O equivalence
- `make quality` - Run all quality gates
- `make clean` - Clean build artifacts

### Example Makefiles

**Location:** `examples/example_*/Makefile`

**Purpose:** Build, test, and validate individual examples

**Template Structure:**
```makefile
.PHONY: help test compile io-check clean validate

PYTHON_SCRIPT := <script>.py
RUST_BINARY := <script>
TEST_SCRIPT := test_<script>.py

help:
	@echo "example_<name> - <Description>"
	...

test:
	@uv run pytest $(TEST_SCRIPT) -v --cov=$(PYTHON_SCRIPT)

compile: $(RUST_BINARY)

$(RUST_BINARY): $(PYTHON_SCRIPT)
	@depyler compile $(PYTHON_SCRIPT) -o $(RUST_BINARY)

io-check: $(RUST_BINARY)
	@../../scripts/check_io_equivalence.sh $(PYTHON_SCRIPT) $(RUST_BINARY)

validate: test compile io-check
	@echo "✅ All validation passed"

clean:
	@rm -f $(RUST_BINARY) $(RUST_BINARY).rs Cargo.toml
	@rm -rf __pycache__ .pytest_cache .coverage htmlcov
```

## Validation with bashrs

### Manual Validation

Check a single Makefile:
```bash
bashrs make purify --report Makefile
```

Check all Makefiles:
```bash
./scripts/generate_makefiles.sh
```

### What bashrs Checks

1. **Non-deterministic wildcards**: Ensures `$(wildcard ...)` is wrapped with `$(sort ...)`
2. **PHONY declarations**: Validates targets are properly marked
3. **Pattern consistency**: Checks for consistent Makefile patterns

### Expected Output

For deterministic Makefiles (our case):
```
Transformations Applied: 0
Issues Fixed: 0
Manual Fixes Needed: 0
```

## Makefile Best Practices

### 1. Always Use .PHONY

Mark targets that don't create files:
```makefile
.PHONY: help test clean
```

### 2. Silent Commands with @

Use `@` to suppress command echoing:
```makefile
test:
	@echo "Running tests..."
	@pytest test.py
```

### 3. Error Handling

Fail fast on errors:
```makefile
compile-all:
	@for dir in examples/*/; do \
		$(MAKE) -C "$$dir" compile || exit 1; \
	done
```

### 4. Sorted Wildcards

Ensure deterministic file order:
```makefile
# Bad (non-deterministic)
SOURCES := $(wildcard src/*.c)

# Good (deterministic)
SOURCES := $(sort $(wildcard src/*.c))
```

## Regenerating Makefiles

While Makefiles are manually written, the `generate_makefiles.sh` script serves two purposes:

### 1. Validation

Validates all Makefiles for determinism:
```bash
./scripts/generate_makefiles.sh
```

### 2. Template Application

When adding a new example:
1. Copy an existing example Makefile
2. Update variables (PYTHON_SCRIPT, RUST_BINARY, TEST_SCRIPT)
3. Run `./scripts/generate_makefiles.sh` to validate

## Integration with Quality Gates

Makefile validation is integrated into the quality gates:

```bash
# Check during lint
make lint
```

The `lint` target includes:
```makefile
lint:
	@bashrs make purify --report Makefile
```

## Why Not Full Code Generation?

We chose manual Makefiles over code generation because:

1. **Simplicity**: Makefiles are straightforward and widely understood
2. **Maintainability**: Easier to read and modify by hand
3. **Flexibility**: Can customize per-example without template complexity
4. **Validation**: bashrs provides validation without code generation overhead

## Alternative Approaches Considered

### Makefile.rs DSL

Initially considered using a Rust DSL to generate Makefiles:
```rust
// This approach was NOT used
use bashrs::makefile::*;

fn main() {
    let mut makefile = Makefile::new();
    makefile.target("test").recipe("pytest test.py");
}
```

**Rejected because:**
- Adds complexity without clear benefits
- bashrs focuses on purification, not generation
- Manual Makefiles are sufficient for this project

### bashrs make generate

Considered using bashrs code generation:
```bash
# This approach was NOT used
bashrs make generate Makefile.template -o Makefile
```

**Rejected because:**
- bashrs doesn't have a generation API (only purification)
- Templates would duplicate the complexity of Makefiles themselves

## Future Enhancements

### Potential Improvements

1. **Makefile Templates**: Create a `scripts/new_example.sh` that generates boilerplate
2. **Automated Updates**: Script to update all Makefiles when patterns change
3. **Validation CI**: Run `bashrs make purify --report` in GitHub Actions

### Not Planned

1. **Full Code Generation**: Unnecessary complexity for this project
2. **DSL Development**: Would require maintaining custom tooling

## References

- [bashrs make purify documentation](https://github.com/paiml/bashrs)
- [GNU Make Manual](https://www.gnu.org/software/make/manual/)
- [Makefile Best Practices](https://tech.davis-hansson.com/p/make/)

---

**Last Updated:** 2025-11-12
**Status:** ✅ Production Ready
