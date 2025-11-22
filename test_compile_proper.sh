#!/bin/bash
# Proper test compilation of all examples using cargo
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
declare -a FAILED_EXAMPLES

echo "=========================================="
echo "Testing All Examples Compilation"
echo "=========================================="
echo ""

for example in "${EXAMPLES[@]}"; do
    name=$(basename "$example" .py)
    dir=$(dirname "$example")

    echo "📦 Testing: $name"

    cd "examples/$dir"
    cargo clean >/dev/null 2>&1
    rm -f *.rs 2>/dev/null

    # Transpile
    if depyler transpile "$name.py" -o "$name.rs" >/dev/null 2>&1; then
        if [ -f "$name.rs" ]; then
            echo "   ✅ Transpilation: SUCCESS"

            # Compile
            if cargo build --release >/dev/null 2>&1; then
                echo "   ✅ Compilation: SUCCESS"
                PASSED=$((PASSED + 1))
            else
                ERROR_COUNT=$(cargo build --release 2>&1 | grep -c "^error\[" || echo 0)
                echo "   ❌ Compilation: FAILED ($ERROR_COUNT errors)"
                BUILD_FAILED=$((BUILD_FAILED + 1))
                FAILED=$((FAILED + 1))
                FAILED_EXAMPLES+=("$name (build: $ERROR_COUNT errors)")
            fi
        else
            echo "   ❌ Transpilation: FAILED (no output)"
            TRANSPILE_FAILED=$((TRANSPILE_FAILED + 1))
            FAILED=$((FAILED + 1))
            FAILED_EXAMPLES+=("$name (transpile: no output)")
        fi
    else
        ERR_MSG=$(depyler transpile "$name.py" -o "$name.rs" 2>&1 | grep "^Error:" | head -1 || echo "unknown error")
        echo "   ❌ Transpilation: FAILED"
        echo "      $ERR_MSG"
        TRANSPILE_FAILED=$((TRANSPILE_FAILED + 1))
        FAILED=$((FAILED + 1))
        FAILED_EXAMPLES+=("$name (transpile: $ERR_MSG)")
    fi

    cd /home/noah/src/reprorusted-python-cli
done

echo ""
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
PERCENT=$(awk "BEGIN {printf \"%.1f\", $PASSED * 100 / ${#EXAMPLES[@]}}")
echo "Success rate: $PERCENT%"
echo ""

exit $FAILED
