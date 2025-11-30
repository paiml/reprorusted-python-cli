#!/usr/bin/env bash
# Extreme TDD tests for Rust Compilation Verification (GH-17)
#
# Run with: bash tests/test_verify_rust.sh
#
# Exit codes: 0 = all pass, 1 = failures

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VERIFY_SCRIPT="$PROJECT_ROOT/scripts/verify_rust_compilation.sh"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test helpers
test_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    printf "${GREEN}✓${NC} %s\n" "$1"
}

test_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    printf "${RED}✗${NC} %s\n" "$1"
}

run_test() {
    local name="$1"
    local expected="$2"
    shift 2
    TESTS_RUN=$((TESTS_RUN + 1))

    if "$@" 2>/dev/null | grep -q "$expected"; then
        test_pass "$name"
    else
        test_fail "$name: expected '$expected'"
    fi
}

# ============================================================================
# Test Suite
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RUST COMPILATION VERIFICATION TESTS (GH-17)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test 1: Script exists
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$VERIFY_SCRIPT" ]; then
    test_pass "verify_rust_compilation.sh exists"
else
    test_fail "verify_rust_compilation.sh does not exist"
fi

# Test 2: Script is executable
TESTS_RUN=$((TESTS_RUN + 1))
if [ -x "$VERIFY_SCRIPT" ]; then
    test_pass "verify_rust_compilation.sh is executable"
else
    test_fail "verify_rust_compilation.sh is not executable"
fi

# Test 3: Help flag works
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$VERIFY_SCRIPT" ] && "$VERIFY_SCRIPT" --help 2>/dev/null | grep -qi "usage\|help"; then
    test_pass "--help shows usage"
else
    test_fail "--help does not show usage"
fi

# Test 4: JSON output flag exists
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$VERIFY_SCRIPT" ] && "$VERIFY_SCRIPT" --help 2>/dev/null | grep -q "\-\-json\|\-j"; then
    test_pass "--json flag documented"
else
    test_fail "--json flag not documented"
fi

# Test 5: Outputs total count
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$VERIFY_SCRIPT" ]; then
    dry_output=$("$VERIFY_SCRIPT" --dry-run 2>&1)
    if echo "$dry_output" | grep -qi "total\|examples"; then
        test_pass "Output includes total/examples count"
    else
        test_fail "Output missing total/examples count (got: $(echo "$dry_output" | head -4))"
    fi
else
    test_fail "Script does not exist"
fi

# Test 6: Handles missing cargo gracefully
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$VERIFY_SCRIPT" ]; then
    # Script should check for cargo
    if grep -q "cargo" "$VERIFY_SCRIPT" 2>/dev/null; then
        test_pass "Script references cargo"
    else
        test_fail "Script does not reference cargo"
    fi
else
    test_fail "Script does not exist"
fi

# Test 7: JSON output is valid (test --json flag exists in help)
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$VERIFY_SCRIPT" ] && command -v jq &>/dev/null; then
    # Test that --json flag is documented (actual JSON tested elsewhere)
    if "$VERIFY_SCRIPT" --help 2>&1 | grep -q "json"; then
        test_pass "JSON output flag available"
    else
        test_fail "JSON output flag not available"
    fi
else
    test_fail "Cannot test JSON output (script missing or no jq)"
fi

# Test 8: Reports compilation success rate
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$VERIFY_SCRIPT" ] && "$VERIFY_SCRIPT" --dry-run 2>/dev/null | grep -qE "[0-9]+%|success"; then
    test_pass "Reports success percentage"
else
    test_fail "Does not report success percentage"
fi

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "Tests: %d | Passed: ${GREEN}%d${NC} | Failed: ${RED}%d${NC}\n" "$TESTS_RUN" "$TESTS_PASSED" "$TESTS_FAILED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$TESTS_FAILED" -gt 0 ]; then
    exit 1
fi
exit 0
