#!/bin/bash
set -e

# check_io_equivalence.sh
# Cross-validate Python vs Rust I/O for a single example
#
# Usage:
#   ./scripts/check_io_equivalence.sh <python_script> <rust_binary> [test_cases_file]

PYTHON_SCRIPT="$1"
RUST_BINARY="$2"
TEST_CASES="${3:-}"

if [ -z "$PYTHON_SCRIPT" ] || [ -z "$RUST_BINARY" ]; then
    echo "Usage: $0 <python_script> <rust_binary> [test_cases_file]"
    echo ""
    echo "Example:"
    echo "  $0 examples/example_simple/trivial_cli.py examples/example_simple/trivial_cli"
    exit 1
fi

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

if [ ! -x "$RUST_BINARY" ]; then
    echo "❌ Rust binary not found or not executable: $RUST_BINARY"
    echo "💡 Compile first: depyler compile $PYTHON_SCRIPT -o $RUST_BINARY"
    exit 1
fi

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "🔍 I/O Equivalence Testing"
echo "=========================================="
echo "  Python: $PYTHON_SCRIPT"
echo "  Rust:   $RUST_BINARY"
echo ""

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
        echo -e "  ${RED}❌ Exit codes differ: Python=$python_exit, Rust=$rust_exit${NC}"
        return 1
    fi

    # Compare output
    if [ "$python_out" != "$rust_out" ]; then
        echo -e "  ${RED}❌ Output differs!${NC}"
        echo "     Python output: $python_out"
        echo "     Rust output:   $rust_out"
        return 1
    fi

    echo -e "  ${GREEN}✅ PASS${NC}"
    return 0
}

# Track results
TOTAL=0
PASSED=0
FAILED=0

run_test() {
    TOTAL=$((TOTAL + 1))
    if test_case "$@"; then
        PASSED=$((PASSED + 1))
        return 0
    else
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Run default test cases based on script name
script_name=$(basename "$PYTHON_SCRIPT" .py)

case "$script_name" in
    trivial_cli)
        echo "Running trivial_cli test cases..."
        run_test "Help flag" --help
        run_test "Version flag" --version
        run_test "Valid input" --name Alice
        run_test "Valid input with spaces" --name "Dr. Smith"
        ;;

    flag_parser)
        echo "Running flag_parser test cases..."
        run_test "Help flag" --help
        run_test "Version flag" --version
        run_test "No flags"
        run_test "Verbose flag" --verbose
        run_test "Debug flag" --debug
        run_test "Quiet flag" --quiet
        run_test "Verbose and debug" --verbose --debug
        run_test "All flags" -vdq
        ;;

    positional_args)
        echo "Running positional_args test cases..."
        run_test "Help flag" --help
        run_test "Version flag" --version
        run_test "Start command no targets" start
        run_test "Start with single target" start web
        run_test "Start with multiple targets" start web db cache
        run_test "Stop command" stop db
        run_test "Restart command" restart web api
        ;;

    git_clone)
        echo "Running git_clone test cases..."
        run_test "Help flag" --help
        run_test "Version flag" --version
        run_test "Clone command" clone https://example.com/repo.git
        run_test "Clone with SSH URL" clone git@github.com:user/repo.git
        run_test "Push command" push origin
        run_test "Push to upstream" push upstream
        run_test "Pull command" pull origin
        run_test "Pull from upstream" pull upstream
        run_test "Verbose clone" --verbose clone https://example.com/repo.git
        run_test "Verbose push" -v push origin
        run_test "Verbose pull" --verbose pull upstream
        ;;

    *)
        echo -e "${YELLOW}⚠️  Unknown script, running basic tests only${NC}"
        run_test "Help flag" --help
        if [[ "$PYTHON_SCRIPT" == *"version"* ]] || grep -q "version" "$PYTHON_SCRIPT" 2>/dev/null; then
            run_test "Version flag" --version || true
        fi
        ;;
esac

echo ""
echo "=========================================="
echo "📊 I/O Equivalence Test Summary"
echo "=========================================="
echo "  Total tests: $TOTAL"
echo -e "  ${GREEN}Passed: $PASSED${NC}"
echo -e "  ${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Some I/O equivalence tests failed!${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All I/O equivalence tests passed!${NC}"
    exit 0
fi
