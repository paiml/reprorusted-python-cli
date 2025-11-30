#!/usr/bin/env bash
# Extreme TDD tests for Rust Error Analysis (GH-18)
#
# Run with: bash tests/test_analyze_rust_errors.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ANALYZE_SCRIPT="$PROJECT_ROOT/scripts/analyze_rust_errors.sh"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

test_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    printf "${GREEN}✓${NC} %s\n" "$1"
}

test_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    printf "${RED}✗${NC} %s\n" "$1"
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RUST ERROR ANALYSIS TESTS (GH-18)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test 1: Script exists
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$ANALYZE_SCRIPT" ]; then
    test_pass "analyze_rust_errors.sh exists"
else
    test_fail "analyze_rust_errors.sh does not exist"
fi

# Test 2: Script is executable
TESTS_RUN=$((TESTS_RUN + 1))
if [ -x "$ANALYZE_SCRIPT" ]; then
    test_pass "analyze_rust_errors.sh is executable"
else
    test_fail "analyze_rust_errors.sh is not executable"
fi

# Test 3: Help flag works
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$ANALYZE_SCRIPT" ] && "$ANALYZE_SCRIPT" --help 2>/dev/null | grep -qi "usage\|help"; then
    test_pass "--help shows usage"
else
    test_fail "--help does not show usage"
fi

# Test 4: Summary flag documented
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$ANALYZE_SCRIPT" ] && "$ANALYZE_SCRIPT" --help 2>/dev/null | grep -q "\-\-summary\|\-s"; then
    test_pass "--summary flag documented"
else
    test_fail "--summary flag not documented"
fi

# Test 5: JSON output flag documented
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$ANALYZE_SCRIPT" ] && "$ANALYZE_SCRIPT" --help 2>/dev/null | grep -q "\-\-json\|\-j"; then
    test_pass "--json flag documented"
else
    test_fail "--json flag not documented"
fi

# Test 6: Parses error codes (E0XXX pattern)
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$ANALYZE_SCRIPT" ] && grep -q "E0[0-9]\{3\}\|error\[E" "$ANALYZE_SCRIPT" 2>/dev/null; then
    test_pass "Script parses E0XXX error codes"
else
    test_fail "Script does not parse error codes"
fi

# Test 7: Can process sample error input
TESTS_RUN=$((TESTS_RUN + 1))
sample_error="error[E0432]: unresolved import"
if [ -f "$ANALYZE_SCRIPT" ]; then
    result=$(echo "$sample_error" | "$ANALYZE_SCRIPT" --stdin 2>/dev/null || echo "")
    if echo "$result" | grep -qi "E0432\|unresolved\|import"; then
        test_pass "Processes error input correctly"
    else
        test_fail "Cannot process error input"
    fi
else
    test_fail "Script does not exist"
fi

# Test 8: Outputs category counts
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$ANALYZE_SCRIPT" ] && "$ANALYZE_SCRIPT" --help 2>/dev/null | grep -qi "category\|count\|summary"; then
    test_pass "Supports category counting"
else
    test_fail "No category counting support"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "Tests: %d | Passed: ${GREEN}%d${NC} | Failed: ${RED}%d${NC}\n" "$TESTS_RUN" "$TESTS_PASSED" "$TESTS_FAILED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$TESTS_FAILED" -gt 0 ]; then
    exit 1
fi
exit 0
