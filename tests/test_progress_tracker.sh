#!/usr/bin/env bash
# Extreme TDD tests for Progress Tracking (GH-19)
#
# Run with: bash tests/test_progress_tracker.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TRACKER_SCRIPT="$PROJECT_ROOT/scripts/progress_tracker.sh"

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
echo "PROGRESS TRACKING TESTS (GH-19)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test 1: Script exists
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$TRACKER_SCRIPT" ]; then
    test_pass "progress_tracker.sh exists"
else
    test_fail "progress_tracker.sh does not exist"
fi

# Test 2: Script is executable
TESTS_RUN=$((TESTS_RUN + 1))
if [ -x "$TRACKER_SCRIPT" ]; then
    test_pass "progress_tracker.sh is executable"
else
    test_fail "progress_tracker.sh is not executable"
fi

# Test 3: Help flag works
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$TRACKER_SCRIPT" ] && "$TRACKER_SCRIPT" --help 2>/dev/null | grep -qi "usage\|help"; then
    test_pass "--help shows usage"
else
    test_fail "--help does not show usage"
fi

# Test 4: Record flag documented
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$TRACKER_SCRIPT" ] && "$TRACKER_SCRIPT" --help 2>/dev/null | grep -q "\-\-record\|\-r"; then
    test_pass "--record flag documented"
else
    test_fail "--record flag not documented"
fi

# Test 5: History flag documented
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$TRACKER_SCRIPT" ] && "$TRACKER_SCRIPT" --help 2>/dev/null | grep -q "\-\-history"; then
    test_pass "--history flag documented"
else
    test_fail "--history flag not documented"
fi

# Test 6: Uses JSONL format
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$TRACKER_SCRIPT" ] && grep -q "jsonl\|\.jsonl" "$TRACKER_SCRIPT" 2>/dev/null; then
    test_pass "Script uses JSONL format"
else
    test_fail "Script does not use JSONL format"
fi

# Test 7: Records depyler version
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$TRACKER_SCRIPT" ] && grep -q "depyler\|version" "$TRACKER_SCRIPT" 2>/dev/null; then
    test_pass "Script tracks depyler version"
else
    test_fail "Script does not track version"
fi

# Test 8: Shows trend indicator
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$TRACKER_SCRIPT" ] && grep -qi "trend\|spark\|▁\|▅\|█" "$TRACKER_SCRIPT" 2>/dev/null; then
    test_pass "Script shows trend indicator"
else
    test_fail "Script does not show trend"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "Tests: %d | Passed: ${GREEN}%d${NC} | Failed: ${RED}%d${NC}\n" "$TESTS_RUN" "$TESTS_PASSED" "$TESTS_FAILED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$TESTS_FAILED" -gt 0 ]; then
    exit 1
fi
exit 0
