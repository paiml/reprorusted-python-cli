#!/bin/bash
# Test compilation of all examples using cargo
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
FAILED_EXAMPLES=()

echo "=========================================="
echo "Testing All Examples Compilation (cargo)"
echo "=========================================="
echo ""

for example in "${EXAMPLES[@]}"; do
    name=$(basename "$example" .py)
    dir=$(dirname "$example")

    echo "📦 Testing: $name"
    echo "   Path: examples/$dir"

    cd "examples/$dir"

    # Clean previous build
    cargo clean 2>/dev/null || true
    rm -f *.rs 2>/dev/null || true

    # Try transpilation
    if /home/noah/src/depyler/target/release/depyler transpile "$name.py" -o "$name.rs" 2>&1 | grep -E "(Error|Output:|Total time:)" || true; then
        if [ -f "$name.rs" ]; then
            echo "   ✅ Transpilation: SUCCESS"

            # Try compilation with cargo
            if cargo build --release 2>&1 | tail -5; then
                if [ $? -eq 0 ]; then
                    echo "   ✅ Compilation: SUCCESS"
                    PASSED=$((PASSED + 1))
                else
                    echo "   ❌ Compilation: FAILED"
                    ERROR_COUNT=$(cargo build --release 2>&1 | grep -c "error\[" || echo 0)
                    echo "   Error count: $ERROR_COUNT"
                    BUILD_FAILED=$((BUILD_FAILED + 1))
                    FAILED=$((FAILED + 1))
                    FAILED_EXAMPLES+=("$name (build)")
                fi
            fi
        else
            echo "   ❌ Transpilation: FAILED"
            TRANSPILE_FAILED=$((TRANSPILE_FAILED + 1))
            FAILED=$((FAILED + 1))
            FAILED_EXAMPLES+=("$name (transpile)")
        fi
    else
        echo "   ❌ Transpilation: FAILED"
        TRANSPILE_FAILED=$((TRANSPILE_FAILED + 1))
        FAILED=$((FAILED + 1))
        FAILED_EXAMPLES+=("$name (transpile)")
    fi

    echo ""
    cd /home/noah/src/reprorusted-python-cli
done

echo "=========================================="
echo "Summary"
echo "=========================================="
echo "✅ Passed: $PASSED / ${#EXAMPLES[@]}"
echo "❌ Failed: $FAILED"
echo "   - Transpile failures: $TRANSPILE_FAILED"
echo "   - Build failures: $BUILD_FAILED"
echo ""

if [ $FAILED -gt 0 ]; then
    echo "Failed examples:"
    for failed in "${FAILED_EXAMPLES[@]}"; do
        echo "  - $failed"
    done
fi

echo ""
echo "Success rate: $(echo "scale=1; $PASSED * 100 / ${#EXAMPLES[@]}" | bc)%"
