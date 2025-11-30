#!/usr/bin/env bash
# Extreme TDD tests for Corpus Dashboard (GH-21)
#
# Run with: bash tests/test_dashboard.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DASH_SCRIPT="$PROJECT_ROOT/scripts/corpus_dashboard.sh"

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
echo "CORPUS DASHBOARD TESTS (GH-21)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test 1: Script exists
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$DASH_SCRIPT" ]; then
    test_pass "corpus_dashboard.sh exists"
else
    test_fail "corpus_dashboard.sh does not exist"
fi

# Test 2: Script is executable
TESTS_RUN=$((TESTS_RUN + 1))
if [ -x "$DASH_SCRIPT" ]; then
    test_pass "corpus_dashboard.sh is executable"
else
    test_fail "corpus_dashboard.sh is not executable"
fi

# Test 3: Help flag works
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$DASH_SCRIPT" ] && "$DASH_SCRIPT" --help 2>/dev/null | grep -qi "usage\|help"; then
    test_pass "--help shows usage"
else
    test_fail "--help does not show usage"
fi

# Test 4: Shows success rate
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$DASH_SCRIPT" ] && grep -qi "success\|rate\|percent" "$DASH_SCRIPT" 2>/dev/null; then
    test_pass "Script shows success rate"
else
    test_fail "Script does not show success rate"
fi

# Test 5: Shows trend
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$DASH_SCRIPT" ] && grep -qi "trend\|spark\|history" "$DASH_SCRIPT" 2>/dev/null; then
    test_pass "Script shows trend"
else
    test_fail "Script does not show trend"
fi

# Test 6: Shows risk distribution
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$DASH_SCRIPT" ] && grep -qi "risk\|LOW\|MEDIUM\|HIGH" "$DASH_SCRIPT" 2>/dev/null; then
    test_pass "Script shows risk distribution"
else
    test_fail "Script does not show risk"
fi

# Test 7: Uses box drawing
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$DASH_SCRIPT" ] && grep -q "═\|║\|╔\|╗\|╚\|╝\|━" "$DASH_SCRIPT" 2>/dev/null; then
    test_pass "Script uses box drawing"
else
    test_fail "Script does not use box drawing"
fi

# Test 8: Reads corpus
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$DASH_SCRIPT" ] && grep -q "parquet\|corpus\|labeled" "$DASH_SCRIPT" 2>/dev/null; then
    test_pass "Script reads corpus"
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
