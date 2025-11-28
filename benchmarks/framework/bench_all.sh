#!/usr/bin/env bash
# Benchmark all examples and generate comparison report

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BENCH_RUNNER="$SCRIPT_DIR/bench_runner.sh"
RESULTS_DIR="$PROJECT_ROOT/benchmarks/reports"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*"
}

main() {
    log_info "Benchmarking all examples..."
    echo ""

    mkdir -p "$RESULTS_DIR"

    local success_count=0
    local total_count=0

    # Find all example directories
    for example_dir in "$PROJECT_ROOT"/examples/example_*/; do
        if [[ -d "$example_dir" ]]; then
            total_count="$((total_count + 1)")
            example_name="$(basename "$example_dir")"

            echo "═══════════════════════════════════════════════════════════"
            echo " Benchmarking: $example_name"
            echo "═══════════════════════════════════════════════════════════"
            echo ""

            if "$BENCH_RUNNER" "$example_dir"; then
                success_count="$((success_count + 1)")
            fi

            echo ""
        fi
    done

    echo "═══════════════════════════════════════════════════════════"
    log_success "Completed $success_count/$total_count benchmarks"
    log_info "Results directory: $RESULTS_DIR"
    echo ""

    # Generate summary report if jq is available
    if command -v jq >/dev/null 2>&1; then
        log_info "Generating summary report..."
        generate_summary_report
    fi
}

generate_summary_report() {
    local summary_file="$RESULTS_DIR/summary.txt"

    {
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  Benchmark Summary Report"
        echo "  Generated: "$(date)""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""

        for json_file in "$RESULTS_DIR"/*-bench.json; do
            if [[ -f "$json_file" ]]; then
                local example_name
                example_name="$(basename "$json_file" -bench.json)"

                echo "╔═══════════════════════════════════════════════════════╗"
                echo "║  $example_name"
                echo "╚═══════════════════════════════════════════════════════╝"
                echo ""

                jq -r '
                    .benchmarks[] |
                    "  Implementation: \(.name)\n" +
                    "    Mean time:    \(.mean_ms) ms\n" +
                    "    Std dev:      \(.std_dev_ms) ms\n" +
                    (if .memory_kb then "    Peak memory:  \(.memory_kb) KB\n" else "" end) +
                    ""
                ' "$json_file" 2>/dev/null || echo "  (parsing error)"

                # Calculate speedup if both Python and Rust are present
                local python_time rust_time
                python_time="$(jq -r '.benchmarks[] | select(.name | contains("python")") | .mean_ms' "$json_file" 2>/dev/null || echo "")
                rust_time="$(jq -r '.benchmarks[] | select(.name | contains("rust")") | .mean_ms' "$json_file" 2>/dev/null || echo "")

                if [[ -n "$python_time" ]] && [[ -n "$rust_time" ]]; then
                    local speedup
                    speedup="$(awk "BEGIN {printf \"%.2f\", $python_time / $rust_time}")"
                    echo "  📊 Speedup: ${speedup}x faster (Rust vs Python)"
                    echo ""
                fi
            fi
        done

        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    } > "$summary_file"

    cat "$summary_file"
    log_success "Summary saved to: $summary_file"
}

main "$@"
