#!/usr/bin/env bash
# Corpus Diff Tool (GH-14) - Compare quality reports using jq
# Usage: ./scripts/corpus_diff.sh baseline.json current.json

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    echo "Usage: $0 <baseline.json> <current.json>"
    echo ""
    echo "Compare two corpus quality reports and show improvement metrics."
    exit 1
}

if [[ $# -lt 2 ]]; then
    usage
fi

BASELINE="$1"
CURRENT="$2"

if [[ ! -f "$BASELINE" ]]; then
    echo -e "${RED}Error: Baseline file not found: $BASELINE${NC}"
    exit 1
fi

if [[ ! -f "$CURRENT" ]]; then
    echo -e "${RED}Error: Current file not found: $CURRENT${NC}"
    exit 1
fi

# Check jq is available
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed${NC}"
    exit 1
fi

# Extract metrics
baseline_success=$(jq -r '.metrics.success_rate // 0' "$BASELINE")
current_success=$(jq -r '.metrics.success_rate // 0' "$CURRENT")

baseline_total=$(jq -r '.metrics.total_samples // 0' "$BASELINE")
current_total=$(jq -r '.metrics.total_samples // 0' "$CURRENT")

baseline_successful=$(jq -r '.metrics.successful_count // 0' "$BASELINE")
current_successful=$(jq -r '.metrics.successful_count // 0' "$CURRENT")

baseline_high=$(jq -r '.metrics.risk_distribution.HIGH_RISK // 0' "$BASELINE")
current_high=$(jq -r '.metrics.risk_distribution.HIGH_RISK // 0' "$CURRENT")

# Calculate deltas
success_delta=$(echo "$current_success - $baseline_success" | bc)
successful_delta=$((current_successful - baseline_successful))
high_delta=$((current_high - baseline_high))

# Format delta with sign
format_delta() {
    local val=$1
    if (( $(echo "$val > 0" | bc -l) )); then
        echo -e "${GREEN}+$val${NC}"
    elif (( $(echo "$val < 0" | bc -l) )); then
        echo -e "${RED}$val${NC}"
    else
        echo "$val"
    fi
}

# Print report
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CORPUS IMPROVEMENT REPORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Baseline: $BASELINE"
echo "Current:  $CURRENT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "METRICS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "%-20s %10s → %-10s %s\n" "Success Rate:" "${baseline_success}%" "${current_success}%" "($(format_delta "$success_delta")%)"
printf "%-20s %10s → %-10s %s\n" "Successful:" "$baseline_successful" "$current_successful" "($(format_delta "$successful_delta"))"
printf "%-20s %10s → %-10s %s\n" "Total Samples:" "$baseline_total" "$current_total" ""
printf "%-20s %10s → %-10s %s\n" "HIGH_RISK:" "$baseline_high" "$current_high" "($(format_delta "$high_delta"))"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Determine overall status
if (( $(echo "$success_delta > 0" | bc -l) )); then
    echo -e "${GREEN}✅ IMPROVED: Success rate increased by ${success_delta}%${NC}"
    exit 0
elif (( $(echo "$success_delta < 0" | bc -l) )); then
    echo -e "${RED}❌ REGRESSED: Success rate decreased by ${success_delta}%${NC}"
    exit 1
else
    echo -e "${YELLOW}➖ NO CHANGE: Success rate unchanged${NC}"
    exit 0
fi
