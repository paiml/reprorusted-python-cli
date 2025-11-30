#!/usr/bin/env bash
# Rust Compilation Error Analysis (GH-18)
#
# Categorizes Rust compilation errors to help prioritize fixes.
#
# Usage:
#   ./scripts/analyze_rust_errors.sh [OPTIONS]
#
# Options:
#   -h, --help      Show this help message
#   -j, --json      Output results as JSON
#   -s, --summary   Show summary only (no per-example details)
#   --stdin         Read cargo output from stdin instead of running cargo

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EXAMPLES_DIR="$PROJECT_ROOT/examples"

# Options
JSON_OUTPUT=false
SUMMARY_ONLY=false
READ_STDIN=false

# Error categories with descriptions
declare -A ERROR_DESCRIPTIONS=(
    ["E0432"]="unresolved import"
    ["E0599"]="no method named"
    ["E0425"]="cannot find value"
    ["E0308"]="mismatched types"
    ["E0277"]="trait not satisfied"
    ["E0412"]="cannot find type"
    ["E0433"]="failed to resolve"
    ["E0382"]="use of moved value"
    ["E0507"]="cannot move out"
    ["E0015"]="calls in constants"
)

# Counters
declare -A ERROR_COUNTS
declare -A EXAMPLE_ERRORS
TOTAL_ERRORS=0

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Analyze and categorize Rust compilation errors.

Options:
  -h, --help      Show this help message
  -j, --json      Output results as JSON
  -s, --summary   Show summary count by category
  --stdin         Read cargo output from stdin

Error Categories:
  E0432  Unresolved import (missing crate/module)
  E0599  No method named (trait not implemented)
  E0425  Cannot find value (undefined variable)
  E0308  Mismatched types
  E0277  Trait not satisfied

Examples:
  $(basename "$0")              # Analyze all examples
  $(basename "$0") --summary    # Show category summary
  cargo check 2>&1 | $(basename "$0") --stdin
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -j|--json)
            JSON_OUTPUT=true
            shift
            ;;
        -s|--summary)
            SUMMARY_ONLY=true
            shift
            ;;
        --stdin)
            READ_STDIN=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

# Parse error line and extract code
parse_error() {
    local line="$1"
    local code=""

    # Match error[E0XXX] pattern
    if [[ $line =~ error\[E([0-9]{4})\] ]]; then
        code="E${BASH_REMATCH[1]}"
    fi

    echo "$code"
}

# Process cargo output
process_output() {
    local input="$1"
    local current_example=""

    while IFS= read -r line; do
        # Extract error code
        local code
        code=$(parse_error "$line")

        if [[ -n "$code" ]]; then
            TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
            ERROR_COUNTS[$code]=$((${ERROR_COUNTS[$code]:-0} + 1))

            # Track per-example if we can determine it
            if [[ $line =~ examples/([^/]+)/ ]]; then
                current_example="${BASH_REMATCH[1]}"
                EXAMPLE_ERRORS[$current_example]=$((${EXAMPLE_ERRORS[$current_example]:-0} + 1))
            fi
        fi
    done <<< "$input"
}

# Collect errors from all examples
collect_errors() {
    local all_output=""

    for cargo_toml in "$EXAMPLES_DIR"/example_*/Cargo.toml; do
        if [[ -f "$cargo_toml" ]]; then
            local example_dir
            example_dir=$(dirname "$cargo_toml")
            local output
            output=$(cargo check --manifest-path "$cargo_toml" 2>&1 || true)
            all_output+="$output"$'\n'
        fi
    done

    echo "$all_output"
}

# Output JSON
output_json() {
    local categories="{"
    local first=true

    for code in "${!ERROR_COUNTS[@]}"; do
        if [[ "$first" != true ]]; then
            categories+=","
        fi
        first=false
        local desc="${ERROR_DESCRIPTIONS[$code]:-unknown}"
        categories+="\"$code\":{\"count\":${ERROR_COUNTS[$code]},\"description\":\"$desc\"}"
    done
    categories+="}"

    local examples="{"
    first=true
    for ex in "${!EXAMPLE_ERRORS[@]}"; do
        if [[ "$first" != true ]]; then
            examples+=","
        fi
        first=false
        examples+="\"$ex\":${EXAMPLE_ERRORS[$ex]}"
    done
    examples+="}"

    cat <<EOF
{
  "total_errors": $TOTAL_ERRORS,
  "by_category": $categories,
  "by_example": $examples
}
EOF
}

# Output human-readable report
output_report() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "RUST COMPILATION ERROR ANALYSIS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "Total errors: %d\n" "$TOTAL_ERRORS"
    echo ""

    if [[ $TOTAL_ERRORS -gt 0 ]]; then
        echo "By Category:"
        # Sort by count descending
        for code in $(for k in "${!ERROR_COUNTS[@]}"; do echo "$k ${ERROR_COUNTS[$k]}"; done | sort -k2 -rn | cut -d' ' -f1); do
            local count=${ERROR_COUNTS[$code]}
            local pct
            pct=$(echo "scale=1; $count * 100 / $TOTAL_ERRORS" | bc)
            local desc="${ERROR_DESCRIPTIONS[$code]:-unknown}"
            printf "  %s (%s): %d (%.1f%%)\n" "$code" "$desc" "$count" "$pct"
        done

        if [[ "$SUMMARY_ONLY" != true ]] && [[ ${#EXAMPLE_ERRORS[@]} -gt 0 ]]; then
            echo ""
            echo "Top affected examples:"
            for ex in $(for k in "${!EXAMPLE_ERRORS[@]}"; do echo "$k ${EXAMPLE_ERRORS[$k]}"; done | sort -k2 -rn | head -5 | cut -d' ' -f1); do
                printf "  - %s: %d errors\n" "$ex" "${EXAMPLE_ERRORS[$ex]}"
            done
        fi
    else
        echo "No compilation errors found!"
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main
main() {
    local cargo_output=""

    if [[ "$READ_STDIN" == true ]]; then
        cargo_output=$(cat)
    else
        echo "Collecting errors from examples..." >&2
        cargo_output=$(collect_errors)
    fi

    process_output "$cargo_output"

    if [[ "$JSON_OUTPUT" == true ]]; then
        output_json
    else
        output_report
    fi
}

main
