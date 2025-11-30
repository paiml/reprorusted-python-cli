#!/usr/bin/env bash
# CI Runner for Corpus Validation (GH-22)
#
# Runs corpus validation and compares against baseline.
# Exits non-zero if regression detected.
#
# Usage:
#   ./scripts/ci_runner.sh [OPTIONS]
#
# Options:
#   -h, --help      Show this help message
#   --ci            CI mode (GitHub Actions compatible output)
#   --no-fail       Don't fail on regression (report only)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BASELINE_FILE="$PROJECT_ROOT/data/ci_baseline.json"
CORPUS_FILE="$PROJECT_ROOT/data/labeled_corpus.parquet"

CI_MODE=false
NO_FAIL=false

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Run corpus validation for CI/CD pipeline.
Compares current results against baseline and detects regression.

Options:
  -h, --help      Show this help message
  --ci            CI mode (GitHub Actions compatible markdown output)
  --no-fail       Don't exit 1 on regression (report only)

Exit Codes:
  0  - Success (no regression)
  1  - Regression detected (success rate decreased)

Examples:
  $(basename "$0")        # Local run
  $(basename "$0") --ci   # GitHub Actions mode
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        --ci)
            CI_MODE=true
            shift
            ;;
        --no-fail)
            NO_FAIL=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

# Get current metrics
get_current_metrics() {
    uv run python3 << 'PYTHON'
import json
import pyarrow.parquet as pq

df = pq.read_table("data/labeled_corpus.parquet").to_pandas()
total = len(df)
success = int(df["has_rust"].sum())
failing = total - success
rate = round(success * 100 / total, 1) if total > 0 else 0

print(json.dumps({
    "total": total,
    "success": success,
    "failing": failing,
    "rate": rate
}))
PYTHON
}

# Get baseline metrics
get_baseline() {
    if [[ -f "$BASELINE_FILE" ]]; then
        cat "$BASELINE_FILE"
    else
        echo '{"total": 0, "success": 0, "failing": 0, "rate": 0}'
    fi
}

# Save current as baseline
save_baseline() {
    local metrics="$1"
    echo "$metrics" > "$BASELINE_FILE"
}

# Output markdown table for GitHub
output_markdown() {
    local current="$1"
    local baseline="$2"

    local cur_rate cur_failing cur_success
    cur_rate=$(echo "$current" | jq -r '.rate')
    cur_failing=$(echo "$current" | jq -r '.failing')
    cur_success=$(echo "$current" | jq -r '.success')

    local base_rate base_failing base_success
    base_rate=$(echo "$baseline" | jq -r '.rate')
    base_failing=$(echo "$baseline" | jq -r '.failing')
    base_success=$(echo "$baseline" | jq -r '.success')

    # Calculate changes
    local rate_delta failing_delta
    rate_delta=$(echo "$cur_rate - $base_rate" | bc)
    failing_delta=$((cur_failing - base_failing))

    # Determine status
    local status_icon
    if (( $(echo "$rate_delta >= 0" | bc -l) )); then
        status_icon="✅"
    else
        status_icon="❌"
    fi

    local rate_change failing_change
    if (( $(echo "$rate_delta > 0" | bc -l) )); then
        rate_change="+${rate_delta}%"
    else
        rate_change="${rate_delta}%"
    fi

    if [[ $failing_delta -gt 0 ]]; then
        failing_change="+${failing_delta}"
    else
        failing_change="${failing_delta}"
    fi

    cat << EOF
## Corpus Validation Results $status_icon

| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| Success Rate | ${base_rate}% | ${cur_rate}% | ${rate_change} |
| Successful | ${base_success} | ${cur_success} | $((cur_success - base_success)) |
| Failing | ${base_failing} | ${cur_failing} | ${failing_change} |

EOF

    if (( $(echo "$rate_delta < 0" | bc -l) )); then
        echo "⚠️ **Regression detected**: Success rate decreased by ${rate_delta}%"
    elif (( $(echo "$rate_delta > 0" | bc -l) )); then
        echo "🎉 **Improvement**: Success rate increased by +${rate_delta}%"
    else
        echo "➡️ **No change**: Success rate unchanged"
    fi
}

# Output console report
output_console() {
    local current="$1"
    local baseline="$2"

    local cur_rate base_rate rate_delta
    cur_rate=$(echo "$current" | jq -r '.rate')
    base_rate=$(echo "$baseline" | jq -r '.rate')
    rate_delta=$(echo "$cur_rate - $base_rate" | bc)

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "CI CORPUS VALIDATION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "Baseline: %s%%\n" "$base_rate"
    printf "Current:  %s%%\n" "$cur_rate"
    printf "Change:   %s%%\n" "$rate_delta"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if (( $(echo "$rate_delta < 0" | bc -l) )); then
        echo "❌ REGRESSION DETECTED"
    elif (( $(echo "$rate_delta > 0" | bc -l) )); then
        echo "✅ IMPROVEMENT"
    else
        echo "➡️ NO CHANGE"
    fi
}

# Main
main() {
    if [[ ! -f "$CORPUS_FILE" ]]; then
        echo "Error: Corpus not found. Run 'make corpus-label' first." >&2
        exit 1
    fi

    local current baseline
    current=$(get_current_metrics)
    baseline=$(get_baseline)

    # Output results
    if [[ "$CI_MODE" == true ]]; then
        output_markdown "$current" "$baseline"
    else
        output_console "$current" "$baseline"
    fi

    # Check for regression
    local cur_rate base_rate
    cur_rate=$(echo "$current" | jq -r '.rate')
    base_rate=$(echo "$baseline" | jq -r '.rate')

    if (( $(echo "$cur_rate < $base_rate" | bc -l) )); then
        if [[ "$NO_FAIL" != true ]]; then
            exit 1
        fi
    fi
}

main
