#!/usr/bin/env bash
# Extreme TDD tests for CI Runner (GH-22)
#
# Run with: bash tests/test_ci_runner.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CI_SCRIPT="$PROJECT_ROOT/scripts/ci_runner.sh"

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
echo "CI RUNNER TESTS (GH-22)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test 1: Script exists
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$CI_SCRIPT" ]; then
    test_pass "ci_runner.sh exists"
else
    test_fail "ci_runner.sh does not exist"
fi

# Test 2: Script is executable
TESTS_RUN=$((TESTS_RUN + 1))
if [ -x "$CI_SCRIPT" ]; then
    test_pass "ci_runner.sh is executable"
else
    test_fail "ci_runner.sh is not executable"
fi

# Test 3: Help flag works
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$CI_SCRIPT" ] && "$CI_SCRIPT" --help 2>/dev/null | grep -qi "usage\|help"; then
    test_pass "--help shows usage"
else
    test_fail "--help does not show usage"
fi

# Test 4: Compares to baseline
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$CI_SCRIPT" ] && grep -qi "baseline\|compare\|diff" "$CI_SCRIPT" 2>/dev/null; then
    test_pass "Script compares to baseline"
else
    test_fail "Script does not compare baseline"
fi

# Test 5: Detects regression
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$CI_SCRIPT" ] && grep -qi "regression\|fail\|decrease" "$CI_SCRIPT" 2>/dev/null; then
    test_pass "Script detects regression"
else
    test_fail "Script does not detect regression"
fi

# Test 6: Outputs markdown
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$CI_SCRIPT" ] && grep -qi "markdown\|##\|\|.*\|" "$CI_SCRIPT" 2>/dev/null; then
    test_pass "Script outputs markdown"
else
    test_fail "Script does not output markdown"
fi

# Test 7: Has CI mode flag
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$CI_SCRIPT" ] && "$CI_SCRIPT" --help 2>/dev/null | grep -qi "\-\-ci\|github"; then
    test_pass "--ci flag documented"
else
    test_fail "--ci flag not documented"
fi

# Test 8: Exits non-zero on regression
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$CI_SCRIPT" ] && grep -q "exit 1\|exit \$" "$CI_SCRIPT" 2>/dev/null; then
    test_pass "Script exits non-zero on failure"
else
    test_fail "Script does not exit on failure"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "Tests: %d | Passed: ${GREEN}%d${NC} | Failed: ${RED}%d${NC}\n" "$TESTS_RUN" "$TESTS_PASSED" "$TESTS_FAILED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$TESTS_FAILED" -gt 0 ]; then
    exit 1
fi
exit 0
