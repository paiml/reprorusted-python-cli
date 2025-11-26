#!/bin/bash
# Test compilation of all examples
set -e

cd /home/noah/src/reprorusted-python-cli

EXAMPLES=(
    "example_simple/trivial_cli.py"
    "example_flags/flag_parser.py"
    "example_positional/positional_args.py"
    "example_subcommands/git_clone.py"
    "example_complex/complex_cli.py"
    "example_stdlib/stdlib_integration.py"
    "example_config/config_manager.py"
    "example_subprocess/task_runner.py"
    "example_environment/env_info.py"
    "example_regex/pattern_matcher.py"
    "example_io_streams/stream_processor.py"
    "example_csv_filter/csv_filter.py"
    "example_log_analyzer/log_analyzer.py"
)

PASSED=0
FAILED=0
TRANSPILE_FAILED=0
BUILD_FAILED=0

echo "=========================================="
echo "Testing All Examples Compilation"
echo "=========================================="
echo ""

for example in "${EXAMPLES[@]}"; do
    name=$(basename "$example" .py)
    dir=$(dirname "$example")

    echo "📦 Testing: $name"
    echo "   Path: examples/$dir"

    cd "examples/$dir"

    # Clean previous build
    rm -f "$name" "${name}_rust" *.rs 2>/dev/null || true

    # Try transpilation
    if /home/noah/src/depyler/target/release/depyler transpile "$name.py" -o "${name}_output.rs" 2>&1 | tee /tmp/transpile_${name}.log; then
        echo "   ✅ Transpilation: SUCCESS"

        # Try compilation
        if rustc --edition 2021 "${name}_output.rs" -o "${name}_rust" 2>&1 | tee /tmp/compile_${name}.log; then
            echo "   ✅ Compilation: SUCCESS"
            PASSED=$((PASSED + 1))
        else
            echo "   ❌ Compilation: FAILED"
            echo "   Error count: $(grep -c "error\[" /tmp/compile_${name}.log || echo 0)"
            BUILD_FAILED=$((BUILD_FAILED + 1))
            FAILED=$((FAILED + 1))
        fi
    else
        echo "   ❌ Transpilation: FAILED"
        TRANSPILE_FAILED=$((TRANSPILE_FAILED + 1))
        FAILED=$((FAILED + 1))
    fi

    echo ""
    cd /home/noah/src/reprorusted-python-cli
done

echo "=========================================="
echo "Summary"
echo "=========================================="
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo "   - Transpile failures: $TRANSPILE_FAILED"
echo "   - Build failures: $BUILD_FAILED"
echo ""
echo "Success rate: $PASSED / ${#EXAMPLES[@]}"
