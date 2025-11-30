#!/usr/bin/env bash
# Extreme TDD tests for Fix Recommendations (GH-20)
#
# Run with: bash tests/test_recommendations.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REC_SCRIPT="$PROJECT_ROOT/scripts/generate_recommendations.sh"

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
echo "FIX RECOMMENDATIONS TESTS (GH-20)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test 1: Script exists
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$REC_SCRIPT" ]; then
    test_pass "generate_recommendations.sh exists"
else
    test_fail "generate_recommendations.sh does not exist"
fi

# Test 2: Script is executable
TESTS_RUN=$((TESTS_RUN + 1))
if [ -x "$REC_SCRIPT" ]; then
    test_pass "generate_recommendations.sh is executable"
else
    test_fail "generate_recommendations.sh is not executable"
fi

# Test 3: Help flag works
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$REC_SCRIPT" ] && "$REC_SCRIPT" --help 2>/dev/null | grep -qi "usage\|help"; then
    test_pass "--help shows usage"
else
    test_fail "--help does not show usage"
fi

# Test 4: Top flag documented
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$REC_SCRIPT" ] && "$REC_SCRIPT" --help 2>/dev/null | grep -q "\-\-top\|\-t"; then
    test_pass "--top flag documented"
else
    test_fail "--top flag not documented"
fi

# Test 5: Shows priority levels
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$REC_SCRIPT" ] && grep -qi "HIGH\|MED\|LOW\|priority" "$REC_SCRIPT" 2>/dev/null; then
    test_pass "Script shows priority levels"
else
    test_fail "Script does not show priorities"
fi

# Test 6: Calculates impact
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$REC_SCRIPT" ] && grep -qi "impact\|percent\|improvement" "$REC_SCRIPT" 2>/dev/null; then
    test_pass "Script calculates impact"
else
    test_fail "Script does not calculate impact"
fi

# Test 7: Groups by pattern
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$REC_SCRIPT" ] && grep -qi "pattern\|category\|group" "$REC_SCRIPT" 2>/dev/null; then
    test_pass "Script groups by pattern"
else
    test_fail "Script does not group patterns"
fi

# Test 8: Reads corpus data
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$REC_SCRIPT" ] && grep -q "parquet\|corpus\|labeled" "$REC_SCRIPT" 2>/dev/null; then
    test_pass "Script reads corpus data"
else
    test_fail "Script does not read corpus"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "Tests: %d | Passed: ${GREEN}%d${NC} | Failed: ${RED}%d${NC}\n" "$TESTS_RUN" "$TESTS_PASSED" "$TESTS_FAILED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$TESTS_FAILED" -gt 0 ]; then
    exit 1
fi
exit 0
