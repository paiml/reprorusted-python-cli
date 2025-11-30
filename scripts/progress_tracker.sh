#!/usr/bin/env bash
# Progress Tracking (GH-19)
#
# Track corpus success rate over time.
#
# Usage:
#   ./scripts/progress_tracker.sh [OPTIONS]
#
# Options:
#   -h, --help      Show this help message
#   -r, --record    Record current metrics
#   --history       Show progress history
#   --sparkline     Show trend as sparkline

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HISTORY_FILE="$PROJECT_ROOT/data/progress_history.jsonl"
CORPUS_FILE="$PROJECT_ROOT/data/labeled_corpus.parquet"

# Sparkline characters (sorted by height)
SPARKS=("▁" "▂" "▃" "▄" "▅" "▆" "▇" "█")

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Track corpus success rate over time.

Options:
  -h, --help      Show this help message
  -r, --record    Record current metrics to history
  --history       Show progress history table
  --sparkline     Show trend as sparkline

Data Storage:
  Progress is stored in: data/progress_history.jsonl
  One JSON record per measurement with timestamp and depyler version.

Examples:
  $(basename "$0") --record      # Record current metrics
  $(basename "$0") --history     # Show history table
EOF
}

# Get current metrics from corpus
get_current_metrics() {
    if [[ ! -f "$CORPUS_FILE" ]]; then
        echo "Error: Corpus file not found: $CORPUS_FILE" >&2
        exit 1
    fi

    uv run python3 -c "
import pyarrow.parquet as pq
import json
df = pq.read_table('$CORPUS_FILE').to_pandas()
total = len(df)
success = df['has_rust'].sum()
rate = round(success * 100 / total, 1) if total > 0 else 0
print(json.dumps({'total': int(total), 'success': int(success), 'rate': float(rate)}))
"
}

# Get depyler version
get_depyler_version() {
    if command -v depyler &>/dev/null; then
        depyler --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown"
    else
        echo "unknown"
    fi
}

# Record current metrics
record_metrics() {
    local metrics
    metrics=$(get_current_metrics)
    local version
    version=$(get_depyler_version)
    local timestamp
    timestamp=$(date -Iseconds)

    # Create data dir if needed
    mkdir -p "$(dirname "$HISTORY_FILE")"

    # Append to JSONL
    local record
    record=$(echo "$metrics" | jq -c ". + {\"timestamp\": \"$timestamp\", \"depyler_version\": \"$version\"}")
    echo "$record" >> "$HISTORY_FILE"

    local rate
    rate=$(echo "$metrics" | jq -r '.rate')
    echo "Recorded: ${rate}% success (depyler $version)"
}

# Show history table
show_history() {
    if [[ ! -f "$HISTORY_FILE" ]]; then
        echo "No history yet. Run with --record to start tracking."
        exit 0
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "CORPUS PROGRESS HISTORY"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "%-12s %-12s %-10s %-10s\n" "Date" "Version" "Success" "Change"

    local prev_rate=0
    while IFS= read -r line; do
        local date version rate change
        date=$(echo "$line" | jq -r '.timestamp' | cut -dT -f1)
        version=$(echo "$line" | jq -r '.depyler_version')
        rate=$(echo "$line" | jq -r '.rate')

        if [[ "$prev_rate" != "0" ]]; then
            local delta
            delta=$(echo "$rate - $prev_rate" | bc)
            if (( $(echo "$delta > 0" | bc -l) )); then
                change="+${delta}%"
            else
                change="${delta}%"
            fi
        else
            change="-"
        fi

        printf "%-12s %-12s %-10s %-10s\n" "$date" "$version" "${rate}%" "$change"
        prev_rate="$rate"
    done < "$HISTORY_FILE"

    # Show trend sparkline
    echo ""
    show_sparkline
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Show sparkline trend
show_sparkline() {
    if [[ ! -f "$HISTORY_FILE" ]]; then
        echo "Trend: (no data)"
        return
    fi

    local rates=()
    while IFS= read -r line; do
        rates+=("$(echo "$line" | jq -r '.rate')")
    done < "$HISTORY_FILE"

    if [[ ${#rates[@]} -lt 2 ]]; then
        echo "Trend: (need more data)"
        return
    fi

    # Find min/max for scaling
    local min=100 max=0
    for r in "${rates[@]}"; do
        (( $(echo "$r < $min" | bc -l) )) && min="$r"
        (( $(echo "$r > $max" | bc -l) )) && max="$r"
    done

    # Generate sparkline
    local spark=""
    local range
    range=$(echo "$max - $min" | bc)
    if (( $(echo "$range == 0" | bc -l) )); then
        range=1
    fi

    for r in "${rates[@]}"; do
        local idx
        idx=$(echo "scale=0; ($r - $min) * 7 / $range" | bc)
        [[ "$idx" -gt 7 ]] && idx=7
        [[ "$idx" -lt 0 ]] && idx=0
        spark+="${SPARKS[$idx]}"
    done

    # Determine trend direction
    local first="${rates[0]}"
    local last="${rates[-1]}"
    local trend_word
    if (( $(echo "$last > $first" | bc -l) )); then
        trend_word="(improving)"
    elif (( $(echo "$last < $first" | bc -l) )); then
        trend_word="(declining)"
    else
        trend_word="(stable)"
    fi

    echo "Trend: $spark $trend_word"
}

# Main
main() {
    if [[ $# -eq 0 ]]; then
        show_history
        exit 0
    fi

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -r|--record)
                record_metrics
                exit 0
                ;;
            --history)
                show_history
                exit 0
                ;;
            --sparkline)
                show_sparkline
                exit 0
                ;;
            *)
                echo "Unknown option: $1" >&2
                usage >&2
                exit 1
                ;;
        esac
    done
}

main "$@"
