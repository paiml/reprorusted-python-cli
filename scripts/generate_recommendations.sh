#!/usr/bin/env bash
# Fix Recommendations Generator (GH-20)
#
# Analyzes failures and generates prioritized recommendations.
#
# Usage:
#   ./scripts/generate_recommendations.sh [OPTIONS]
#
# Options:
#   -h, --help      Show this help message
#   -t, --top N     Show top N recommendations (default: 10)
#   -j, --json      Output as JSON

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CORPUS_FILE="$PROJECT_ROOT/data/labeled_corpus.parquet"

TOP_N=10
JSON_OUTPUT=false

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Analyze failures and generate prioritized fix recommendations.

Options:
  -h, --help      Show this help message
  -t, --top N     Show top N recommendations (default: 10)
  -j, --json      Output as JSON

Priority Levels:
  HIGH   - Affects 5+ files, high impact improvement
  MED    - Affects 3-4 files, medium impact
  LOW    - Affects 1-2 files, lower priority

Output includes estimated percent improvement per fix.

Examples:
  $(basename "$0")           # Show top 10 recommendations
  $(basename "$0") --top 5   # Show top 5
  $(basename "$0") --json    # Output as JSON
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -t|--top)
            TOP_N="$2"
            shift 2
            ;;
        -j|--json)
            JSON_OUTPUT=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

# Pattern descriptions for common failure categories
declare -A PATTERN_DESC=(
    ["async"]="async/await patterns"
    ["time"]="time.time() and time module"
    ["heapq"]="heapq operations"
    ["base64"]="base64 encoding/decoding"
    ["calendar"]="calendar operations"
    ["functools"]="functools (partial, curry)"
    ["threading"]="threading primitives"
    ["queue"]="queue operations"
    ["socket"]="socket operations"
    ["subprocess"]="subprocess calls"
)

# Analyze corpus and generate recommendations
analyze_corpus() {
    uv run python3 << 'PYTHON'
import json
import sys
from collections import defaultdict
import pyarrow.parquet as pq

# Load corpus
df = pq.read_table("data/labeled_corpus.parquet").to_pandas()
total = len(df)
failing = df[~df["has_rust"]]
failing_count = len(failing)

if failing_count == 0:
    print(json.dumps({"recommendations": [], "total": total, "failing": 0}))
    sys.exit(0)

# Group by category
category_counts = failing["category"].value_counts().to_dict()

# Build recommendations
recommendations = []
for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
    impact = round(count * 100 / total, 1)

    # Determine priority
    if count >= 5:
        priority = "HIGH"
    elif count >= 3:
        priority = "MED"
    else:
        priority = "LOW"

    # Infer pattern from category name
    pattern = cat.replace("_", " ")

    recommendations.append({
        "category": cat,
        "count": count,
        "priority": priority,
        "impact": impact,
        "pattern": pattern
    })

output = {
    "recommendations": recommendations,
    "total": total,
    "failing": failing_count,
    "success_rate": round((total - failing_count) * 100 / total, 1)
}

print(json.dumps(output))
PYTHON
}

# Output human-readable report
output_report() {
    local data="$1"
    local total failing success_rate
    total=$(echo "$data" | jq -r '.total')
    failing=$(echo "$data" | jq -r '.failing')
    success_rate=$(echo "$data" | jq -r '.success_rate')

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "DEPYLER FIX RECOMMENDATIONS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "Current: %s%% success (%d/%d files)\n" "$success_rate" "$((total - failing))" "$total"
    printf "Failing: %d files\n" "$failing"
    echo ""

    if [[ "$failing" -eq 0 ]]; then
        echo "🎉 No failures - all files transpile successfully!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        return
    fi

    echo "Top Recommendations:"
    echo ""

    local i=1
    echo "$data" | jq -r ".recommendations[:$TOP_N][] | \"\(.priority)|\(.count)|\(.impact)|\(.category)|\(.pattern)\"" | \
    while IFS='|' read -r priority count impact category pattern; do
        local icon
        case "$priority" in
            HIGH) icon="🔴" ;;
            MED)  icon="🟡" ;;
            LOW)  icon="🟢" ;;
        esac

        printf "%2d. %s [%s] %s (%d files)\n" "$i" "$icon" "$priority" "$pattern" "$count"
        printf "    Impact: +%.1f%% success rate\n" "$impact"
        echo ""
        i=$((i + 1))
    done

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main
main() {
    if [[ ! -f "$CORPUS_FILE" ]]; then
        echo "Error: Corpus not found. Run 'make corpus-label' first." >&2
        exit 1
    fi

    local data
    data=$(analyze_corpus)

    if [[ "$JSON_OUTPUT" == true ]]; then
        echo "$data" | jq .
    else
        output_report "$data"
    fi
}

main
