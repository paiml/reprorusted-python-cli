#!/usr/bin/env bash
# Rust Compilation Verification (GH-17)
#
# Verifies that transpiled Rust code compiles with cargo check/clippy.
#
# Usage:
#   ./scripts/verify_rust_compilation.sh [OPTIONS]
#
# Options:
#   -h, --help      Show this help message
#   -j, --json      Output results as JSON
#   -d, --dry-run   Show what would be checked without running cargo
#   -c, --clippy    Also run clippy for idiomatic Rust checks
#   -v, --verbose   Show detailed output for each example

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EXAMPLES_DIR="$PROJECT_ROOT/examples"

# Options
JSON_OUTPUT=false
DRY_RUN=false
RUN_CLIPPY=false
VERBOSE=false

# Results
TOTAL=0
COMPILED=0
CLIPPY_CLEAN=0
FAILED_EXAMPLES=()

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Verify that transpiled Rust code compiles successfully.

Options:
  -h, --help      Show this help message
  -j, --json      Output results as JSON
  -d, --dry-run   Show what would be checked without running cargo
  -c, --clippy    Also run clippy for idiomatic Rust checks
  -v, --verbose   Show detailed output for each example

Examples:
  $(basename "$0")              # Check all examples
  $(basename "$0") --json       # Output JSON report
  $(basename "$0") --clippy     # Include clippy checks
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
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -c|--clippy)
            RUN_CLIPPY=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

# Check for cargo
if ! command -v cargo &>/dev/null && [ "$DRY_RUN" = false ]; then
    echo "Error: cargo not found. Please install Rust." >&2
    exit 1
fi

# Find examples with Cargo.toml
find_rust_examples() {
    find "$EXAMPLES_DIR" -name "Cargo.toml" -type f 2>/dev/null | \
        xargs -I {} dirname {} | \
        sort -u
}

# Check single example
check_example() {
    local example_dir="$1"
    local name
    name=$(basename "$example_dir")

    if [ "$DRY_RUN" = true ]; then
        echo "Would check: $name"
        return 0
    fi

    local compile_ok=false
    local clippy_ok=false

    # Run cargo check
    if cargo check --manifest-path "$example_dir/Cargo.toml" 2>/dev/null; then
        compile_ok=true
    fi

    # Run clippy if requested
    if [ "$RUN_CLIPPY" = true ] && [ "$compile_ok" = true ]; then
        if cargo clippy --manifest-path "$example_dir/Cargo.toml" -- -D warnings 2>/dev/null; then
            clippy_ok=true
        fi
    fi

    # Report results
    if [ "$VERBOSE" = true ]; then
        if [ "$compile_ok" = true ]; then
            printf '\033[0;32m✓\033[0m %s\n' "$name"
        else
            printf '\033[0;31m✗\033[0m %s\n' "$name"
        fi
    fi

    if [ "$compile_ok" = true ]; then
        COMPILED=$((COMPILED + 1))
        if [ "$RUN_CLIPPY" = true ] && [ "$clippy_ok" = true ]; then
            CLIPPY_CLEAN=$((CLIPPY_CLEAN + 1))
        fi
        return 0
    else
        FAILED_EXAMPLES+=("$name")
        return 1
    fi
}

# Output JSON report
output_json() {
    local success_rate=0
    local clippy_rate=0

    if [ "$TOTAL" -gt 0 ]; then
        success_rate=$(echo "scale=1; $COMPILED * 100 / $TOTAL" | bc)
        if [ "$RUN_CLIPPY" = true ]; then
            clippy_rate=$(echo "scale=1; $CLIPPY_CLEAN * 100 / $TOTAL" | bc)
        fi
    fi

    local failed_json="[]"
    if [[ ${#FAILED_EXAMPLES[@]} -gt 0 ]]; then
        failed_json=$(printf '%s\n' "${FAILED_EXAMPLES[@]}" | jq -R . | jq -s .)
    fi

    jq -n \
        --argjson total "$TOTAL" \
        --argjson compiled "$COMPILED" \
        --argjson clippy_clean "$CLIPPY_CLEAN" \
        --argjson success_rate "$success_rate" \
        --argjson clippy_rate "$clippy_rate" \
        --argjson failed "$failed_json" \
        --arg run_clippy "$RUN_CLIPPY" \
        '{
            total_examples: $total,
            compiled_successfully: $compiled,
            clippy_clean: $clippy_clean,
            success_rate_percent: $success_rate,
            clippy_rate_percent: $clippy_rate,
            run_clippy: ($run_clippy == "true"),
            failed_examples: $failed
        }'
}

# Output human-readable report
output_report() {
    local success_rate=0

    if [ "$TOTAL" -gt 0 ]; then
        success_rate=$(echo "scale=1; $COMPILED * 100 / $TOTAL" | bc)
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "RUST COMPILATION VERIFICATION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "Total examples with Rust: %d\n" "$TOTAL"
    printf "Compiles successfully: %d (%.1f%%)\n" "$COMPILED" "$success_rate"

    if [ "$RUN_CLIPPY" = true ] && [ "$TOTAL" -gt 0 ]; then
        local clippy_rate
        clippy_rate=$(echo "scale=1; $CLIPPY_CLEAN * 100 / $TOTAL" | bc)
        printf "Clippy clean: %d (%.1f%%)\n" "$CLIPPY_CLEAN" "$clippy_rate"
    fi

    if [[ ${#FAILED_EXAMPLES[@]} -gt 0 ]]; then
        echo ""
        printf '\033[0;31m❌ Compilation failures:\033[0m\n'
        for ex in "${FAILED_EXAMPLES[@]}"; do
            echo "   - $ex"
        done
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main
main() {
    if [ "$DRY_RUN" = true ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "DRY RUN - Rust Compilation Verification"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi

    local examples
    mapfile -t examples < <(find_rust_examples)
    TOTAL=${#examples[@]}

    if [ "$DRY_RUN" = true ]; then
        echo "Total examples with Cargo.toml: $TOTAL"
        echo ""
        for ex in "${examples[@]}"; do
            check_example "$ex" || true
        done
        echo ""
        echo "Would report success percentage after checking."
        exit 0
    fi

    if [ "$TOTAL" -eq 0 ]; then
        if [ "$JSON_OUTPUT" = true ]; then
            echo '{"total_examples": 0, "compiled_successfully": 0, "success_rate_percent": 0}'
        else
            echo "No Rust examples found in $EXAMPLES_DIR"
        fi
        exit 0
    fi

    # Check each example
    for example in "${examples[@]}"; do
        check_example "$example" || true
    done

    # Output results
    if [ "$JSON_OUTPUT" = true ]; then
        output_json
    else
        output_report
    fi

    # Exit with error if any failures
    if [[ ${#FAILED_EXAMPLES[@]} -gt 0 ]]; then
        exit 1
    fi
}

main
