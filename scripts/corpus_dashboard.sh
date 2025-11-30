#!/usr/bin/env bash
# Corpus Dashboard (GH-21)
#
# Unified view of all corpus metrics.
#
# Usage:
#   ./scripts/corpus_dashboard.sh [OPTIONS]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CORPUS_FILE="$PROJECT_ROOT/data/labeled_corpus.parquet"
HISTORY_FILE="$PROJECT_ROOT/data/progress_history.jsonl"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Show unified corpus dashboard with all key metrics.

Options:
  -h, --help    Show this help message

Displays:
  - Success rate and trend sparkline
  - Risk distribution (LOW/MEDIUM/HIGH)
  - Top failing categories
  - Depyler version
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

# Get corpus metrics
get_metrics() {
    uv run python3 << 'PYTHON'
import json
import pyarrow.parquet as pq

df = pq.read_table("data/labeled_corpus.parquet").to_pandas()
total = len(df)
success = df["has_rust"].sum()
rate = round(success * 100 / total, 1) if total > 0 else 0

# Risk distribution
risk_counts = df["risk_label"].value_counts().to_dict() if "risk_label" in df.columns else {}

# Top failures
failing = df[~df["has_rust"]]
top_failures = failing["category"].value_counts().head(5).to_dict()

print(json.dumps({
    "total": int(total),
    "success": int(success),
    "rate": float(rate),
    "risk": {k: int(v) for k, v in risk_counts.items()},
    "top_failures": top_failures
}))
PYTHON
}

# Get trend sparkline
get_trend() {
    if [[ ! -f "$HISTORY_FILE" ]]; then
        echo "(no history)"
        return
    fi

    local rates=()
    while IFS= read -r line; do
        rates+=("$(echo "$line" | jq -r '.rate')")
    done < "$HISTORY_FILE"

    if [[ ${#rates[@]} -lt 1 ]]; then
        echo "(no data)"
        return
    fi

    # Sparkline characters
    local sparks=("▁" "▂" "▃" "▄" "▅" "▆" "▇" "█")
    local min=100 max=0

    for r in "${rates[@]}"; do
        (( $(echo "$r < $min" | bc -l) )) && min="$r"
        (( $(echo "$r > $max" | bc -l) )) && max="$r"
    done

    local spark=""
    local range
    range=$(echo "$max - $min" | bc)
    [[ $(echo "$range == 0" | bc -l) -eq 1 ]] && range=1

    for r in "${rates[@]}"; do
        local idx
        idx=$(echo "scale=0; ($r - $min) * 7 / $range" | bc)
        [[ "$idx" -gt 7 ]] && idx=7
        [[ "$idx" -lt 0 ]] && idx=0
        spark+="${sparks[$idx]}"
    done

    echo "$spark"
}

# Get depyler version
get_version() {
    if command -v depyler &>/dev/null; then
        depyler --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown"
    else
        echo "not installed"
    fi
}

# Main
main() {
    if [[ ! -f "$CORPUS_FILE" ]]; then
        echo "Error: Corpus not found. Run 'make corpus-label' first." >&2
        exit 1
    fi

    local metrics trend version
    metrics=$(get_metrics)
    trend=$(get_trend)
    version=$(get_version)

    local total success rate
    total=$(echo "$metrics" | jq -r '.total')
    success=$(echo "$metrics" | jq -r '.success')
    rate=$(echo "$metrics" | jq -r '.rate')

    local low med high
    low=$(echo "$metrics" | jq -r '.risk.LOW_RISK // 0')
    med=$(echo "$metrics" | jq -r '.risk.MEDIUM_RISK // 0')
    high=$(echo "$metrics" | jq -r '.risk.HIGH_RISK // 0')

    # Build top failures string
    local failures=""
    while IFS='=' read -r cat count; do
        [[ -n "$cat" ]] && failures+="$cat($count) "
    done < <(echo "$metrics" | jq -r '.top_failures | to_entries | .[:4] | .[] | "\(.key)=\(.value)"')

    # Display dashboard
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║           DEPYLER CORPUS DASHBOARD                   ║"
    echo "╠══════════════════════════════════════════════════════╣"
    printf "║ Success Rate: %5.1f%% (%d/%d)    Trend: %-8s    ║\n" "$rate" "$success" "$total" "$trend"
    printf "║ Depyler: %-20s                        ║\n" "$version"
    echo "╠══════════════════════════════════════════════════════╣"
    echo "║ Risk Distribution:                                   ║"
    printf "║   LOW: %-4d   MEDIUM: %-4d   HIGH: %-4d              ║\n" "$low" "$med" "$high"
    echo "╠══════════════════════════════════════════════════════╣"
    echo "║ Top Failures:                                        ║"
    printf "║   %-50s ║\n" "${failures:0:50}"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
}

main
